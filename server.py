import os
import uvicorn
from fastapi import FastAPI

# Create a simple FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Loan Processing App"}

@app.get("/healthcheck")
async def health_check():
    return {"status": "ok"}

# For direct execution
if __name__ == "__main__":
    # Get port from environment variable
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port: {port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info") 