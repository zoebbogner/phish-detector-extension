import pandas as pd
import random
import os
import argparse

def read_urls_from_file(file_path):
    """Read URLs from a file, one URL per line."""
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

def sample_urls(urls, count):
    """Sample 'count' URLs from the list, or all if fewer are available."""
    if count >= len(urls):
        return urls
    return random.sample(urls, count)

def main():
    parser = argparse.ArgumentParser(description='Combine URLs from multiple files into one CSV.')
    parser.add_argument('--file1', required=True, help='Path to first URL file')
    parser.add_argument('--file2', required=True, help='Path to second URL file')
    parser.add_argument('--file3', required=True, help='Path to third URL file')
    parser.add_argument('--count1', type=int, default=0, help='Number of URLs to take from first file (0 for all)')
    parser.add_argument('--count2', type=int, default=0, help='Number of URLs to take from second file (0 for all)')
    parser.add_argument('--count3', type=int, default=0, help='Number of URLs to take from third file (0 for all)')
    parser.add_argument('--output', default='combined_urls.csv', help='Output CSV file name')
    
    args = parser.parse_args()
    
    # Read URLs from files
    urls1 = read_urls_from_file(args.file1)
    urls2 = read_urls_from_file(args.file2)
    urls3 = read_urls_from_file(args.file3)
    
    print(f"File 1 contains {len(urls1)} URLs")
    print(f"File 2 contains {len(urls2)} URLs")
    print(f"File 3 contains {len(urls3)} URLs")
    
    # Sample URLs based on counts (0 means take all)
    count1 = len(urls1) if args.count1 <= 0 else min(args.count1, len(urls1))
    count2 = len(urls2) if args.count2 <= 0 else min(args.count2, len(urls2))
    count3 = len(urls3) if args.count3 <= 0 else min(args.count3, len(urls3))
    
    sampled_urls1 = sample_urls(urls1, count1)
    sampled_urls2 = sample_urls(urls2, count2)
    sampled_urls3 = sample_urls(urls3, count3)
    
    # Create a DataFrame with the URLs and their source
    data = []
    for url in sampled_urls1:
        data.append({'url': url, 'source': os.path.basename(args.file1)})
    for url in sampled_urls2:
        data.append({'url': url, 'source': os.path.basename(args.file2)})
    for url in sampled_urls3:
        data.append({'url': url, 'source': os.path.basename(args.file3)})
        
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(args.output, index=False)
    print(f"Combined {len(sampled_urls1)} URLs from {args.file1}, "
          f"{len(sampled_urls2)} URLs from {args.file2}, and "
          f"{len(sampled_urls3)} URLs from {args.file3}.")
    print(f"Total {len(df)} URLs saved to {args.output}")

if __name__ == "__main__":
    main()
