# ModelVault — AI Model Extraction Defense

`Under Active Development`

**An adaptive AI security gateway and middleware that detects and prevents model extraction attacks in real time by analyzing query behavior, input-space exploration, and decision-boundary probing.**

ModelVault protects the **ARGUS** predictive maintenance model (Random Forest classifier) from intellectual property theft and unauthorized model replication using a multi-signal behavioral detection engine, dynamic risk scoring, role-based access control, and adaptive defense policies.

---

## Architecture & Flow

```
                                    ┌────────────────────────┐
                                    │       login.html       │
                                    │ Unified Auth & Portal  │
                                    └───────────┬────────────┘
                                                │
                     ┌──────────────────────────┴──────────────────────────┐
                     │ (Role: "client")                                    │ (Role: "server")
                     ▼                                                     ▼
       ┌──────────────────────────┐                          ┌──────────────────────────┐
       │        Client UI         │                          │        Server UI         │
       │  (client-ui/index.html)  │                          │  (server-ui/index.html)  │
       │                          │                          │    Security Dashboard    │
       │  • Normal User Queries   │                          │  • Real-Time Threat View │
       │  • Attack Simulator      │                          │  • 5-Signal Breakdown    │
       │  • Prediction Results    │                          │  • Auto-polls every 3s   │
       └─────────────┬────────────┘                          └─────────────┬────────────┘
                     │                                                     │
                     │ POST /predict                                       │ GET /dashboard/*
                     ▼                                                     ▼
       ┌────────────────────────────────────────────────────────────────────────────────┐
       │                           MODELVAULT FASTAPI GATEWAY                           │
       │                                  (main.py)                                     │
       │                                                                                │
       │  [Authentication]       [Request Audit Log]       [Detection Engine]           │
       │  POST /auth/register    logs/requests.jsonl       • Behavioral Fingerprinting  │
       │  POST /auth/login                                 • Query Trajectory           │
       │  users.json                                       • Cosine Similarity          │
       │                                                   • Boundary Probing           │
       │                                                   • Space Coverage             │
       │                                                                                │
       │                      [Adaptive Defense & Risk Scoring]                         │
       │                      ALLOW | RATE_LIMIT | RESTRICT | BLOCK                     │
       └───────────────────────────────────────┬────────────────────────────────────────┘
                                               │
                                               ▼
                              ┌──────────────────────────────────┐
                              │           ARGUS MODEL            │
                              │   model/random_forest_model.pkl  │
                              └──────────────────────────────────┘
```

> **Security Guarantee:** The client **never** has direct access to the ARGUS model file. All prediction requests must traverse the ModelVault inspection gateway.

---

## Project Structure

```
ModelSentinel/
├── main.py                     ← Core FastAPI gateway (Predict, Dashboard, & Auth APIs)
├── detector.py                 ← ModelVault 5-signal behavioral detection engine
├── login.html                  ← Unified login portal with role-based routing
├── users.json                  ← Local JSON user store (SHA-256 hashed)
├── requirements.txt            ← Project-wide server & gateway dependencies
├── README.md                   ← Project documentation
│
├── model/
│   └── random_forest_model.pkl ← ARGUS trained Random Forest model
│
├── logs/
│   └── requests.jsonl          ← Append-only JSON Lines security audit log
│
├── server-ui/                  ← Security Analyst Dashboard
│   ├── index.html              ← Real-time telemetry, risk graphs & audit feed
│   ├── DESIGN.md               ← UI/UX design tokens and layout spec
│   └── screen.png              ← Screenshot preview
│
├── client-ui/                  ← Client Console
│   ├── index.html              ← Interactive engine query & attack simulation console
│   ├── DESIGN.md               ← UI/UX design tokens and layout spec
│   └── screen.png              ← Screenshot preview
│
├── client/                     ← CLI Client Simulation Tools
│   ├── normal_user.py          ← Simulates benign human-like telemetry queries
│   ├── attacker.py             ← Simulates systematic extraction attacks
│   └── requirements.txt        ← Client script dependencies
│
├── tests/                      ← Verification and smoke tests
│   ├── test_model.py           ← ARGUS model integrity test
│   └── test_detector.py        ← Detector algorithm smoke tests
│
└── backend/                    ← Legacy standalone server package (retained for reference)
```

---

## Authentication & Role-Based Routing

ModelVault features a built-in authentication layer with role-based access control (RBAC):

