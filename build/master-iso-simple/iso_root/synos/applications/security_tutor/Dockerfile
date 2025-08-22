# Syn_OS Security Tutor Service
FROM python:3.11-slim

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG BUILD_DATE
ARG VERSION=latest

# Set labels for metadata
LABEL maintainer="Syn_OS Team" \
    version="${VERSION}" \
    build-date="${BUILD_DATE}" \
    description="Syn_OS Security Tutor Service"

# Create non-root user for security
RUN groupadd -r synos && useradd -r -g synos -s /bin/false synos

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements (use security dashboard requirements if no specific ones)
COPY ../security_dashboard/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy shared source code from parent directories
COPY ../../src/security/ /app/src/security/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/tmp /app/templates && \
    chown -R synos:synos /app

# Set environment variables
ENV PYTHONPATH="/app:/app/src" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8085/health || exit 1

# Switch to non-root user
USER synos

# Expose port
EXPOSE 8085

# Run the application
CMD ["python", "main.py"]
