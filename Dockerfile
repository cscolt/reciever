# Dockerfile for Desktop Casting Receiver
# Provides a containerized deployment option

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Optional: Install UxPlay for iOS screen mirroring
# Uncomment if you want iOS support (requires additional dependencies)
# RUN apt-get update && apt-get install -y \
#     uxplay \
#     gstreamer1.0-tools \
#     gstreamer1.0-plugins-base \
#     && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY assets/ ./assets/
COPY run.py .

# Expose ports
# 8080: WebRTC/HTTP server
# 7000: AirPlay (Python fallback)
# 7100: UxPlay video port
EXPOSE 8080 7000 7100

# Environment variables
ENV DCR_HOST=0.0.0.0
ENV DCR_PORT=8080
ENV DCR_LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/status')" || exit 1

# Run in headless mode by default
CMD ["python", "run.py", "--headless"]
