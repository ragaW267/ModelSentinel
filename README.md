# ModelVault — AI Model Extraction Defense

`Still under development`

**An adaptive AI security middleware that detects and prevents model extraction attacks by analyzing API query behavior, input-space exploration, and decision-boundary probing.**

ModelVault protects the **ARGUS** predictive maintenance model (Random Forest classifier) from extraction attacks using a multi-signal detection engine with 5 behavioral analysis components, risk fusion, and adaptive security policies.

---

## Architecture

```
LAPTOP 1 — MODEL OWNER / SERVER          LAPTOP 2 — CLIENT / ATTACKER

┌─────────────────────────┐              ┌──────────────────────────┐
│     Server UI           │              │       Client UI          │
│   Security Dashboard    │              │                          │
│ (server-ui/index.html)  │              │  Normal User Mode        │
└──────────┬──────────────┘              │  Extraction Attack Mode  │
           │ polls every 3s              │ (client-ui/index.html)   │
           ▼                             └────────────┬─────────────┘
┌─────────────────────────┐                           │
│     MODELVAULT          │                           │ HTTP POST /predict
│   FastAPI Gateway       │◄──────────────────────────┘
│   (backend/main.py)     │
│                         │              ┌──────────────────────────┐
│  Request Logging        │              │   Client Scripts         │
│  Detection Engine       │              │  (client/normal_user.py) │
│  Risk Engine            │              │  (client/attacker.py)    │
│  Adaptive Defense       │              └────────────┬─────────────┘
└──────────┬──────────────┘                           │
           │                                          │
           ▼                                          │
┌─────────────────────────┐                           │
│     ARGUS MODEL         │              HTTP requests to SERVER_IP:8000
│  random_forest_model.pkl│◄──────────────────────────┘
└─────────────────────────┘
```

**The client NEVER has the ARGUS model.** All predictions go through the ModelVault gateway.

---

## Project Structure

```
ModelSentinel/
│
├── backend/                      ← SERVER-SIDE (Laptop 1)
│   ├── main.py                   ← FastAPI server + dashboard endpoints
│   ├── detector.py               ← ModelVault detection engine (912 lines)
│   ├── model/
│   │   └── random_forest_model.pkl  ← ARGUS trained model
│   ├── logs/
│   │   └── requests.jsonl        ← Persistent request log
│   └── requirements.txt          ← Server dependencies
│
├── server-ui/                    ← SERVER DASHBOARD (Laptop 1)
│   ├── index.html                ← Live security dashboard
│   ├── DESIGN.md                 ← Design system specification
│   └── screen.png                ← UI screenshot
│
├── client/                       ← CLIENT SCRIPTS (Laptop 2)
│   ├── normal_user.py            ← Normal user simulator
│   ├── attacker.py               ← Extraction attack simulator
│   └── requirements.txt          ← Client dependencies
│
├── client-ui/                    ← CLIENT CONSOLE (Laptop 2)
│   ├── index.html                ← Interactive client console
│   ├── DESIGN.md                 ← Design system specification
│   └── screen.png                ← UI screenshot
│
├── tests/                        ← Test scripts
│   ├── test_model.py             ← ARGUS model verification
│   └── test_detector.py          ← Detector smoke test
│
├── archive/                      ← Original files (backup)
│
└── README.md                     ← This file
```

---

## Quick Start

### LAPTOP 1 — SERVER

#### 1. Create and activate virtual environment
```powershell
cd ModelSentinel
python -m venv .venv
.venv\Scripts\activate
```

#### 2. Install dependencies
```powershell
pip install -r backend\requirements.txt
```

#### 3. Start FastAPI server
```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```
You should see: `ARGUS model loaded successfully`

#### 4. Find your local IP address
```powershell
ipconfig
```
Look for: `IPv4 Address . . . . : 192.168.X.X`

#### 5. Test the API
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Dashboard status: http://localhost:8000/dashboard/status

#### 6. Open the Server Dashboard
Open `server-ui/index.html` in your browser.

The dashboard will auto-connect to `http://localhost:8000` and poll every 3 seconds for live data.

---

### LAPTOP 2 — CLIENT

#### 1. Copy client files
Copy the `client/` and `client-ui/` folders to Laptop 2.

#### 2. Configure the Server URL

