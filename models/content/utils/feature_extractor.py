import re
import math
import pandas as pd
from models.content.config import FEATURES

class ContentFeatureExtractor:
    """
    Extracts content-based features from HTML documents.
    Returns a pandas DataFrame with columns matching FEATURES from config.
    """
    def __init__(self):
        self.feature_names = FEATURES

    def transform(self, X):
        """
        Extract features from a list or Series of HTML strings and return a DataFrame.
        For now, each feature is a stub (returns 0 or simple placeholder logic).
        """
        s = pd.Series(X, dtype=str)
        features = {}
        for feature in self.feature_names:
            # Placeholder: all features return 0 for now
            features[feature] = [0] * len(s)
        return pd.DataFrame(features) 