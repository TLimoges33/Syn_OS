FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/consciousness_state

# Set environment variables
ENV PYTHONPATH=/app
ENV RAY_DISABLE_IMPORT_WARNING=1
ENV RAY_ADDRESS=ray://ray-head:10001

# Expose Ray ports
EXPOSE 8265 10001 6379 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import ray; ray.init(address='auto', ignore_reinit_error=True); print('Ray cluster healthy')" || exit 1

# Run the distributed consciousness engine
CMD ["python", "ray_consciousness_engine.py"]
