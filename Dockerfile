# Lightweight Dockerfile for Railway deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy lightweight requirements
COPY requirements-light.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application with proper environment variable handling
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} 