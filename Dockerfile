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
COPY start.sh /start.sh
RUN chmod +x /start.sh


# Start cron in foreground
CMD ["/start.sh"]

