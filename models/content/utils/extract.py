import os
import time
from models.content.utils.feature_extractor import ContentFeatureExtractor
from models.content.config import FEATURES
from models.content.utils.load_from_db import load_html_dataset_by_zip
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
ZIP_DIR = "/Users/zoe/Downloads/n96ncsr5g4-1/dataset"
PROCESSED_PATH = "data/processed/content.csv"

def extract_html_features():
    """
    Extract HTML content features from a JSON array file and write them to a CSV in batches.
    """
    print(f"[INFO] Extracting features from {ZIP_DIR}...")
    extractor = ContentFeatureExtractor()
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
        features_df = extractor.transform_batch(batch)
        end_time = time.time()
        print(f"[INFO] Time taken: {end_time - start_time} seconds")
        print(f"[INFO] Features extracted for {len(features_df)} items")
        features_df = features_df[FEATURES]
        features_df["label"] = [entry["label"] for entry in batch if "html" in entry and "label" in entry]
        features_df.to_csv(PROCESSED_PATH,
                           mode="w" if first_write else "a",
                           index=False,
                           header=first_write
                           )
        
        first_write = False
        print(f"[INFO] Saved batch {batch_idx + 1} ({len(batch)} entries)")
        batch_idx += 1

if __name__ == "__main__":
    # delete the file if it exists
    if os.path.exists(PROCESSED_PATH):
        print(f"[INFO] Deleting {PROCESSED_PATH}")
        os.remove(PROCESSED_PATH)
    print(f"[INFO] Extracting features from {ZIP_DIR}...")
    extract_html_features()