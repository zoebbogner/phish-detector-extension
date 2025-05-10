import pandas as pd
import argparse

def sample_df(df: pd.DataFrame, count: int) -> pd.DataFrame:
    """Return a random sample of `count` rows, or the full df if count ≤ 0 or ≥ len(df)."""
    if count <= 0 or count >= len(df):
        return df
    return df.sample(n=count, random_state=42)

def main():
    parser = argparse.ArgumentParser(
        description='Combine (and optionally sample) URL CSVs into one unified CSV.'
    )
    parser.add_argument('--file1',   required=True, help='First CSV, with columns url,label,source,timestamp')
    parser.add_argument('--file2',   required=True, help='Second CSV')
    parser.add_argument('--file3',   required=True, help='Third CSV')
    parser.add_argument('--count1',  type=int, default=0, help='# rows to sample from file1 (0 = all)')
    parser.add_argument('--count2',  type=int, default=0, help='# rows to sample from file2 (0 = all)')
    parser.add_argument('--count3',  type=int, default=0, help='# rows to sample from file3 (0 = all)')
    parser.add_argument('--output',  default='combined_urls.csv', help='Output CSV path')
    args = parser.parse_args()

    # Load and sample each
    dfs = []
    for path, cnt in [(args.file1, args.count1),
                      (args.file2, args.count2),
                      (args.file3, args.count3)]:
        df = pd.read_csv(path)
        # ensure required columns are present
        expected = {'url','label','source','timestamp'}
        if not expected.issubset(df.columns):
            raise ValueError(f"{path} is missing one of {expected}")
        dfs.append(sample_df(df, cnt))

    # Concatenate and write
    combined = pd.concat(dfs, ignore_index=True)
    combined.to_csv(args.output, index=False)
    print(f"✅ Wrote {len(combined)} rows to {args.output}")

if __name__ == "__main__":
    main()
