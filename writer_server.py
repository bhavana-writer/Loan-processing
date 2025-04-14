import sys
import os
import logging
from pathlib import Path

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

# Define a global app variable
app = None

try:
    # Import Writer Framework modules
    import writer as wf
    import writer.serve
    
    logger.info("Writer Framework imported successfully")
    
    # First, try to initialize Writer app directly
    try:
        # Initialize main app to load state
        import main
        logger.info("Main app imported successfully")
        
        # Try to get the app from writer.serve
        if hasattr(writer.serve, 'app') and writer.serve.app is not None:
            app = writer.serve.app
            logger.info("Using writer.serve.app")
        else:
            # Initialize directly using writer.serve.init_app()
            logger.info("writer.serve.app is None, initializing manually")
            if hasattr(writer.serve, 'init_app'):
                app = writer.serve.init_app()
                logger.info("App initialized using writer.serve.init_app()")
            else:
                logger.error("Could not initialize app - writer.serve.init_app not found")
                app = None
    except Exception as e:
        logger.error(f"Error initializing Writer app: {e}")
        app = None
        
except ImportError as e:
    logger.error(f"Error importing Writer Framework: {e}")
    app = None

# If we couldn't get the Writer app, create a fallback FastAPI app
if app is None:
    logger.warning("Using fallback FastAPI app")
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

# Add health check endpoint regardless of which app we're using
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "framework": "writer" if 'writer' in sys.modules else "fallback"}

# Direct execution handler
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting server on port: {port}")
    uvicorn.run("writer_server:app", host="0.0.0.0", port=port, log_level="info") 