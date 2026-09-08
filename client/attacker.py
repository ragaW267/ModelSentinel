"""
ModelVault — Extraction Attack Simulator
==========================================
Sends rapid, systematic queries designed to extract the ARGUS model
by probing decision boundaries and sweeping the input space.

Usage:
    set MODELVAULT_SERVER_URL=http://192.168.X.X:8000
    python attacker.py
"""

import os
import sys
import time
import json

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

# Number of extraction queries to send
NUM_QUERIES = 30

# Delay between queries (seconds) — fast to simulate automated attack
QUERY_DELAY = 0.15


def generate_extraction_queries(n: int) -> list[dict]:
    """Generate a systematic sweep of the feature space.

    Attack strategy:
    1. Start from a known baseline point
    2. Incrementally sweep engine_rpm (monotonic)
    3. Apply small perturbations to fuel_pressure
    4. Alternate prediction classes to find decision boundary
    5. Gradually expand coverage across multiple features
    """
    base = {
        "engine_rpm": 700.0,
        "lub_oil_pressure": 2.5,
        "fuel_pressure": 11.8,
        "coolant_pressure": 3.2,
        "lub_oil_temp": 80.0,
        "coolant_temp": 82.0,
        "pressure_ratio": 0.78,
        "temp_diff": -2.0,
    }

    queries = []
    for i in range(n):
        q = dict(base)

        # Phase 1 (0-9): Monotonic RPM sweep with small perturbations
        if i < 10:
            q["engine_rpm"] = 700 + i * 5
            q["fuel_pressure"] = 11.8 + i * 0.1

        # Phase 2 (10-19): Boundary probing — small changes around a point
        elif i < 20:
            q["engine_rpm"] = 750 + (i - 10) * 2
            q["lub_oil_pressure"] = 2.5 + (i - 10) * 0.05
            q["coolant_temp"] = 82 + (i - 10) * 0.5

        # Phase 3 (20-29): Wide coverage sweep
        else:
            q["engine_rpm"] = 500 + (i - 20) * 200
            q["fuel_pressure"] = 8.0 + (i - 20) * 1.5
            q["lub_oil_temp"] = 60 + (i - 20) * 12
            q["pressure_ratio"] = 0.5 + (i - 20) * 0.15

        queries.append(q)

    return queries


def main():
    print("=" * 60)
    print("  ⚡ ModelVault — Extraction Attack Simulator ⚡")
    print("=" * 60)
    print(f"  Server: {SERVER_URL}")
    print(f"  Endpoint: {PREDICT_ENDPOINT}")
    print(f"  Attack queries: {NUM_QUERIES}")
    print(f"  Query delay: {QUERY_DELAY}s (rapid-fire)")
    print()

    # Check server health first
    try:
        health = requests.get(f"{SERVER_URL}/health", timeout=5)
        h = health.json()
        print(f"  Server health: {h.get('api', '?')}  |  Model loaded: {h.get('model_loaded', '?')}")
    except Exception:
        print("  ✗ Could not reach server health endpoint")
        print(f"     Make sure the server is running at {SERVER_URL}")
        return

    queries = generate_extraction_queries(NUM_QUERIES)
    results = []

    print(f"\n{'─' * 60}")
    print(f"  {'#':>3}  {'RPM':>6}  {'Risk':>5}  {'Status':<12}  {'Action':<11}  {'Prediction'}")
    print(f"{'─' * 60}")

    blocked_count = 0
    restricted_count = 0

    for i, query in enumerate(queries, 1):
        try:
            resp = requests.post(PREDICT_ENDPOINT, json=query, timeout=10)
            data = resp.json()

            security = data.get("security", {})
            risk = security.get("risk_score", 0)
            status = security.get("status", "?")
            action = security.get("action", "?")
            prediction = data.get("prediction", data.get("prediction_class", "SUPPRESSED"))

            if action == "BLOCK":
                blocked_count += 1
                prediction = "BLOCKED"
            elif action == "RESTRICT":
                restricted_count += 1
                prediction = "RESTRICTED"

            # Color-code the output for terminal
            risk_indicator = "██" if risk >= 70 else "▓▓" if risk >= 50 else "░░" if risk >= 30 else "  "

            print(
                f"  {i:3d}  {query['engine_rpm']:6.0f}  {risk:5.1f}  {status:<12}  {action:<11}  {prediction}  {risk_indicator}"
            )

            results.append({
                "query_index": i,
                "risk_score": risk,
                "status": status,
                "action": action,
            })

        except requests.exceptions.ConnectionError:
            print(f"  {i:3d}  CONNECTION FAILED")
            break
        except Exception as e:
            print(f"  {i:3d}  ERROR: {e}")

        time.sleep(QUERY_DELAY)

    # Summary
    print(f"\n{'=' * 60}")
    print("  ATTACK SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total queries sent: {len(results)}")
    print(f"  Queries blocked:    {blocked_count}")
    print(f"  Queries restricted: {restricted_count}")

    if results:
        max_risk = max(r["risk_score"] for r in results)
        final_status = results[-1]["status"]
        final_action = results[-1]["action"]
        print(f"  Peak risk score:    {max_risk:.1f}")
        print(f"  Final status:       {final_status}")
        print(f"  Final action:       {final_action}")

        if blocked_count > 0:
            print(f"\n  ✓ ModelVault DETECTED the extraction attack!")
            print(f"    The model is PROTECTED — predictions were suppressed.")
        elif restricted_count > 0:
            print(f"\n  ⚠ ModelVault detected suspicious activity.")
            print(f"    Some predictions were restricted.")
        else:
            print(f"\n  ✗ ModelVault did not block the attack.")
            print(f"    Consider tuning detection thresholds.")

    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
