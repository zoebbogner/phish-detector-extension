import os
import csv
import zlib
import gzip
import requests
from io import BytesIO
from warcio.archiveiterator import ArchiveIterator
from utils.fetch.config import COMMON_CRAWL_S3_PATHS, OUTPUT_CSV_GZ
from main_config import GOOGLE_API_KEY



def label_url_google_safe_browsing(url: str) -> int:
    """Query Google Safe Browsing API for a URL and return 1 if flagged, else 0."""
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_API_KEY}"
    body = {
        "client": {"clientId": "your-company", "clientVersion": "1.5.2"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        response = requests.post(api_url, json=body, timeout=3)
        response.raise_for_status()
        if response.json().get("matches"):
            return 1
    except requests.RequestException:
        pass
    return 0


def process_warc_file(url: str, max_pages: int = 100):
    """Download and process a Common Crawl WARC file."""
    print(f"[INFO] Downloading and processing: {url}")
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        stream = BytesIO(resp.raw.read())
    except Exception as e:
        print(f"[ERROR] Failed to fetch WARC: {e}")
        return []

    samples = []
    for record in ArchiveIterator(stream):
        if record.rec_type != "response":
            continue
        target_url = record.rec_headers.get_header("WARC-Target-URI")
        try:
            raw_bytes = record.content_stream().read()
            html = raw_bytes.decode("utf-8", errors="ignore")
            compressed_html = zlib.compress(html.encode("utf-8"))
            label = label_url_google_safe_browsing(target_url)
            samples.append((target_url, compressed_html, label))
            print(f"[INFO] Collected {target_url} - Label: {label}")
        except Exception as e:
            print(f"[WARN] Skipping {target_url} due to: {e}")
        if len(samples) >= max_pages:
            break
    return samples


def write_compressed_csv(data: list, output_path: str):
    """Write list of (url, compressed_html, label) to a .csv.gz file."""
    with gzip.open(output_path, "wt", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "compressed_html", "label"])
        for url, html, label in data:
            writer.writerow([url, zlib.compress(html).hex(), label])  # convert to hex string for CSV

    print(f"[INFO] Wrote {len(data)} samples to {output_path}")


def main():
    os.makedirs(os.path.dirname(OUTPUT_CSV_GZ), exist_ok=True)

    total_data = []
    for warc_url in COMMON_CRAWL_S3_PATHS:
        data = process_warc_file(warc_url, max_pages=100)  # Adjust limit if needed
        total_data.extend(data)
    write_compressed_csv(total_data, OUTPUT_CSV_GZ)


if __name__ == "__main__":
    main()