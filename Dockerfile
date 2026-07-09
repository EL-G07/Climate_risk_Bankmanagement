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

# Use Render's PORT environment variable
ENV PORT=8050
ENV PYTHONUNBUFFERED=1

# Expose the ports
EXPOSE 8050 8051

# Start the application
CMD ["python", "start_deploy.py"]