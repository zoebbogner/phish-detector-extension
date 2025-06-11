import pandas as pd
import os

from models.content.config import CONTROLLER_FEATURES_DIR, PROCESSED_PATH, FEATURES
from utils.ml_helpers import load_and_preprocess_data

def load_controller_csvs() -> tuple[pd.DataFrame, pd.Series]:
    label_col: str = "label"
    files = os.listdir(CONTROLLER_FEATURES_DIR)

    final_X = pd.DataFrame(columns=FEATURES)
    final_y = pd.Series(dtype="int64")

    desired_cols = FEATURES + [label_col]
    
    for file in files:
        path = os.path.join(CONTROLLER_FEATURES_DIR, file)
        # Skip anything that is not a .csv
        if not file.lower().endswith(".csv"):
            continue
        try:
            # Only read the columns we actually need. Ignore everything else—pandas
            # will not attempt to parse extra fields, so the “Expected 28 fields”
            # error goes away.
            df = pd.read_csv(path, usecols=desired_cols)

        except Exception as e:
            print(f"⚠️  Skipping `{file}`: {e}")
            continue

        if "url" in df.columns:
            df = df.drop(columns=["url"])
            print(f"Dropped url column from {file}")

        # Drop any rows where any feature or label is NaN
        df = df.dropna(subset=list(FEATURES) + [label_col])
        # Concatenate features/labels with a fresh index
        final_X = pd.concat([final_X, df[FEATURES]], ignore_index=True)
        final_y = pd.concat([final_y, df[label_col]], ignore_index=True)

    return final_X, final_y

def load_all_csvs() -> tuple[pd.DataFrame, pd.Series]:
    # 1) Load everything from the “controller” folder
    X, y = load_controller_csvs()

    # 2) Load the master processed file, then append (and re‐index)
    X_master, y_master = load_and_preprocess_data(PROCESSED_PATH, FEATURES)
    X = pd.concat([X, X_master], ignore_index=True)
    
    y = pd.concat([y, y_master], ignore_index=True)

    # Suppose X is your DataFrame after concatenation:
    # (you already printed X.shape and saw the dtypes)

    # 1) Identify which columns are object‐typed
    obj_cols = X.select_dtypes(include="object").columns.tolist()
    # 2) Convert those columns to numeric (int or float as appropriate).
    #    We’ll use pd.to_numeric(..., errors='raise') to catch any remaining bad strings.
    for c in obj_cols:
        X[c] = pd.to_numeric(X[c], errors="raise")
    
    return X, y
    
    
if __name__ == "__main__":
    X, y = load_all_csvs()
    
    # print the number of 1's and 0's in y
    print(y.value_counts())
