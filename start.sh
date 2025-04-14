#!/bin/bash
# start.sh - Script to start the application optimized for Render

# Make the script executable
chmod +x start.sh

# Set memory limits for Python
export PYTHONUNBUFFERED=1
export PYTHONMALLOC=malloc

# Use the PORT environment variable provided by Render
PORT=${PORT:-8000}

# Start the application with optimized settings
exec gunicorn server_setup:asgi_app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --preload \
    --max-requests 1000 \
    --max-requests-jitter 50 