**For Python scripts:**
```powershell
set MODELVAULT_SERVER_URL=http://192.168.X.X:8000
```
(Replace `192.168.X.X` with the server laptop's IP address)

**For the Client UI:**
Open `client-ui/index.html` and enter the server URL in the input field at the top.

Or use a URL parameter:
```
client-ui/index.html?server=http://192.168.X.X:8000
```

#### 3. Install Python dependencies (for scripts)
```powershell
pip install -r client\requirements.txt
```

#### 4. Run Normal User mode
```powershell
cd client
python normal_user.py
```
Sends 7 varied, human-paced engine health queries. Expect: low risk, all ALLOWED.

#### 5. Run Extraction Attacker mode
```powershell
cd client
python attacker.py
```
Sends 30 rapid, systematic queries. Expect: escalating risk → BLOCK.

#### 6. Open the Client Console UI
Open `client-ui/index.html` in your browser.

- Enter the server URL and click CONNECT
- Toggle between Normal User and Extraction Attack modes
- Click SEND REQUEST for individual queries
- Click DISPATCH BURST for automated attack simulation

---

## Demo Walkthrough (For Judges)

### Normal User → Low Risk → ALLOW

```
STEP 1:  Start the FastAPI server on Laptop 1
STEP 2:  Open the Server Dashboard (server-ui/index.html)
STEP 3:  From Laptop 2, run normal_user.py or use Client UI in Normal mode
STEP 4:  Watch requests appear on the Server Dashboard
STEP 5:  Risk stays LOW (0–20), status: TRUSTED, action: ALLOW
STEP 6:  All 5 detection signals stay near zero
```

### Extraction Attacker → Risk Escalation → BLOCK

```
STEP 7:   Switch to attacker.py or Extraction Attack mode in Client UI
STEP 8:   Send systematic queries (monotonic sweep + boundary probing)
STEP 9:   Watch the Server Dashboard — risk score climbs rapidly

           Risk Trajectory:
           0 → 12 → 31 → 47 → 62 → 78 → 91

STEP 10:  Watch detection signals activate:
           ✓ Behavioral Anomaly    ↑  (automated scripting detected)
           ✓ Query Similarity      ↑  (high cosine clustering)
           ✓ Trajectory Analysis   ↑  (systematic perturbations)
           ✓ Boundary Probing      ↑  (prediction flips detected)
           ✓ Input Coverage        ↑  (systematic space exploration)

STEP 11:  Adaptive Defense escalates:
           ALLOW → RATE_LIMIT → RESTRICT → BLOCK

STEP 12:  Attacker receives:
           {
             "prediction": null,
             "message": "Request blocked by ModelVault..."
           }

STEP 13:  Server Dashboard shows:
           🔴 CRITICAL incident banner
           Risk chart with escalation trajectory
           Security events timeline
           Request log: ALLOW → LIMIT → BLOCK
```

---

## Detection Engine (5 Signals)

| Signal | What It Detects |
|--------|----------------|
| **Behavioral Fingerprinting** | Request frequency, regularity, burst patterns, volume |
| **Query Trajectory Analysis** | Monotonic sweeps, systematic perturbations, directional consistency |
| **Query Similarity Analysis** | High cosine similarity between consecutive queries |
| **Decision-Boundary Probing** | Prediction flips between near-identical inputs |
| **Input-Space Coverage** | Systematic exploration of the feature space |

All 5 signals are fused into a single risk score (0–100) using weighted combination, then mapped to an adaptive security policy:

| Risk Score | Status | Action |
|:----------:|--------|--------|
| 0 – 29 | TRUSTED | ALLOW |
| 30 – 49 | MONITORED | ALLOW |
| 50 – 69 | SUSPICIOUS | RATE_LIMIT |
| 70 – 84 | HIGH_RISK | RESTRICT |
| 85 – 100 | CRITICAL | BLOCK |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | System info |
| GET | `/health` | Health check |
| POST | `/predict` | Engine prediction with security analysis |
| GET | `/dashboard/status` | System status for dashboard |
| GET | `/dashboard/stats` | Aggregate statistics |
| GET | `/dashboard/requests` | Recent request log |
| GET | `/docs` | Swagger API documentation |

---

## Dependencies

### Server (backend/requirements.txt)
- fastapi
- uvicorn
- joblib
- numpy
- scikit-learn
- pydantic

### Client (client/requirements.txt)
- requests

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, FastAPI, uvicorn |
| Model | scikit-learn Random Forest (.pkl) |
| Detection | Custom Python engine (numpy + stdlib) |
| Server UI | HTML, Tailwind CSS CDN, Vanilla JS |
| Client UI | HTML, Tailwind CSS CDN, Vanilla JS |
| Client Scripts | Python + requests library |
| Communication | HTTP/JSON REST API |

No databases, no Docker, no Redis required. The entire system runs from two terminals.