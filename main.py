
from fastapi import FastAPI

app = FastAPI(
    title="MT5 Native Bridge",
    description="Your own MT5 Bridge API",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "MT5 Native Bridge API is running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.get("/accounts")
def accounts():
    return {
        "accounts": [],
        "message": "No accounts connected yet"
    }
