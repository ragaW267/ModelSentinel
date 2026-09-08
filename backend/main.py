from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import time

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
# CORS — required for cross-origin requests from
# Laptop 2 browser and the Server UI dashboard
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
    model_loaded_at = time.time()
    print("ARGUS model loaded successfully")
except Exception as e:
    model = None
    model_loaded_at = None
    print(f"Failed to load ARGUS model: {e}")


# --------------------------------------------------
# ModelVault detector
# --------------------------------------------------

detector = ModelVaultDetector(max_history=200)

# --------------------------------------------------
# In-memory request history for dashboard
# --------------------------------------------------

_recent_requests: list[dict] = []
_MAX_DASHBOARD_HISTORY = 500


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
    # Store for dashboard
    # --------------------------------------------------

    dashboard_record = {
        "timestamp": time.time(),
        "client_id": client_id,
        "request_id": security["request_id"],
        "features": features[0].tolist(),
        "prediction": prediction,
        "prediction_label": "FAULTY" if prediction == 1 else "NORMAL",
        "confidence": confidence,
        "risk_score": security["risk_score"],
        "scores": security["scores"],
        "status": security["status"],
        "action": security["action"],
        "reasons": security["reasons"],
    }

    _recent_requests.append(dashboard_record)
    if len(_recent_requests) > _MAX_DASHBOARD_HISTORY:
        _recent_requests.pop(0)

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


# ==================================================
# DASHBOARD API ENDPOINTS
# ==================================================

@app.get("/dashboard/status")
def dashboard_status():
    """System status for Server UI dashboard."""
    return {
        "system": "ModelVault",
        "api_status": "online",
        "model_loaded": model is not None,
        "model_name": "ARGUS (Random Forest Classifier)",
        "model_loaded_at": model_loaded_at,
        "detector_status": "active",
        "uptime_seconds": time.time() - model_loaded_at if model_loaded_at else 0,
    }


@app.get("/dashboard/stats")
def dashboard_stats():
    """Aggregate statistics for Server UI dashboard."""
    total = len(_recent_requests)
    blocked = sum(1 for r in _recent_requests if r["action"] == "BLOCK")
    restricted = sum(1 for r in _recent_requests if r["action"] == "RESTRICT")
    rate_limited = sum(1 for r in _recent_requests if r["action"] == "RATE_LIMIT")
    allowed = sum(1 for r in _recent_requests if r["action"] == "ALLOW")
    suspicious = sum(1 for r in _recent_requests if r["status"] in ("SUSPICIOUS", "HIGH_RISK", "CRITICAL"))

    # Current max risk across all clients
    current_risk = _recent_requests[-1]["risk_score"] if _recent_requests else 0.0
    current_status = _recent_requests[-1]["status"] if _recent_requests else "TRUSTED"

    # Unique client sessions
    unique_clients = len(set(r["client_id"] for r in _recent_requests))

    return {
        "total_requests": total,
        "allowed": allowed,
        "rate_limited": rate_limited,
        "restricted": restricted,
        "blocked": blocked,
        "suspicious": suspicious,
        "current_risk": current_risk,
        "current_status": current_status,
        "unique_clients": unique_clients,
    }


@app.get("/dashboard/requests")
def dashboard_requests(limit: int = 50):
    """Recent request log for Server UI dashboard."""
    return {
        "requests": list(reversed(_recent_requests[-limit:])),
        "total": len(_recent_requests),
    }