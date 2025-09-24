FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY samples/ ./samples/

# Create output directory
RUN mkdir -p /app/output

# Set Python path
ENV PYTHONPATH=/app/src

# Make CLI executable
RUN chmod +x /app/src/firefly_analyzer/cli.py

# Default command
CMD ["python", "-m", "firefly_analyzer.cli", "--help"]
