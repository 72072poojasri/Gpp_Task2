#!/bin/bash
# Install the cron job
crontab /app/cron/2fa-cron
# Start cron in foreground
cron -f
