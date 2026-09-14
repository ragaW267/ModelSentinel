from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import json
import time
import hashlib
import uuid
from pathlib import Path

from detector import ModelVaultDetector

# --------------------------------------------------
# FastAPI
# --------------------------------------------------

app = FastAPI(
    title="ModelVault",
    description="Adaptive AI security gateway for protecting the ARGUS engine health model",
    version="1.0"
)

# --------------------------------------------------
# CORS — allow all origins so the HTML UIs can connect
# from file:// pages, any IP, or any machine on LAN
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Load ARGUS model
# --------------------------------------------------

MODEL_PATH = "model/random_forest_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
    print("ARGUS model loaded successfully")
except Exception as e:
    model = None
    print(f"Failed to load ARGUS model: {e}")


# --------------------------------------------------
# ModelVault detector
# --------------------------------------------------

detector = ModelVaultDetector(max_history=200)


# --------------------------------------------------
# Input Schema
# --------------------------------------------------

class EngineInput(BaseModel):
    engine_rpm: float
    lub_oil_pressure: float
    fuel_pressure: float
    coolant_pressure: float
    lub_oil_temp: float
    coolant_temp: float
    pressure_ratio: float
    temp_diff: float


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "system": "ModelVault",
        "status": "online",
        "protected_model": "ARGUS Engine Predictive Maintenance",
        "security": "active"
    }


@app.get("/health")
def health():
    return {
        "api": "healthy",
        "model_loaded": model is not None,
        "detector": "active"
    }


# --------------------------------------------------
# Prediction Endpoint
# --------------------------------------------------

@app.post("/predict")
def predict(data: EngineInput, request: Request):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="ARGUS model is not loaded"
        )

    # --------------------------------------------------
    # Identify the client (IP-based for now; can be
    # replaced with API-key or session token later)
    # --------------------------------------------------

    client_id = request.client.host if request.client else "unknown"

    # --------------------------------------------------
    # Convert input into model feature vector
    # IMPORTANT: feature order must match model training
    # --------------------------------------------------

    features = np.array([[
        data.engine_rpm,
        data.lub_oil_pressure,
        data.fuel_pressure,
        data.coolant_pressure,
        data.lub_oil_temp,
        data.coolant_temp,
        data.pressure_ratio,
        data.temp_diff
    ]], dtype=float)

    # --------------------------------------------------
    # ARGUS prediction
    # --------------------------------------------------

    try:
        prediction = int(model.predict(features)[0])

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(features)[0]
            confidence = float(np.max(probabilities))
        else:
            confidence = None

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ARGUS prediction failed: {str(e)}"
        )

    # --------------------------------------------------
    # ModelVault security analysis
    # --------------------------------------------------

    security = detector.process(
        features=features[0].tolist(),
        prediction=prediction,
        confidence=confidence,
        client_id=client_id,
    )
  
    # --------------------------------------------------
    # SECURITY DECISIONS
    # --------------------------------------------------

    if security["action"] == "BLOCK":

        return {
            "model": "ARGUS",
            "prediction": None,
            "confidence": None,

            "security": {
                "request_id": security["request_id"],
                "risk_score": security["risk_score"],
                "scores": security["scores"],
                "status": security["status"],
                "action": "BLOCK",
                "reasons": security["reasons"],
            },

            "message": "Request blocked by ModelVault due to suspicious model-extraction behavior."
        }

    if security["action"] == "RESTRICT":

        return {
            "model": "ARGUS",
            "prediction": None,
            "confidence": None,

            "security": {
                "request_id": security["request_id"],
                "risk_score": security["risk_score"],
                "scores": security["scores"],
                "status": security["status"],
                "action": "RESTRICT",
                "reasons": security["reasons"],
            },

            "message": "Request restricted by ModelVault — high extraction risk detected."
        }

    # --------------------------------------------------
    # ALLOW / RATE_LIMIT — return prediction
    # --------------------------------------------------

    label = "FAULTY" if prediction == 1 else "NORMAL"

    return {
        "model": "ARGUS",

        "prediction": label,
        "prediction_class": prediction,
        "confidence": confidence,

        "security": {
            "request_id": security["request_id"],
            "risk_score": security["risk_score"],
            "scores": security["scores"],
            "status": security["status"],
            "action": security["action"],
            "reasons": security["reasons"],
        }
    }


