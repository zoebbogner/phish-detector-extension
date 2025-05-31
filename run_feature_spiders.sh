#!/usr/bin/env bash
#
# run_feature_spiders.sh
#
# Usage: ./run_feature_spiders.sh  <chunk1> <chunk2>
#
# Example for Machine A:  ./run_feature_spiders.sh 1 2
# This will launch:
#   - scrapy crawl feature_spider -s SEEDS_CSV="phishing_crawler/seeds/seeds_1.csv"  -s LOG_FILE="crawl_1.log" -O content_features_1.csv:csv &
#   - scrapy crawl feature_spider -s SEEDS_CSV="phishing_crawler/seeds/seeds_2.csv"  -s LOG_FILE="crawl_2.log" -O content_features_2.csv:csv &
#
# The two spiders will run in parallel (backgrounded by “&”) and each will write its own .csv + .log.

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <chunk_index_1> <chunk_index_2>"
  echo "  e.g. $0 1 2    # (run seeds_1.csv and seeds_2.csv)"
  exit 1
fi

CHUNK1=$1
CHUNK2=$2

# You can set these paths relative to your project root:
SEEDS_DIR="phishing_crawler/seeds"
SPIDER_NAME="feature_spider"

# Launch spider for chunk $CHUNK1
echo "Starting spider on seeds_${CHUNK1}.csv → content_features_${CHUNK1}.csv  (log: crawl_${CHUNK1}.log)"
scrapy crawl ${SPIDER_NAME} \
  -s SEEDS_CSV="${SEEDS_DIR}/seeds_${CHUNK1}.csv" \
  -s LOG_FILE="crawl_${CHUNK1}.log" \
  -O "content_features_${CHUNK1}.csv:csv" &

# Launch spider for chunk $CHUNK2
echo "Starting spider on seeds_${CHUNK2}.csv → content_features_${CHUNK2}.csv  (log: crawl_${CHUNK2}.log)"
scrapy crawl ${SPIDER_NAME} \
  -s SEEDS_CSV="${SEEDS_DIR}/seeds_${CHUNK2}.csv" \
  -s LOG_FILE="crawl_${CHUNK2}.log" \
  -O "content_features_${CHUNK2}.csv:csv" &

# Optionally wait for both to finish before exiting this script:
wait
echo "Both spiders for chunks ${CHUNK1} and ${CHUNK2} have completed."