#!/bin/bash
# start.sh - Script to start the application optimized for Render

# Display script execution for debugging
set -x

# Set memory limits for Python
export PYTHONUNBUFFERED=1
export PYTHONMALLOC=malloc

# Use the PORT environment variable provided by Render (default to 10000 if not set)
export PORT=${PORT:-10000}
echo "Starting server on port: $PORT"

# Start the application with optimized settings
# Using uvicorn directly with the simplified server_deploy.py
exec uvicorn server_deploy:app --host 0.0.0.0 --port $PORT --log-level info 