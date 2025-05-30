import csv
import os

def copy_csv(source_path: str, target_path: str):
    """
    Copy rows from source_path into target_path, appending only new rows
    and verifying that both files share the same header.
    """
    # Read source header and all rows once
    with open(source_path, newline='', encoding='utf-8') as src_f:
        reader = csv.DictReader(src_f)
        source_header = reader.fieldnames
        source_rows = list(reader)

    # If target exists, read its header; else create it with the source header
    if os.path.exists(target_path):
        with open(target_path, newline='', encoding='utf-8') as tgt_read_f:
            tgt_reader = csv.DictReader(tgt_read_f)
            target_header = tgt_reader.fieldnames
            if target_header != source_header:
                raise ValueError(f"Header mismatch:\n  source: {source_header}\n  target: {target_header}")
            # Build a set of URLs (or whatever unique key) already in the target
            seen = {row['url'] for row in tgt_reader if 'url' in row}
    else:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        # Write header out
        with open(target_path, 'w', newline='', encoding='utf-8') as tgt_write_f:
            writer = csv.DictWriter(tgt_write_f, fieldnames=source_header)
            writer.writeheader()
        seen = set()

    # Append only new rows
    with open(target_path, 'a', newline='', encoding='utf-8') as tgt_append_f:
        writer = csv.DictWriter(tgt_append_f, fieldnames=source_header)
        for row in source_rows:
            key = row.get('url')
            if key is None:
                raise KeyError("Source CSV missing a 'url' column")
            if key in seen:
                continue
            writer.writerow(row)
            seen.add(key)
            
all_urls = "data/raw/all_urls.csv"
target = "phishing_crawler/seeds.csv"

copy_csv(all_urls, target)