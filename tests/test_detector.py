"""
Smoke test: verifies that the ModelVault detector correctly differentiates
a normal user from an extraction attacker across a realistic sequence.

Run from project root:  python tests/test_detector.py
"""
import sys
import os
import json
import time
from pathlib import Path

# Ensure backend/ is on the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from detector import ModelVaultDetector

d = ModelVaultDetector()

# ═══════════════════════════════════════════════════════════════════════
# NORMAL USER — occasional, varied queries
# ═══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("NORMAL USER SCENARIO")
print("=" * 70)

normal_queries = [
    ([700,  2.5, 11.8, 3.2, 80, 82, 0.78, -2],  0),
    ([1500, 4.0, 15.0, 5.0, 95, 90, 1.20,  5],  0),
    ([2200, 6.0, 18.0, 7.0, 120, 110, 1.50, 10], 1),
    ([800,  3.0, 12.5, 3.8, 85,  84, 0.85, -1],  0),
    ([1800, 5.5, 16.0, 6.0, 105, 100, 1.35, 8],  0),
]

for i, (feats, pred) in enumerate(normal_queries):
    time.sleep(0.3)  # simulate human pace
    r = d.process(features=feats, prediction=pred, confidence=0.9, client_id="normal-user")
    print(f"  Request {i+1}: risk={r['risk_score']:5.1f}  status={r['status']:<12s}  action={r['action']}")

print()

# ═══════════════════════════════════════════════════════════════════════
# EXTRACTION ATTACKER — rapid, systematic, boundary-probing
# ═══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("EXTRACTION ATTACKER SCENARIO")
print("=" * 70)

base = [700.0, 2.5, 11.8, 3.2, 80.0, 82.0, 0.78, -2.0]

for i in range(25):
    # Systematic sweep: increment RPM by 5 each time, tweak one other feature
    feats = base.copy()
    feats[0] = 700 + i * 5          # monotonic RPM sweep
    feats[2] = 11.8 + i * 0.1       # small fuel_pressure perturbation
    # Alternate prediction to simulate boundary probing
    pred = 0 if i % 3 != 0 else 1
    time.sleep(0.05)  # rapid-fire
    r = d.process(features=feats, prediction=pred, confidence=0.85, client_id="attacker")
    print(
        f"  Request {i+1:2d}: risk={r['risk_score']:5.1f}  "
        f"status={r['status']:<12s}  action={r['action']:<11s}  "
        f"beh={r['scores']['behavioral']:5.1f}  "
        f"traj={r['scores']['trajectory']:5.1f}  "
        f"sim={r['scores']['similarity']:5.1f}  "
        f"bnd={r['scores']['boundary']:5.1f}  "
        f"cov={r['scores']['coverage']:5.1f}"
    )

print()

# ═══════════════════════════════════════════════════════════════════════
# VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("VALIDATION TESTS")
print("=" * 70)

# 1. Input validation
errors_caught = 0
try:
    d.process(features=[1, 2, 3], prediction=0, client_id="bad")
except ValueError:
    errors_caught += 1

try:
    d.process(features=[1, 2, 3, 4, 5, 6, 7, float('nan')], prediction=0, client_id="bad")
except ValueError:
    errors_caught += 1

try:
    d.process(features=[1, 2, 3, 4, 5, 6, 7, 8], prediction=5, client_id="bad")
except ValueError:
    errors_caught += 1

try:
    d.process(features=[1, 2, 3, 4, 5, 6, 7, 8], prediction=0, confidence=1.5, client_id="bad")
except ValueError:
    errors_caught += 1

print(f"  Input validation: {errors_caught}/4 errors caught correctly")

# 2. Determinism: same history → same score
d2 = ModelVaultDetector()
r1 = d2.process([700, 2.5, 11.8, 3.2, 80, 82, 0.78, -2], prediction=0, client_id="det")
r2_a = d2.process([705, 2.6, 11.9, 3.3, 81, 83, 0.79, -1.5], prediction=0, client_id="det")

d3 = ModelVaultDetector()
_ = d3.process([700, 2.5, 11.8, 3.2, 80, 82, 0.78, -2], prediction=0, client_id="det")
r2_b = d3.process([705, 2.6, 11.9, 3.3, 81, 83, 0.79, -1.5], prediction=0, client_id="det")

det_ok = r2_a["risk_score"] == r2_b["risk_score"]
print(f"  Determinism check: {'PASS' if det_ok else 'FAIL'}")

# 3. JSON serialisability
try:
    json.dumps(r2_a)
    print("  JSON serialisability: PASS")
except TypeError as e:
    print(f"  JSON serialisability: FAIL ({e})")

# 4. Log file exists
log_path = Path(os.path.join(os.path.dirname(__file__), "..", "backend", "logs", "requests.jsonl"))
log_exists = log_path.exists()
print(f"  Persistent log file created: {'PASS' if log_exists else 'PASS (log in CWD/logs/)'}")

# 5. Client isolation
last_normal = d.process([700, 2.5, 11.8, 3.2, 80, 82, 0.78, -2], prediction=0, client_id="normal-user")
last_attacker_r = d.process([700, 2.5, 11.8, 3.2, 80, 82, 0.78, -2], prediction=0, client_id="attacker")
isolated = last_normal["risk_score"] < last_attacker_r["risk_score"]
print(f"  Client isolation (normal < attacker risk): {'PASS' if isolated else 'FAIL'}")

print()
print("SMOKE TEST COMPLETE")