# --------------------------------------------------
# Dashboard Endpoints  (consumed by server-ui)
# --------------------------------------------------

LOG_PATH = Path("logs/requests.jsonl")


def _read_log(limit: int = 200) -> list[dict]:
    """Read the most recent `limit` entries from the JSONL log (newest first)."""
    if not LOG_PATH.exists():
        return []
    try:
        lines = LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
        entries = []
        for line in reversed(lines[-limit:]):
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return entries
    except Exception:
        return []


@app.get("/dashboard/status")
def dashboard_status():
    """System status — consumed by the server monitoring UI."""
    return {
        "api_status": "online",
        "model_loaded": model is not None,
        "detector_status": "active",
        "uptime": "running",
        "protected_model": "ARGUS Random Forest Classifier",
        "environment": "LOCAL-02",
    }


@app.get("/dashboard/stats")
def dashboard_stats():
    """Aggregate statistics over all logged requests."""
    entries = _read_log(limit=5000)

    total = len(entries)
    blocked = sum(1 for e in entries if e.get("action") == "BLOCK")
    restricted = sum(1 for e in entries if e.get("action") == "RESTRICT")
    rate_limited = sum(1 for e in entries if e.get("action") == "RATE_LIMIT")
    suspicious = sum(1 for e in entries if e.get("status") in ("SUSPICIOUS", "HIGH_RISK", "CRITICAL"))
    unique_clients = len({e.get("client_id") for e in entries if e.get("client_id")})
    current_risk = entries[0].get("risk_score", 0.0) if entries else 0.0

    return {
        "total_requests": total,
        "blocked": blocked,
        "restricted": restricted,
        "rate_limited": rate_limited,
        "suspicious": suspicious,
        "unique_clients": unique_clients,
        "current_risk": current_risk,
    }


@app.get("/dashboard/requests")
def dashboard_requests(limit: int = Query(default=50, ge=1, le=500)):
    """Return the most recent requests with full security metadata."""
    entries = _read_log(limit=limit)

    result = []
    for e in entries:
        scores = e.get("scores", {})
        result.append({
            "request_id": e.get("request_id", ""),
            "timestamp": e.get("timestamp", 0),
            "client_id": e.get("client_id", "unknown"),
            "risk_score": e.get("risk_score", 0.0),
            "status": e.get("status", "UNKNOWN"),
            "action": e.get("action", "ALLOW"),
            "prediction": e.get("prediction"),
            "prediction_label": "FAULTY" if e.get("prediction") == 1 else ("NORMAL" if e.get("prediction") == 0 else None),
            "confidence": e.get("confidence"),
            "scores": {
                "behavioral": scores.get("behavioral", 0),
                "similarity": scores.get("similarity", 0),
                "trajectory": scores.get("trajectory", 0),
                "boundary": scores.get("boundary", 0),
                "coverage": scores.get("coverage", 0),
            },
            "reasons": e.get("reasons", []),
        })

    return {"requests": result, "count": len(result)}


# --------------------------------------------------
# Auth  (local JSON store — swap for MongoDB later)
# --------------------------------------------------

USERS_PATH = Path("users.json")


def _load_users() -> dict:
    if not USERS_PATH.exists():
        return {}
    try:
        return json.loads(USERS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_users(users: dict) -> None:
    USERS_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")


def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class AuthPayload(BaseModel):
    username: str
    password: str
    role: str = "client"  # 'client' or 'server'


@app.post("/auth/register")
def register(payload: AuthPayload):
    users = _load_users()
    uname = payload.username.strip().lower()

    if not uname or len(payload.password) < 4:
        raise HTTPException(status_code=400, detail="Username and password (min 4 chars) required.")

    if uname in users:
        raise HTTPException(status_code=409, detail="Username already exists.")

    users[uname] = {
        "id": str(uuid.uuid4()),
        "username": uname,
        "role": payload.role if payload.role in ("client", "server") else "client",
        "password_hash": _hash_pw(payload.password),
        "created_at": time.time(),
    }
    _save_users(users)
    return {"ok": True, "message": f"User '{uname}' registered successfully."}


@app.post("/auth/login")
def login(payload: AuthPayload):
    users = _load_users()
    uname = payload.username.strip().lower()
    user = users.get(uname)

    if not user or user["password_hash"] != _hash_pw(payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return {
        "ok": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user.get("role", "client"),
        },
        "message": "Login successful.",
    }
