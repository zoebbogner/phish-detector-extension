#!/usr/bin/env python3
import os
import csv
import json
import threading
import asyncio
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uvicorn
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────
# 1. LOAD ENVIRONMENT VARIABLES (optional)
# ─────────────────────────────────────────────────────────────
# Uncomment if you want to override settings via a .env file:
# load_dotenv(env_file=".env")

FEATURES = [
    "html_tag_count",
    "form_count",
    "input_count",
    "anchor_count",
    "script_count",
    "iframe_count",
    "img_count",
    "meta_refresh_count",
    "title_length",
    "text_to_html_ratio",
    "document_text_entropy",
    "suspicious_keyword_count",
    "base64_asset_count",
    "data_uri_asset_count",
    "inline_style_count",
    "password_field_count",
    "hidden_redirect_element_count",
    "external_stylesheet_ratio",
    "non_https_resource_ratio",
    "domain_mismatch_link_ratio",
    "password_reset_link_count",
    "external_resource_count",
    "favicon_domain_mismatch",
    "redirect_pattern_count",
    "external_domain_count",
    "ad_network_asset_count",
]

# CSV will be written with columns = ["url"] + FEATURES + ["label"]
HEADER = ["url"] + FEATURES + ["label"]

# Path to the large CSV of URLs (we stream it line by line)
CSV_PATH = os.getenv("CSV_PATH", "all_urls.csv")

# State file which keeps track of (offset, served_count)
STATE_FILE = os.getenv("STATE_FILE", "controller_state.json")

# Where to append CSV results
RESULTS_FILE = os.getenv("RESULTS_FILE", "results.csv")

# HTTP host/port for the controller
HOST = os.getenv("CONTROLLER_HOST", "0.0.0.0")
PORT = int(os.getenv("CONTROLLER_PORT", 8000))

# Hand out one URL at a time
DEFAULT_BATCH_SIZE = int(os.getenv("DEFAULT_BATCH_SIZE", 1))
MAX_BATCH_SIZE     = int(os.getenv("MAX_BATCH_SIZE", 1))

# ─────────────────────────────────────────────────────────────
# 2. GLOBAL STATE & LOCKS
# ─────────────────────────────────────────────────────────────
queue_lock   = threading.Lock()  # protects file‐handle reads from all_urls.csv
results_lock = threading.Lock()  # protects appending to results.csv

file_handle: Optional[Any] = None
total_urls: int        = 0
served_count: int      = 0

# This will be our asyncio queue for POSTed payloads:
write_queue: asyncio.Queue = asyncio.Queue()

# ─────────────────────────────────────────────────────────────
# 3. FASTAPI APPLICATION & Pydantic MODELS
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Streaming Controller + Async Submit Queue (CSV)",
    version="1.0",
    description=(
        "1) Streams one URL at a time from a large CSV (no full‐file load),\n"
        "2) Accepts POSTed JSON feature‐objects from workers, enqueues them,\n"
        "   and writes them sequentially to a CSV file in the background."
    )
)

class UrlLabelPair(BaseModel):
    url: str
    label: int

class NextBatchResponse(BaseModel):
    # Now “urls” becomes a list of UrlLabelPair, not just strings
    urls:       List[UrlLabelPair]
    batch_size: int
    next_index: int
    total_urls: int
class StatusResponse(BaseModel):
    total_urls:    int
    served_urls:   int
    remaining_urls: int

class SubmitPayload(BaseModel):
    """
    Schema for each worker’s POST. All fields are required (no Optional).
    Count‐based features are typed as int; ratio/entropy features as float.
    """
    url: str

    html_tag_count:                     int
    form_count:                         int
    input_count:                        int
    anchor_count:                       int
    script_count:                       int
    iframe_count:                       int
    img_count:                          int
    meta_refresh_count:                 int
    title_length:                       int
    text_to_html_ratio:                 float
    document_text_entropy:              float
    suspicious_keyword_count:           int
    base64_asset_count:                 int
    data_uri_asset_count:               int
    inline_style_count:                 int
    password_field_count:               int
    hidden_redirect_element_count:      int
    external_stylesheet_ratio:          float
    non_https_resource_ratio:           float
    domain_mismatch_link_ratio:         float
    password_reset_link_count:          int
    external_resource_count:            int
    favicon_domain_mismatch:            int
    redirect_pattern_count:             int
    external_domain_count:              int
    ad_network_asset_count:             int
    label:                              int