1. **Unified Portal (`login.html`)**:
   - Offers single sign-on style authentication for both clients and administrators.
   - Includes an interactive **Role Selector**:
     - 💻 **Client Mode** (Cyan accent): Intended for machine operators and client applications. Automatically routes to `client-ui/index.html`.
     - 🖥️ **Server Admin Mode** (Purple accent): Intended for security engineers and SOC analysts. Automatically routes to `server-ui/index.html`.
   - Remembers the configured Server URL and session user in browser `localStorage` (`mv_user`).

2. **Credentials Storage (`users.json`)**:
   - Passwords are securely stored using SHA-256 hashing with per-installation salting.
   - Pre-seeded default admin account:
     - **Username:** `admin`
     - **Password:** `1234`
     - **Role:** `server`
   - New accounts can be registered instantly via the `Register` tab on `login.html`.

3. **CORS Enabled**:
   - `main.py` incorporates FastAPI `CORSMiddleware` configured with permissive cross-origin access (`*`), ensuring `login.html`, `client-ui`, and `server-ui` function seamlessly whether opened from `file://` protocols, local web servers, or across local area networks (LAN).

---

## Quick Start & Setup

### 1. Server Setup (Laptop 1 / Host Machine)

#### A. Prepare Virtual Environment
```powershell
# Open terminal in the ModelSentinel root directory
cd ModelSentinel

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### B. Start the Gateway Server
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```
*Expected console output: `ARGUS model loaded successfully` and `Uvicorn running on http://0.0.0.0:8000`.*

#### C. Find Your Local Network IP (For Multi-Device Setup)
```powershell
ipconfig
```
Locate your active adapter's **IPv4 Address** (e.g., `192.168.1.50`).

#### D. Allow Inbound Traffic on Port 8000 (Windows Firewall)
If accessing from a second laptop or mobile device over Wi-Fi/LAN, allow inbound TCP port 8000 (run as Administrator in PowerShell):
```powershell
netsh advfirewall firewall add rule name="ModelVault Gateway" dir=in action=allow protocol=TCP localport=8000
```

#### E. Access the Web Interfaces
Open `login.html` in your browser:
- On the host machine: `login.html?server=http://localhost:8000`
- Log in with `admin` / `1234` to access the **Server Security Dashboard** (`server-ui/index.html`).

---

### 2. Client Setup (Laptop 2 / Remote Device)

#### Method A: Via Web Browser (No Installation Needed)
1. Transfer or host `login.html`, `client-ui/`, and `server-ui/` on Laptop 2 (or serve them via any simple web server / file share).
2. Open `login.html` in a web browser with the server query parameter pointing to Laptop 1:
   ```
   login.html?server=http://192.168.1.50:8000
   ```
3. Register a new user or log in with role **Client** to automatically redirect to `client-ui/index.html?server=http://192.168.1.50:8000`.
4. Run individual queries or simulate automated extraction attacks directly from the UI.

#### Method B: Via CLI Attack/Normal Simulator Scripts
1. Navigate to the `client/` folder on Laptop 2:
   ```powershell
   cd client
   pip install -r requirements.txt
   ```
2. Configure the target server endpoint:
   ```powershell
   set MODELVAULT_SERVER_URL=http://192.168.1.50:8000
   ```
3. Run the simulators:
   - **Benign Normal Traffic:**
     ```powershell
     python normal_user.py
     ```
     *Sends varied, human-paced engine parameter readings. Expect low risk and ALLOW.*
   - **Extraction Attack Traffic:**
     ```powershell
     python attacker.py
     ```
     *Dispatches systematic parameter sweeps and decision-boundary probing. Expect risk score escalation and eventual BLOCK.*

---

## Live Attack Demonstration Walkthrough

### 1. Normal User Flow (Low Risk → ALLOW)
1. Open `server-ui/index.html` on Laptop 1.
2. From Laptop 2, run `python normal_user.py` or dispatch queries via the Client UI in **Normal User Mode**.
3. Watch requests appear in real time on the Server Dashboard.
4. **Behavior:**
   - Queries feature natural variance and realistic pacing.
   - Risk score remains low (`0 – 25`).
   - Threat level remains `TRUSTED`.
   - Action returned: `ALLOW`.

