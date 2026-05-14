#!/bin/bash
# Data retention cleanup - deletes X/Twitter scraped data older than 7 days
# GDPR compliance for Tesla FSD AI Bot

DATA_DIR="$HOME/Documents/tesla-fsd-ai-bot/summaries"
RETENTION_DAYS=7
LOG_FILE="$HOME/.openclaw/workspace/logs/data_retention.log"

# Create log dir if needed
mkdir -p "$(dirname "$LOG_FILE")"

# Find and delete files older than retention period
deleted_count=0
for file in "$DATA_DIR"/summary_*.json "$DATA_DIR"/summary_*.md; do
    if [ -f "$file" ]; then
        file_age_days=$(( ($(date +%s) - $(stat -f%m "$file")) / 86400 ))
        if [ "$file_age_days" -gt "$RETENTION_DAYS" ]; then
            rm "$file"
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted: $file (age: ${file_age_days}d)" >> "$LOG_FILE"
            ((deleted_count++))
        fi
    fi
done

# Log completion
if [ "$deleted_count" -gt 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup complete. Deleted $deleted_count files." >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup complete. No old files found." >> "$LOG_FILE"
fi

# Keep only latest.json and latest.md (always preserved)
# source_performance.json is also preserved