# ─────────────────────────────────────────────────────────────
# 4. UTILITY: State‐File Load/Save & CSV Line Counting
# ─────────────────────────────────────────────────────────────
def load_state(state_path: str) -> (int, int):
    """
    Read JSON state file and return (offset, served_count).
    If missing or malformed, return (0, 0).
    """
    if not os.path.isfile(state_path):
        return 0, 0
    try:
        with open(state_path, "r") as sf:
            data = json.load(sf)
            offset = int(data.get("offset", 0))
            served = int(data.get("served", 0))
            return offset, served
    except Exception:
        return 0, 0

def save_state(state_path: str, offset: int, served: int):
    """
    Atomically write {"offset": offset, "served": served} to state file.
    """
    try:
        tmp_path = state_path + ".tmp"
        with open(tmp_path, "w") as sf:
            json.dump({"offset": offset, "served": served}, sf)
        os.replace(tmp_path, state_path)
    except Exception as e:
        print(f"WARNING: failed to write state file {state_path}: {e}")

def count_total_lines(csv_path: str) -> int:
    """
    Quickly count how many lines (URLs) are in the CSV on disk.
    Only holds one line in memory at a time.
    """
    count = 0
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count - 1

# ─────────────────────────────────────────────────────────────
# 5. STARTUP EVENT: Open CSV, Seek to Offset, Count Lines, Spawn Writer
# ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def setup_controller():
    global file_handle, total_urls, served_count, write_queue

    # 1) Make sure the CSV file actually exists
    if not os.path.isfile(CSV_PATH):
        raise RuntimeError(f"CSV file not found at '{CSV_PATH}'")

    # 2) Count how many lines in total (including header)
    total_urls = count_total_lines(CSV_PATH)

    # 3) Load saved offset/served_count
    offset, served = load_state(STATE_FILE)
    served_count = served if served <= total_urls else 0
    if offset < 0:
        offset = 0

    # 4) Open the CSV in text mode
    file_handle = open(CSV_PATH, "r", newline="", encoding="utf-8")

    # 5) If this is the very first time (served_count == 0), skip the header row now
    if served_count == 0:
        _ = file_handle.readline()    # read & discard the "url,label\n" header

    # 6) Otherwise, if served_count > 0, we assume the saved offset already points
    #    just after the header, so we simply seek to that offset:
    try:
        file_handle.seek(offset)
    except OSError:
        # If the offset is invalid, rewind and reset served_count
        file_handle.seek(0)
        served_count = 0

    print(f"▶ Controller started. total_urls={total_urls}, served_count={served_count}, offset={file_handle.tell()}")

    # 7) (Optionally) make sure results.csv has its header, then launch background_writer
    if not os.path.isfile(RESULTS_FILE) or os.path.getsize(RESULTS_FILE) == 0:
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as rf:
            writer = csv.DictWriter(rf, fieldnames=HEADER)
            writer.writeheader()

    asyncio.create_task(background_writer())
# ─────────────────────────────────────────────────────────────
# 6. BACKGROUND WRITER TASK (writes to CSV)
# ─────────────────────────────────────────────────────────────
async def background_writer():
    """
    Forever loop that pulls one SubmitPayload at a time from write_queue,
    then writes it as a CSV row under a lock (header already exists).
    """
    while True:
        payload: SubmitPayload = await write_queue.get()
        entry: Dict[str, Any] = payload.dict()

        # Build a row dict in the fixed order of HEADER:
        row = { key: entry.get(key, "") for key in HEADER }

        # Append the single data row under a lock
        with results_lock:
            with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as rf:
                writer = csv.DictWriter(rf, fieldnames=HEADER)
                writer.writerow(row)

        write_queue.task_done()

# ─────────────────────────────────────────────────────────────
# 7. CORE LOGIC: Fetch One URL from CSV
# ─────────────────────────────────────────────────────────────
def fetch_next_batch_from_file(batch_size: int) -> List[Dict[str, Any]]:
    """
    Under queue_lock, read up to batch_size lines from all_urls.csv.
    Each line has the format “url,label”. We skip blank lines.
    Returns a list of dictionaries, each: { "url": <str>, "label": <int> }.

    Also updates served_count and persists the new offset.
    """
    global served_count, file_handle, total_urls

    batch: List[Dict[str, Any]] = []
    with queue_lock:
        # If we’ve already served all data rows, return empty
        if served_count >= total_urls:
            return []

        for _ in range(batch_size):
            line = file_handle.readline()
            if not line:
                # Reached EOF
                break

            raw = line.strip()
            if raw == "":
                # Skip any blank lines
                continue

            # Assume “url,label” format; split into two parts at the first comma
            parts = raw.split(",", 1)
            if len(parts) != 2:
                # Malformed line (no comma); skip it
                continue

            url_part = parts[0].strip()
            label_part = parts[1].strip()

            if url_part == "" or label_part == "":
                # Either column is empty; skip
                continue

            try:
                label_int = int(label_part)
            except ValueError:
                # Label isn’t an integer; skip this line
                continue

            batch.append({"url": url_part, "label": label_int})

        # Update how many data rows we’ve handed out
        served_count += len(batch)

        # Persist new file‐offset
        new_offset = file_handle.tell()
        save_state(STATE_FILE, new_offset, served_count)

        return batch

