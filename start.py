#!/usr/bin/env python3
import os
import subprocess
import sys

# Get port from environment variable with fallback
port = os.environ.get('PORT', '8000')

# Start uvicorn
cmd = [
    sys.executable, '-m', 'uvicorn',
    'main:app',
    '--host', '0.0.0.0',
    '--port', port
]

subprocess.run(cmd) 