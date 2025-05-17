import zipfile
from pathlib import Path
from typing import Generator, List, Dict
import mysql.connector


def get_metadata_for_files(
    filenames: List[str],
    host: str,
    user: str,
    password: str,
    database: str,
) -> Dict[str, dict]:
    """
    Retrieves metadata only for the given filenames from MySQL.
    Returns a mapping from filename to metadata dict.
    """
    conn = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = conn.cursor()

    format_strings = ",".join(["%s"] * len(filenames))
    query = f"SELECT website, url, result FROM `index` WHERE website IN ({format_strings})"
    cursor.execute(query, filenames)

    rows = cursor.fetchall()
    print(f"[INFO] Fetched {len(rows)} rows")
    cursor.close()
    conn.close()

    meta_map = {
        row[0]: {"url": row[1], "label": int(row[2])}
        for row in rows
    }

    return meta_map


def load_html_dataset_by_zip(
    zip_dir: str,
    sql_host="localhost",
    sql_user="root",
    sql_password="",
    sql_database="phish_data",
) -> Generator[List[dict], None, None]:
    """
    Yields batches of {"url", "html", "label"} one per ZIP file.
    Only files that exist in the MySQL metadata table are included.

    Args:
        zip_dir: Directory containing dataset_part_*.zip
        sql_host/sql_user/sql_password/sql_database: MySQL credentials
    """
    skipped = 0
    zip_paths = sorted(Path(zip_dir).glob("dataset_part_*.zip"))
    print(f"[INFO] Found {len(zip_paths)} zip files.")

    for zip_path in zip_paths:
        print(f"[INFO] Processing {zip_path.name}")
        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                html_files = [f for f in zipf.namelist() if f.endswith(".html")]
                basenames = [Path(f).name for f in html_files]
                print(f"[INFO] Found {len(basenames)} html files.")
                
                metadata_map = get_metadata_for_files(
                    basenames,
                    host=sql_host,
                    user=sql_user,
                    password=sql_password,
                    database=sql_database,
                )

                batch = []
                for html_path in html_files:
                    basename = Path(html_path).name
                    if basename not in metadata_map:
                        skipped += 1
                        continue
                    try:
                        html = zipf.read(html_path).decode("utf-8", errors="ignore")
                        batch.append({
                            "url": metadata_map[basename]["url"],
                            "html": html,
                            "label": metadata_map[basename]["label"]
                        })
                    except (KeyError, UnicodeDecodeError, OSError, zipfile.BadZipFile) as e:
                        print(f"[WARN] Failed to read {basename}: {e}")

                if batch:
                    print(f"[INFO] Yielding {len(batch)} entries from {zip_path.name}")
                    print(f"[INFO] Skipped {skipped} entries")
                    yield batch

        except zipfile.BadZipFile as e:
            print(f"[ERROR] Corrupt zip file {zip_path}: {e}")