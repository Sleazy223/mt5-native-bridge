
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, timezone

app = FastAPI(
    title="MT5 Native Bridge",
    description="Centralised MT5 account management API",
    version="2.0.0"
)

# Temporary in-memory demo storage.
# Records reset when the service restarts.
accounts = {}

class AccountCreate(BaseModel):
    owner_id: str
    label: str
    broker: str
    server: str
    login: str

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "MT5 Native Bridge",
        "version": "2.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/accounts")
def create_account(data: AccountCreate):
    account_id = str(uuid4())

    account = {
        "id": account_id,
        "owner_id": data.owner_id,
        "label": data.label,
        "broker": data.broker,
        "server": data.server,
        "login": data.login,
        "connection_status": "not_connected",
        "balance": 0.0,
        "equity": 0.0,
        "floating_pl": 0.0,
        "positions": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    accounts[account_id] = account

    return {
        "success": True,
        "account": account
    }

@app.get("/accounts")
def list_accounts(owner_id: str):
    return {
        "accounts": [
            account for account in accounts.values()
            if account["owner_id"] == owner_id
        ]
    }

@app.get("/accounts/{account_id}")
def get_account(account_id: str, owner_id: str):
    account = accounts.get(account_id)

    if not account or account["owner_id"] != owner_id:
        raise HTTPException(404, "Account not found")

    return account

@app.delete("/accounts/{account_id}")
def delete_account(account_id: str, owner_id: str):
    account = accounts.get(account_id)

    if not account or account["owner_id"] != owner_id:
        raise HTTPException(404, "Account not found")

    del accounts[account_id]

    return {"success": True, "message": "Account removed"}

@app.get("/accounts/{account_id}/positions")
def get_positions(account_id: str, owner_id: str):
    account = accounts.get(account_id)

    if not account or account["owner_id"] != owner_id:
        raise HTTPException(404, "Account not found")

    return {"positions": account["positions"]}
