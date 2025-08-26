FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy neural darwinism engine from consciousness-ai-bridge
COPY ../consciousness-ai-bridge/neural_darwinism.py ./neural_darwinism.py

# Copy service files
COPY unified_consciousness_service.py .
COPY consciousness-unified.service ./consciousness-unified.service

# Create directories
RUN mkdir -p /app/logs /app/static /app/templates

# Copy static files and templates if they exist
COPY static/ ./static/ 2>/dev/null || true
COPY templates/ ./templates/ 2>/dev/null || true

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Run the unified consciousness service
CMD ["python", "unified_consciousness_service.py"]