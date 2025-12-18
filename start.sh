#!/bin/sh
set -e

echo "Starting cron daemon..."
# Start cron in background
cron &

# Add a small delay to ensure cron daemon is ready
sleep 1

echo "Starting FastAPI application..."
# Start FastAPI with unicorn (runs in foreground to keep container alive)
exec unicorn app:app --host 0.0.0.0 --port 8080 --workers 1
