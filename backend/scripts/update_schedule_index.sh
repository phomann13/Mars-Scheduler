#!/bin/bash
#
# Update Schedule Index - Scrape and Index Current Semester
# ==========================================================
#
# Usage:
#   ./scripts/update_schedule_index.sh --semester 202601 --all
#   ./scripts/update_schedule_index.sh --semester 202601 --department CMSC
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
SEMESTER=""
DEPARTMENT=""
ALL_FLAG=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --semester)
      SEMESTER="$2"
      shift 2
      ;;
    --department)
      DEPARTMENT="$2"
      shift 2
      ;;
    --all)
      ALL_FLAG="--all"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 --semester SEMESTER [--department DEPT | --all]"
      exit 1
      ;;
  esac
done

# Validate semester
if [ -z "$SEMESTER" ]; then
  echo -e "${RED}❌ Error: --semester is required${NC}"
  echo "Example: $0 --semester 202601 --all"
  exit 1
fi

# Validate department or all flag
if [ -z "$DEPARTMENT" ] && [ -z "$ALL_FLAG" ]; then
  echo -e "${RED}❌ Error: Must specify --department or --all${NC}"
  exit 1
fi

echo ""
echo "======================================================================"
echo "   UMD Schedule Scraper and Indexer"
echo "======================================================================"
echo -e "${BLUE}Semester:${NC} $SEMESTER"

if [ -n "$DEPARTMENT" ]; then
  echo -e "${BLUE}Department:${NC} $DEPARTMENT"
else
  echo -e "${BLUE}Mode:${NC} All departments"
fi

echo "======================================================================"
echo ""

# Step 1: Scrape schedule data
echo -e "${GREEN}Step 1/2: Scraping schedule data...${NC}"
echo ""

OUTPUT_FILE="backend/data/schedule_${SEMESTER}.json"

if [ -n "$DEPARTMENT" ]; then
  python3 backend/scripts/scrape_current_schedule.py \
    --semester "$SEMESTER" \
    --department "$DEPARTMENT" \
    --output "$OUTPUT_FILE"
else
  python3 backend/scripts/scrape_current_schedule.py \
    --semester "$SEMESTER" \
    --all \
    --output "$OUTPUT_FILE"
fi

echo ""
echo -e "${GREEN}✓ Scraping complete!${NC}"
echo ""

# Step 2: Index into Pinecone
echo -e "${GREEN}Step 2/2: Indexing into Pinecone...${NC}"
echo ""

python3 backend/scripts/index_schedule_data.py "$OUTPUT_FILE"

echo ""
echo -e "${GREEN}✓ Indexing complete!${NC}"
echo ""
echo "======================================================================"
echo "   All Done!"
echo "======================================================================"
echo -e "${GREEN}✓${NC} Schedule data scraped and indexed successfully"
echo -e "${BLUE}📁${NC} Data file: $OUTPUT_FILE"
echo -e "${BLUE}🔍${NC} The AI can now use this data for schedule generation"
echo "======================================================================"
echo ""

