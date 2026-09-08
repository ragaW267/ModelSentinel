from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np

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

detector = ModelVaultDetector(max_history=100)


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
def predict(data: EngineInput):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="ARGUS model is not loaded"
        )

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
        prediction=prediction
    )

    # --------------------------------------------------
    # SECURITY DECISION
    # --------------------------------------------------

    if security["action"] == "BLOCK":

        return {
            "model": "ARGUS",
            "prediction": None,
            "confidence": None,

            "security": {
                "risk_score": security["risk_score"],
                "behavioral_score": security["behavioral_score"],
                "similarity_score": security["similarity_score"],
                "boundary_score": security["boundary_score"],
                "status": security["status"],
                "action": "BLOCK"
            },

            "message": "Request blocked by ModelVault due to suspicious model-extraction behavior."
        }

    # --------------------------------------------------
    # ALLOW RESPONSE
    # --------------------------------------------------

    label = "FAULTY" if prediction == 1 else "NORMAL"

    return {
        "model": "ARGUS",

        "prediction": label,
        "prediction_class": prediction,
        "confidence": confidence,

        "security": {
            "risk_score": security["risk_score"],
            "behavioral_score": security["behavioral_score"],
            "similarity_score": security["similarity_score"],
            "boundary_score": security["boundary_score"],
            "status": security["status"],
            "action": security["action"]
        }
    }