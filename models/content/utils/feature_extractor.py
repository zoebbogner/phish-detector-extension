"""
This file contains the ContentFeatureExtractor class, which is used to extract content-based features from HTML documents.
"""
import pandas as pd
from models.content.utils.feature_helper import extract_html_features
from models.content.config import FEATURES

class ContentFeatureExtractor:
    """
    Extracts content-based features from HTML documents.
    Returns a pandas DataFrame with columns matching FEATURES from config.
    """
    def __init__(self):
        self.feature_names = FEATURES
        
    def transform(self, html, url):
        """
        Extracts features for a single URL and returns a one-row DataFrame.
        """
        features = extract_html_features(html, url)
        
        return pd.DataFrame([features])
    
    def transform_batch(self, batch: list[dict]) -> pd.DataFrame:
        """
        Extract features from a list of URLs. Returns a DataFrame of shape (n_urls, n_features).
        """
        dfs = [self.transform(entry["html"], entry["url"]) for entry in batch]
        df = pd.concat(dfs, ignore_index=True)
        df = df[self.feature_names]
        
        return df
    