# ─────────────────────────────────────────────────────────────
# 8. API ENDPOINT: GET /next?batch_size=1
# ─────────────────────────────────────────────────────────────
@app.get("/next", response_model=NextBatchResponse)
def next_batch(batch_size: Optional[int] = DEFAULT_BATCH_SIZE):
    """
    GET /next?batch_size=1
    Returns a JSON response with:
      - urls: a list of up to batch_size UrlLabelPair objects (each has 'url' and 'label')
      - batch_size: how many were returned
      - next_index: new served_count
      - total_urls: total data‐rows in the CSV
    """
    if batch_size < 1 or batch_size > MAX_BATCH_SIZE:
        raise HTTPException(status_code=400, detail="batch_size must be between 1 and {MAX_BATCH_SIZE}")

    # fetch_next_batch_from_file now returns List[{"url": str, "label": int}, ...]
    pairs = fetch_next_batch_from_file(batch_size)

    # Convert each dict into a UrlLabelPair object
    url_label_objects: List[UrlLabelPair] = [UrlLabelPair(**d) for d in pairs]

    served = min(served_count, total_urls)
    return NextBatchResponse(
        urls=url_label_objects,
        batch_size=len(url_label_objects),
        next_index=served,
        total_urls=total_urls
    )

# ─────────────────────────────────────────────────────────────
# 9. API ENDPOINT: GET /status
# ─────────────────────────────────────────────────────────────
@app.get("/status", response_model=StatusResponse)
def status():
    """
    GET /status
    Returns:
      - total_urls: how many URLs in CSV
      - served_urls: how many have already been handed out
      - remaining_urls: total_urls - served_urls
    """
    served = min(served_count, total_urls)
    return StatusResponse(
        total_urls=total_urls,
        served_urls=served,
        remaining_urls=total_urls - served
    )

# ─────────────────────────────────────────────────────────────
# 10. API ENDPOINT: POST /reset
# ─────────────────────────────────────────────────────────────
@app.post("/reset")
def reset_controller():
    """
    POST /reset
    Resets served_count → 0, offset → 0, seeks to file‐start, writes state.
    Optionally also truncate RESULTS_FILE if you want a fresh run.
    """
    global served_count, file_handle

    with queue_lock:
        served_count = 0
        try:
            file_handle.seek(0)
        except OSError:
            pass
        save_state(STATE_FILE, 0, 0)

    # Optionally, clear results CSV:
    # with results_lock:
    #     open(RESULTS_FILE, "w", newline="", encoding="utf-8").close()

    return {"status": "reset", "total_urls": total_urls}

# ─────────────────────────────────────────────────────────────
# 11. API ENDPOINT: POST /submit
# ─────────────────────────────────────────────────────────────
@app.post("/submit")
async def submit_result(request: Request):
    """
    POST /submit
    Expects a JSON body matching SubmitPayload. Instead of writing immediately,
    this handler simply does `await write_queue.put(validated)`. The background_writer
    task will eventually pull that SubmitPayload off the queue and append to RESULTS_FILE (CSV).

    If the queue is full or busy, this call will "await" until there's space,
    meaning pending requests wait in the queue.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    try:
        validated = SubmitPayload(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payload validation error: {e}")

    # Enqueue the Pydantic model itself
    await write_queue.put(validated)

    # Return immediately, not waiting for the actual disk‐write.
    return {"status": "queued", "queued_payload": validated.dict()}
# ─────────────────────────────────────────────────────────────
# 12. RUN THE APP (Uvicorn)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # --keep-alive 600 keeps connections alive for 10 minutes; adjust as needed
    uvicorn.run(
        "controller:app",
        host=HOST,
        port=PORT,
        reload=True,
        # keepalive=600  # uncomment if you want a long TCP keep-alive window
    )