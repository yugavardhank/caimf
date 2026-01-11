FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data
RUN mkdir -p data/raw data/processed

# Expose ports
EXPOSE 8000 8501

# Default command (API)
CMD ["uvicorn", "caimf.api:app", "--host", "0.0.0.0", "--port", "8000"]
