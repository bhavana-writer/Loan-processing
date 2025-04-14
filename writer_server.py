import sys
import os
import logging
from pathlib import Path
import importlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

try:
    # Import Writer Framework modules
    import writer as wf
    from writer.serve import app as writer_app
    
    # Log successful import
    logger.info("Writer Framework imported successfully")
    
    # Initialize Writer Framework app
    logger.info("Initializing Writer Framework app")
    
    # Import main app to ensure state is initialized
    try:
        import main
        logger.info("Main app imported successfully")
    except Exception as e:
        logger.error(f"Error importing main app: {e}")
    
    # Set the app variable to the Writer Framework app
    app = writer_app
    logger.info("Writer Framework app assigned to 'app'")
    
    # Add additional routes if needed
    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "framework": "writer"}

except ImportError as e:
    # Fall back to a basic FastAPI app if Writer Framework can't be imported
    logger.error(f"Error importing Writer Framework: {e}")
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    
    app = FastAPI(title="Loan Processing App (Fallback)")
    
    @app.get("/")
    async def root():
        return HTMLResponse(content="""
        <html>
            <head>
                <title>Loan Processing App</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .error { color: red; background-color: #ffe6e6; padding: 10px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Loan Processing App</h1>
                <div class="error">
                    <h2>Writer Framework Error</h2>
                    <p>The Writer Framework could not be initialized. This is a fallback page.</p>
                </div>
                <p>Please check the application logs for more information.</p>
            </body>
        </html>
        """)
    
    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "framework": "fallback"}

# Direct execution handler
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting server on port: {port}")
    uvicorn.run("writer_server:app", host="0.0.0.0", port=port, log_level="info") 