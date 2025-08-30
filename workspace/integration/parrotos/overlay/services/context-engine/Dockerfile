FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including spaCy model
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/logs /app/data

# Expose port
EXPOSE 8085

# Run application
CMD ["python", "context_engine.py"]
