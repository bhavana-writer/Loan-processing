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

# Set environment variables for Writer Framework
export PYTHONPATH=$PYTHONPATH:$(pwd)
export WRITER_FRAMEWORK_ENV=production
export WRITER_APP_PORT=$PORT
export WRITER_APP_HOST="0.0.0.0"

# Print debugging information
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Available files:"
ls -la

# Start the app using the direct server approach
python server_direct.py 