"""
Extract features from raw URLs, train the teacher and student models, and evaluate the results.
"""
import argparse
import time
from models.content.utils.extract_features import extract_html_features
from models.content.model import train_model_for_training, train_model_for_production

def fetch_and_extract_features():
    """
    Fetch URLs, extract features, and save to disk.
    """
    extract_html_features()

def training():
    """
    Train the teacher and student models.
    """
    print("[INFO] Training model for training...")
    start_time = time.time()
    train_model_for_training()
    end_time = time.time()
    print(f"[INFO] Trained model in {end_time - start_time} seconds")
    
def production():
    """
    Train the model for production.
    """
    print("[INFO] Training model for production...")
    start_time = time.time()
    train_model_for_production()
    end_time = time.time()
    print(f"[INFO] Trained model in {end_time - start_time} seconds")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process URLs and train models")
    parser.add_argument("--fetch", action="store_true", help="Fetch URLs and extract features")
    args = parser.parse_args()
    
    if args.fetch:
        fetch_and_extract_features()
        
    training()
    production()