import sys
import os
import logging
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Loan Processing App")

# Load environment variables
load_dotenv()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Loan Processing App", "status": "ok"}

# Health check endpoint
@app.get("/healthcheck")
async def health_check():
    return {"status": "ok"}

# API endpoint
@app.get("/api/info")
async def api_info():
    return {
        "app_name": os.getenv("APP_NAME", "Loan Processing App"),
        "version": "1.0.0",
        "environment": os.getenv("ENV", "production")
    }

# For direct execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting server on port: {port}")
    uvicorn.run("server_deploy:app", host="0.0.0.0", port=port, log_level="info") 