# Phase 4 Integration Bridge Dockerfile
# ====================================
# Multi-stage build for production-ready integration bridge

FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc6-dev \
    make \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r synos && useradd -r -g synos synos

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Copy application code
COPY phase4_integration_bridge.py .
COPY __init__.py .

# Copy other required modules
COPY ../security/ security/
COPY ../security_orchestration/ security_orchestration/
COPY ../consciousness_v2/ consciousness_v2/

# Create necessary directories
RUN mkdir -p logs data \
    && chown -R synos:synos /app

# Set proper permissions
RUN chown -R synos:synos /app

# Switch to non-root user
USER synos

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8085/health || exit 1

# Expose port
EXPOSE 8085

# Default command
CMD ["python", "phase4_integration_bridge.py"]