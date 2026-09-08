"""
ModelVault — Normal User Simulator
===================================
Sends varied, human-paced engine health queries to the ModelVault API.
Simulates a legitimate user checking engine diagnostics.

Usage:
    set MODELVAULT_SERVER_URL=http://192.168.X.X:8000
    python normal_user.py
"""

import os
import sys
import time
import json
import random

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not installed.")
    print("Run: pip install requests")
    sys.exit(1)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

SERVER_URL = os.environ.get("MODELVAULT_SERVER_URL", "http://localhost:8000")
PREDICT_ENDPOINT = f"{SERVER_URL}/predict"

# --------------------------------------------------
# Realistic engine health queries (varied conditions)
# --------------------------------------------------

NORMAL_QUERIES = [
    {
        "name": "Idle engine — cold start",
        "engine_rpm": 700,
        "lub_oil_pressure": 2.5,
        "fuel_pressure": 11.8,
        "coolant_pressure": 3.2,
        "lub_oil_temp": 80,
        "coolant_temp": 82,
        "pressure_ratio": 0.78,
        "temp_diff": -2,
    },
    {
        "name": "Moderate load — highway cruising",
        "engine_rpm": 1500,
        "lub_oil_pressure": 4.0,
        "fuel_pressure": 15.0,
        "coolant_pressure": 5.0,
        "lub_oil_temp": 95,
        "coolant_temp": 90,
        "pressure_ratio": 1.20,
        "temp_diff": 5,
    },
    {
        "name": "High load — heavy acceleration",
        "engine_rpm": 2200,
        "lub_oil_pressure": 6.0,
        "fuel_pressure": 18.0,
        "coolant_pressure": 7.0,
        "lub_oil_temp": 120,
        "coolant_temp": 110,
        "pressure_ratio": 1.50,
        "temp_diff": 10,
    },
    {
        "name": "Light load — city driving",
        "engine_rpm": 800,
        "lub_oil_pressure": 3.0,
        "fuel_pressure": 12.5,
        "coolant_pressure": 3.8,
        "lub_oil_temp": 85,
        "coolant_temp": 84,
        "pressure_ratio": 0.85,
        "temp_diff": -1,
    },
    {
        "name": "Medium load — uphill drive",
        "engine_rpm": 1800,
        "lub_oil_pressure": 5.5,
        "fuel_pressure": 16.0,
        "coolant_pressure": 6.0,
        "lub_oil_temp": 105,
        "coolant_temp": 100,
        "pressure_ratio": 1.35,
        "temp_diff": 8,
    },
    {
        "name": "Idle — parking lot",
        "engine_rpm": 650,
        "lub_oil_pressure": 2.2,
        "fuel_pressure": 10.5,
        "coolant_pressure": 2.8,
        "lub_oil_temp": 75,
        "coolant_temp": 78,
        "pressure_ratio": 0.70,
        "temp_diff": -3,
    },
    {
        "name": "Moderate — gentle acceleration",
        "engine_rpm": 1200,
        "lub_oil_pressure": 3.5,
        "fuel_pressure": 13.8,
        "coolant_pressure": 4.5,
        "lub_oil_temp": 90,
        "coolant_temp": 88,
        "pressure_ratio": 1.05,
        "temp_diff": 2,
    },
]


def send_query(query: dict, index: int) -> None:
    """Send a single query and display the result."""
    name = query.pop("name", f"Query {index}")
    print(f"\n{'─' * 60}")
    print(f"  [{index}] {name}")
    print(f"  Features: {json.dumps(query, indent=None)}")

    try:
        resp = requests.post(PREDICT_ENDPOINT, json=query, timeout=10)
        data = resp.json()

        prediction = data.get("prediction", "N/A")
        confidence = data.get("confidence", "N/A")
        security = data.get("security", {})
        risk_score = security.get("risk_score", "N/A")
        action = security.get("action", "N/A")
        status = security.get("status", "N/A")

        if confidence and isinstance(confidence, float):
            confidence = f"{confidence:.1%}"

        print(f"  Prediction: {prediction}  |  Confidence: {confidence}")
        print(f"  Risk: {risk_score}  |  Status: {status}  |  Action: {action}")

        if action in ("BLOCK", "RESTRICT"):
            print(f"  ⚠  {data.get('message', 'Blocked')}")

    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection failed — is the server running at {SERVER_URL}?")
    except Exception as e:
        print(f"  ✗ Error: {e}")


def main():
    print("=" * 60)
    print("  ModelVault — Normal User Simulator")
    print("=" * 60)
    print(f"  Server: {SERVER_URL}")
    print(f"  Endpoint: {PREDICT_ENDPOINT}")
    print(f"  Queries: {len(NORMAL_QUERIES)}")
    print()

    # Check server health first
    try:
        health = requests.get(f"{SERVER_URL}/health", timeout=5)
        h = health.json()
        print(f"  Server health: {h.get('api', '?')}  |  Model loaded: {h.get('model_loaded', '?')}")
    except Exception:
        print("  ⚠  Could not reach server health endpoint")
        print(f"     Make sure the server is running at {SERVER_URL}")
        return

    for i, query in enumerate(NORMAL_QUERIES, 1):
        q = dict(query)  # copy so we don't mutate
        send_query(q, i)
        # Human-like delay: 2–5 seconds between queries
        delay = random.uniform(2.0, 5.0)
        print(f"  (waiting {delay:.1f}s ...)")
        time.sleep(delay)

    print(f"\n{'=' * 60}")
    print("  Normal user simulation complete.")
    print(f"  All {len(NORMAL_QUERIES)} queries sent with human-paced timing.")
    print(f"  Expected result: Low risk, all ALLOWED.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
