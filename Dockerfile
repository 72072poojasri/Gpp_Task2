FROM python:3.11-slim

# ---- Environment ----
ENV TZ=UTC
WORKDIR /app

# ---- System deps ----
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# ---- Python deps ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- App code ----
COPY app.py /app/app.py
COPY scripts /app/scripts
COPY cron/2fa-cron /etc/cron.d/2fa-cron
COPY start.sh /start.sh

# ---- Cron setup ----
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron && \
    chmod +x /start.sh && \
    mkdir -p /data /cron && \
    chmod 755 /data /cron

# ---- Expose API ----
EXPOSE 8080

# ---- Start ----
CMD ["/start.sh"]
