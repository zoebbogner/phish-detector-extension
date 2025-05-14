"""
Extract features from raw URLs, train the teacher and student models, and evaluate the results.
"""
import time, argparse
from models.url.model import train_model_for_training, train_model_for_production
from models.url.utils.fetch_urls.extract_url_features import extract_url_features
from models.url.utils.fetch_urls.fetch import fetch_urls

def fetch_and_extract_features():
    """
    Fetch URLs, extract features, and save to disk.
    """
    fetch_urls()
    start_time = time.time()
    extract_url_features()
    end_time = time.time()
    print(f"[INFO] Extracted features in {end_time - start_time} seconds")
    print(f"[INFO] Each url took {(end_time - start_time) / 1061131} seconds")

def training():
    """
    Train the teacher and student models.
    """
    start_time = time.time()
    train_model_for_training()
    end_time = time.time()
    print(f"[INFO] Trained model in {end_time - start_time} seconds")
    
def production():
    """
    Train the model for production.
    """
    start_time = time.time()
    train_model_for_production()
    end_time = time.time()
    print(f"[INFO] Trained model in {end_time - start_time} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Fetch URLs and extract features")
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--production", action="store_true", help="Train the model for production")
    args = parser.parse_args()

    if args.fetch:
        fetch_and_extract_features()
    if args.train:
        training()
    if args.production:
        production()
    
    if not args.fetch and not args.train and not args.production:
        fetch_and_extract_features()
        training()
        production()
    
    

















