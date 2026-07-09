# Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for geopandas/fiona
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Render sets PORT for you at runtime - this is just a local-dev fallback.
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Only ONE port is public (Render exposes a single port per web service).
# app_risk.ipynb and prediction.ipynb still run on internal ports 8050/8051 -
# run_app.py starts both plus a reverse proxy on $PORT that routes between them.
EXPOSE 8080

# Start the application (see run_app.py - notebooks are never modified,
# only converted to throwaway scripts at container startup)
CMD ["python", "run_app.py"]