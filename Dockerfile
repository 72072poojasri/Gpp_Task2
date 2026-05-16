FROM python:3.11-slim

# ---- Environment ----
ENV TZ=UTC
WORKDIR /app

# ---- System dependencies ----
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# ---- Python dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Application files ----
COPY app.py /app/app.py
COPY scripts /app/scripts
COPY cron/2fa-cron /etc/cron.d/2fa-cron
COPY start.sh /start.sh

# ---- Required key + seed files ----
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem
COPY encrypted_seed.txt /app/encrypted_seed.txt

# ---- Cron setup ----
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron && \
    chmod +x /start.sh && \
    mkdir -p /data /cron && \
    chmod 755 /data /cron

# ---- Expose API ----
EXPOSE 8080

# ---- Start services ----
CMD ["/start.sh"]