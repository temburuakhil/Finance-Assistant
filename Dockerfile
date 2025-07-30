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

# Make the startup script executable
RUN chmod +x /app/start.py

# Expose port
EXPOSE 8000

# Command to run the application with proper environment variable handling
CMD ["python", "/app/start.py"] 