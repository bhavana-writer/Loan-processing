import os
import sys
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

def main():
    """Main entry point for the application"""
    # Configure environment
    port = int(os.environ.get("PORT", 10000))
    os.environ["WRITER_APP_PORT"] = str(port)
    os.environ["WRITER_APP_HOST"] = "0.0.0.0"
    
    logger.info(f"Starting Writer app on port: {port}")
    
    try:
        # Import main to initialize state first
        import main
        logger.info("Successfully imported main.py")
        
        # Then import writer.serve module
        import writer.serve
        logger.info("Successfully imported writer.serve")
        
        # Start the app - this is the writer-recommended approach
        writer.serve.main()
        
    except Exception as e:
        logger.error(f"Error starting the app: {e}")
        
        # Fall back to a simple server
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        import uvicorn
        
        app = FastAPI(title="Loan Processing App - Emergency Mode")
        
        @app.get("/")
        async def root():
            return HTMLResponse(content=f"""
            <html>
                <head>
                    <title>Loan Processing App - Error</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                        .error {{ color: red; background-color: #ffe6e6; padding: 10px; border-radius: 5px; }}
                        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                    </style>
                </head>
                <body>
                    <h1>Loan Processing App</h1>
                    <div class="error">
                        <h2>Writer Framework Error</h2>
                        <p>The Writer Framework failed to start with error:</p>
                        <pre>{str(e)}</pre>
                    </div>
                    <p>Check application logs for details.</p>
                </body>
            </html>
            """)
        
        @app.get("/healthcheck")
        async def health_check():
            return {"status": "error", "error": str(e)}
        
        logger.info("Starting emergency FastAPI server")
        uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main() 