### 2. Model Extraction Attack Flow (Risk Escalation → BLOCK)
1. From Laptop 2, run `python attacker.py` or trigger **Extraction Attack Mode** / **Dispatch Burst** in the Client UI.
2. Watch the Server Dashboard live telemetry respond:
   - **Behavioral Fingerprinting** detects rapid, programmatic cadence.
   - **Query Trajectory Analysis** detects monotonic parameter sweeps.
   - **Query Similarity Analysis** identifies tight cosine clustering.
   - **Decision-Boundary Probing** detects high-frequency classification boundary crossing.
   - **Input-Space Coverage** flags methodical feature-space mapping.
3. **Adaptive Policy Escalation:**
   - Score climbs: `15 → 35 → 55 (RATE_LIMIT) → 75 (RESTRICT) → 90+ (BLOCK)`.
   - Client receives HTTP response with `prediction: null` and defensive security notice.
   - Server Dashboard triggers **CRITICAL INCIDENT ALERT** with full event timeline.

---

## Detection Engine (5 Core Signals)

| Signal | Mechanism & Detection Target | Weight |
|--------|------------------------------|:------:|
| **Behavioral Fingerprinting** | Request timing jitter, cadence variance, request bursts, high frequency | 20% |
| **Query Trajectory Analysis** | Monotonic stepping along feature dimensions, directional gradient consistency | 25% |
| **Query Similarity Analysis** | High cosine similarity between consecutive or clustered feature vectors | 20% |
| **Decision-Boundary Probing** | High ratio of label changes relative to input distance (hunting boundary) | 25% |
| **Input-Space Coverage** | Convex hull and grid coverage growth across normalized feature dimensions | 10% |

### Risk Policy Mapping

| Risk Score | Status | Adaptive Action | System Behavior |
|:----------:|:------:|:---------------:|-----------------|
| **0 – 29** | `TRUSTED` | `ALLOW` | Standard prediction returned with full precision. |
| **30 – 49** | `MONITORED` | `ALLOW` | Prediction returned; heightened query auditing enabled. |
| **50 – 69** | `SUSPICIOUS` | `RATE_LIMIT` | Artificial response delay introduced to degrade extraction speed. |
| **70 – 84** | `HIGH_RISK` | `RESTRICT` | Prediction noise / quantization applied to obscure exact boundary. |
| **85 – 100** | `CRITICAL` | `BLOCK` | Request rejected; extraction payload neutralized. |

---

## API Reference

### Security & Prediction
| Method | Endpoint | Description |
|:------:|----------|-------------|
| `GET` | `/` | Service health status and metadata |
| `GET` | `/health` | Live diagnostic health check |
| `POST` | `/predict` | Evaluates engine telemetry through ARGUS and ModelVault defense |
| `GET` | `/docs` | Interactive Swagger API documentation |

### Authentication & RBAC
| Method | Endpoint | Description |
|:------:|----------|-------------|
| `POST` | `/auth/register` | Registers a new user (`username`, `password`, `role: "client" \| "server"`) |
| `POST` | `/auth/login` | Authenticates credentials and returns user role |

### Dashboard Telemetry
| Method | Endpoint | Description |
|:------:|----------|-------------|
| `GET` | `/dashboard/status` | Current system state, active threat posture, and uptime |
| `GET` | `/dashboard/stats` | Aggregated metrics (total queries, blocked queries, average risk) |
| `GET` | `/dashboard/requests` | Fetch recent query logs (supports `?limit=N`) |

---

## Tech Stack

- **Gateway & Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic
- **Machine Learning Model:** scikit-learn Random Forest Classifier (`random_forest_model.pkl`)
- **Detection Engine:** NumPy, SciPy (multidimensional vector analysis & trajectory math)
- **User Interfaces:** Modern HTML5, Tailwind CSS CDN, Vanilla JavaScript (zero node build step required)
- **Persistence:** Local JSON (`users.json`), JSON Lines audit log (`logs/requests.jsonl`)

---

## Future Roadmap

- [ ] **Database Migration:** Transition user credentials and audit logs from local JSON/JSONL to **MongoDB** with TTL indexes.
- [ ] **JWT Bearer Authentication:** Add signed access tokens to validate requests between the UI and API.
- [ ] **Automated IP Banning:** Automatic temporary firewall/IP table rule injection upon reaching `CRITICAL` status.
- [ ] **Multi-Model Support:** Plug-and-play adapter layer for LLMs and deep learning embeddings defense.