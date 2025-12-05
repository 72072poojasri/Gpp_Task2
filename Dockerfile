# Use Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy application files
COPY app.py /app/
COPY scripts /app/scripts/
COPY cron /app/cron/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cron (Linux) and dos2unix to fix line endings
RUN apt-get update && apt-get install -y cron dos2unix

# Ensure cron file has LF line endings
RUN dos2unix /app/cron/2fa-cron

# Copy entrypoint script
COPY scripts/start-cron.sh /app/start-cron.sh

# Make it executable inside container
RUN ["chmod", "+x", "/app/start-cron.sh"]

# Start cron in foreground
CMD ["/app/start-cron.sh"]
