# Use a minimal Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy only the requirements first to leverage Docker's caching
COPY requirements.txt .

# Install dependencies and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    git cron && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Set up cron jobs
RUN echo "*/15 * * * * /usr/local/bin/python3.10 /app/news_cron.py >> /var/log/news_cron.log 2>&1" > /etc/cron.d/mycron && \
    chmod 0644 /etc/cron.d/mycron && \
    crontab /etc/cron.d/mycron && \
    touch  /var/log/news_cron.log

# Expose the application port for FastAPI
EXPOSE 8000

# Default command is overridden in `docker-compose.yml`
# The cron container uses the `cron` and log tailing commands, while the app container uses uvicorn
# CMD ["tail", "-f", "/var/log/cron.log"]