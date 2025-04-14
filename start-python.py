#!/usr/bin/env python3
"""
Start script for the Loan Processing application on Render.
This script explicitly initializes the Writer Framework app and starts the server.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

def start_server():
    """Initialize and start the FastAPI server"""
    
    # Get the port from environment or use default
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting server on port: {port}")
    
    try:
        # Try to import writer framework
        import writer as wf
        logger.info("Writer Framework imported successfully")
        
        # Try to import main app to initialize state
        try:
            import main
            logger.info("Main app imported successfully")
        except Exception as e:
            logger.error(f"Error importing main app: {e}")
            
        # Check if writer.serve is available
        try:
            import writer.serve
            if hasattr(writer.serve, 'run'):
                logger.info("Starting server with writer.serve.run()")
                # Run the server with writer.serve
                writer.serve.run(host="0.0.0.0", port=port)
                return
        except Exception as e:
            logger.error(f"Error starting with writer.serve: {e}")
        
        # Fallback to uvicorn with our writer_server
        import uvicorn
        logger.info("Starting server with uvicorn and writer_server.py")
        uvicorn.run("writer_server:app", host="0.0.0.0", port=port, log_level="info")
            
    except ImportError as e:
        logger.error(f"Error importing Writer Framework: {e}")
        # Fallback to basic server
        import uvicorn
        logger.info("Starting server with uvicorn and server_deploy.py")
        uvicorn.run("server_deploy:app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    start_server() 