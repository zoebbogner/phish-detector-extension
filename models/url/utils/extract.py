import os
import time
import pandas as pd
from models.url.utils.feature_extractor import URLFeatureExtractor
from models.url.config import FEATURES
from models.content.utils.load_from_db import load_html_dataset_by_zip
from dotenv import load_dotenv

URL_PROCESSED_PATH = "data/processed/url.csv"
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
ZIP_DIR = "/Users/zoe/Downloads/n96ncsr5g4-1/dataset"


def extract_url_features():
    """
    Extract URL features from a MySQL DB and write them to a CSV in batches.
    """
    print("[INFO] Starting URL feature extraction...")
    extractor = URLFeatureExtractor()
    batch_idx = 0
    first_write = True

    for batch in load_html_dataset_by_zip(
        zip_dir=ZIP_DIR,
        sql_host=MYSQL_HOST,
        sql_user=MYSQL_USER,
        sql_password=MYSQL_PASSWORD,
        sql_database=MYSQL_DATABASE,
    ):
        start_time = time.time()
        print(f"[INFO] Processing batch {batch_idx + 1} ({len(batch)} items)")

        urls = [entry["url"] for entry in batch if "url" in entry and "label" in entry]
        labels = [entry["label"] for entry in batch if "url" in entry and "label" in entry]

        features_df = extractor.transform(urls)
        features_df = features_df[FEATURES]
        features_df["label"] = labels

        os.makedirs(os.path.dirname(URL_PROCESSED_PATH), exist_ok=True)
        features_df.to_csv(
            URL_PROCESSED_PATH,
            mode="w" if first_write else "a",
            index=False,
            header=first_write
        )
        first_write = False
        end_time = time.time()
        print(f"[INFO] Time taken: {end_time - start_time:.2f} seconds")
        print(f"[INFO] Saved batch {batch_idx + 1} ({len(batch)} entries)")
        batch_idx += 1


if __name__ == "__main__":
    if os.path.exists(URL_PROCESSED_PATH):
        print(f"[INFO] Deleting {URL_PROCESSED_PATH}")
        os.remove(URL_PROCESSED_PATH)
    extract_url_features()