
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4

app = FastAPI(
    title="MT5 Native Bridge",
    description="Central MT5 account and trading API",
    version="3.0.0"
)

# DEMONSTRATION STORAGE ONLY
accounts = {}
positions = {}
orders = {}
history = {}

def now():
    return datetime.now(timezone.utc).isoformat()

def get_account(account_id, owner_id):
    account = accounts.get(account_id)

    if not account or account["owner_id"] != owner_id:
        raise HTTPException(404, "Account not found")

    return account

class AccountCreate(BaseModel):
    owner_id: str
    label: str
    broker: str
    server: str
    login: str

class ConnectionRequest(BaseModel):
    account_id: str
    owner_id: str

class OrderRequest(BaseModel):
    account_id: str
    owner_id: str
    action: str = "DEAL"
    symbol: str
    volume: float = Field(gt=0)
    type: str
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    deviation: int = 20
    magic: int = 0
    comment: str = ""

class CloseRequest(BaseModel):
    account_id: str
    owner_id: str
    position_id: str

class ModifyRequest(BaseModel):
    account_id: str
    owner_id: str
    position_id: str
    sl: Optional[float] = None
    tp: Optional[float] = None

# HOME

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "MT5 Native Bridge",
        "version": "3.0.0",
        "mode": "SIMULATION"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# ACCOUNT MANAGEMENT

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
        "connection_status": "disconnected",
        "balance": 10000.0,
        "equity": 10000.0,
        "margin": 0.0,
        "free_margin": 10000.0,
        "currency": "USD",
        "created_at": now()
    }

    accounts[account_id] = account
    positions[account_id] = []
    orders[account_id] = []
    history[account_id] = []

    return {"success": True, "account": account}

@app.get("/accounts")
def list_accounts(owner_id: str):
    return {
        "accounts": [
            a for a in accounts.values()
            if a["owner_id"] == owner_id
        ]
    }

@app.get("/accounts/{account_id}")
def account_details(account_id: str, owner_id: str):
    return get_account(account_id, owner_id)

@app.delete("/accounts/{account_id}")
def delete_account(account_id: str, owner_id: str):
    get_account(account_id, owner_id)

    del accounts[account_id]
    positions.pop(account_id, None)
    orders.pop(account_id, None)
    history.pop(account_id, None)

    return {"success": True, "message": "Demo account removed"}

# CONNECTION MANAGEMENT

@app.post("/connection")
def connect(data: ConnectionRequest):
    account = get_account(data.account_id, data.owner_id)

    account["connection_status"] = "simulated_connected"
    account["connected_at"] = now()

    return {
        "success": True,
        "account_id": data.account_id,
        "connection_status": "simulated_connected",
        "simulation": True
    }

@app.get("/connection/{account_id}")
def connection_status(account_id: str, owner_id: str):
    account = get_account(account_id, owner_id)

    return {
        "account_id": account_id,
        "status": account["connection_status"],
        "simulation": True
    }

@app.delete("/connection/{account_id}")
def disconnect(account_id: str, owner_id: str):
    account = get_account(account_id, owner_id)

    account["connection_status"] = "disconnected"

    return {"success": True, "status": "disconnected"}

# ACCOUNT SUMMARY

@app.get("/AccountSummary")
def account_summary(account_id: str, owner_id: str):
    account = get_account(account_id, owner_id)

    account_positions = positions[account_id]

    floating = sum(
        p["profit"] for p in account_positions
    )

    return {
        "account_id": account_id,
        "login": account["login"],
        "broker": account["broker"],
        "server": account["server"],
        "balance": account["balance"],
        "equity": account["balance"] + floating,
        "floating_pl": floating,
        "margin": account["margin"],
        "free_margin": account["balance"] + floating - account["margin"],
        "currency": account["currency"],
        "simulation": True
    }

# POSITIONS

@app.get("/Positions")
def get_positions(account_id: str, owner_id: str):
    get_account(account_id, owner_id)

    return {
        "positions": positions[account_id],
        "simulation": True
    }

# ORDER SEND - SIMULATED

@app.post("/OrderSend")
def order_send(data: OrderRequest):
    account = get_account(data.account_id, data.owner_id)

    if account["connection_status"] != "simulated_connected":
        raise HTTPException(400, "Demo account is not connected")

    if data.action not in ["DEAL", "PENDING"]:
        raise HTTPException(400, "Unsupported demo action")

    if data.type not in [
        "BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT",
        "BUY_STOP", "SELL_STOP"
    ]:
        raise HTTPException(400, "Invalid order type")

    order_id = str(uuid4())

    order = {
        "order_id": order_id,
        "account_id": data.account_id,
        "symbol": data.symbol,
        "volume": data.volume,
        "action": data.action,
        "type": data.type,
        "price": data.price,
        "sl": data.sl,
        "tp": data.tp,
        "deviation": data.deviation,
        "magic": data.magic,
        "comment": data.comment,
        "status": "SIMULATED",
        "created_at": now()
    }

    orders[data.account_id].append(order)

    if data.action == "DEAL":
        position = {
            "position_id": str(uuid4()),
            "order_id": order_id,
            "symbol": data.symbol,
            "type": data.type,
            "volume": data.volume,
            "price_open": data.price or 0,
            "sl": data.sl,
            "tp": data.tp,
            "profit": 0.0,
            "magic": data.magic,
            "comment": data.comment,
            "status": "SIMULATED"
        }

        positions[data.account_id].append(position)

    return {
        "success": True,
        "order": order,
        "simulation": True,
        "message": "Simulated order created. No broker execution occurred."
    }

# ORDER LIST

@app.get("/Orders")
def get_orders(account_id: str, owner_id: str):
    get_account(account_id, owner_id)

    return {
        "orders": orders[account_id],
        "simulation": True
    }

# ORDER CLOSE - SIMULATED

@app.post("/OrderClose")
def close_order(data: CloseRequest):
    get_account(data.account_id, data.owner_id)

    account_positions = positions[data.account_id]

    position = next(
        (p for p in account_positions
         if p["position_id"] == data.position_id),
        None
    )

    if not position:
        raise HTTPException(404, "Position not found")

    account_positions.remove(position)

    history[data.account_id].append({
        **position,
        "status": "SIMULATED_CLOSED",
        "closed_at": now()
    })

    return {
        "success": True,
        "position_id": data.position_id,
        "status": "SIMULATED_CLOSED",
        "simulation": True
    }

# ORDER MODIFY - SIMULATED

@app.post("/OrderModify")
def modify_order(data: ModifyRequest):
    get_account(data.account_id, data.owner_id)

    position = next(
        (p for p in positions[data.account_id]
         if p["position_id"] == data.position_id),
        None
    )

    if not position:
        raise HTTPException(404, "Position not found")

    position["sl"] = data.sl
    position["tp"] = data.tp

    return {
        "success": True,
        "position": position,
        "simulation": True
    }

# ORDER HISTORY

@app.get("/OrderHistory")
def order_history(account_id: str, owner_id: str):
    get_account(account_id, owner_id)

    return {
        "history": history[account_id],
        "simulation": True
    }
