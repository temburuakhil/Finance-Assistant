#!/bin/bash

# Set default port if not provided
PORT=${PORT:-8000}

# Start the application
uvicorn main:app --host 0.0.0.0 --port $PORT 