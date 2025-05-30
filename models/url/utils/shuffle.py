import pandas as pd

# 1. Load the CSV
df = pd.read_csv("data/processed/url_features.csv")

# 2. Shuffle all rows
df_shuf = df.sample(frac=1, random_state=42).reset_index(drop=True)

# 3. Write back out
df_shuf.to_csv("data/processed/url_features.csv", index=False)