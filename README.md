# DATAFENCE

## Personal Data Exposure, Inference & Adaptive Security Platform

DATAFENCE is a cybersecurity and privacy intelligence platform designed to help users understand:

- What personal data is exposed
- What can potentially be inferred from that data
- What security risks exist
- How connected services increase the user's blast radius
- How the platform can eventually recommend and execute privacy/security protection actions

DATAFENCE is currently being developed as a modular cybersecurity/privacy platform.

---

# 1. PROJECT STATUS

Current development stage:

## Phase 1 — Foundation + Authentication + Security Intelligence

The following foundation is currently implemented:

- React/Vite frontend
- FastAPI backend
- SQLite authentication database
- User registration
- User login
- User logout
- Session/token authentication
- Protected API endpoints
- Current-user endpoint
- Authentication-aware frontend
- Security analysis pipeline
- Data exposure analysis
- Inference analysis
- Threat analysis
- Blast-radius analysis
- Security score
- Basic protection workflow
- Dashboard visualization

The basic application flow is working.

The next development phase is to make DATAFENCE perform meaningful, evidence-based personal data analysis instead of relying primarily on demonstration/sample data.

---

# 2. CORE IDEA

The central idea of DATAFENCE is:

> "Don't just tell the user that their data is exposed. Show what that data can reveal, how different data points connect, what risks those connections create, and what the user can do about them."

DATAFENCE should eventually move through the following pipeline:

User
    ↓
Data Sources
    ↓
Data Collection / Import
    ↓
Data Normalization
    ↓
Data Discovery
    ↓
Exposure Analysis
    ↓
Cross-Source Correlation
    ↓
Inference Engine
    ↓
Threat Analysis
    ↓
Blast Radius Analysis
    ↓
Risk Scoring
    ↓
Explainable Security Report
    ↓
Protection Recommendations
    ↓
User-approved Remediation

---

# 3. IMPORTANT DEVELOPMENT PRINCIPLE

Do NOT treat DATAFENCE as a simple "email risk checker".

The email address is only an identifier.

The long-term product should analyze multiple categories of personal data and their relationships.

Example:

Email
    +
Location
    +
Search Activity
    +
Purchases
    +
Contacts
    +
Connected Services
    ↓
Potential inferred profile
    ↓
Privacy/security risk

The project should focus on the relationship between data points rather than isolated data points.

---

# 4. TECHNOLOGY STACK

## Frontend

- React
- Vite
- JavaScript
- Lucide React icons
- CSS

Frontend directory:

frontend/

---

## Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLite

Backend directory:

backend/

---

## Authentication

Current authentication implementation uses:

- SQLite
- PBKDF2-HMAC-SHA256 password hashing
- Random session tokens
- Bearer authentication
- Protected FastAPI routes
- Browser localStorage for the frontend session

Authentication database:

backend/datafence.db

IMPORTANT:

`datafence.db` must NOT be committed to Git.

---

# 5. PROJECT STRUCTURE

Current important structure:

DATAFENCE/
│
├── README.md
├── .gitignore
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── analysis.py
│   │   │   └── security.py
│   │   │
│   │   ├── engines/
│   │   │   │
│   │   │   ├── data/
│   │   │   │   ├── data_discovery.py
│   │   │   │   └── data_exposure.py
│   │   │   │
│   │   │   ├── inference/
│   │   │   │   ├── inference_engine.py
│   │   │   │   └── profile_reconstructor.py
│   │   │   │
│   │   │   ├── intelligence/
│   │   │   │   ├── blast_radius.py
│   │   │   │   ├── data_normalizer.py
│   │   │   │   ├── exposure_engine.py
│   │   │   │   ├── inference_engine.py
│   │   │   │   ├── intelligence_pipeline.py
│   │   │   │   └── threat_engine.py
│   │   │   │
│   │   │   ├── lineage/
│   │   │   │   └── __init__.py
│   │   │   │
│   │   │   ├── security/
│   │   │   │   ├── defense_orchestrator.py
│   │   │   │   ├── remediation_engine.py
│   │   │   │   ├── risk_engine.py
│   │   │   │   ├── security_engine.py
│   │   │   │   ├── security_policy.py
│   │   │   │   └── verification_engine.py
│   │   │   │
│   │   │   └── threat/
│   │   │       └── threat_engine.py
│   │   │
│   │   └── models/
│   │       └── data.py
│   │
│   └── venv/
│
└── frontend/
    │
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    │
    └── src/
        ├── App.jsx
        ├── App.css
        ├── index.css
        ├── main.jsx
        │
        ├── pages/
        │   ├── Login.jsx
        │   └── Dashboard.jsx
        │
        └── services/
            └── api.js

---

# 6. BACKEND ENTRY POINT

Main backend file:

backend/app/main.py

The FastAPI application:

- Creates the FastAPI application
- Configures CORS
- Registers authentication routes
- Registers analysis routes
- Registers security routes
- Provides the root endpoint

Backend runs on:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs

---

# 7. FRONTEND ENTRY POINT

Main frontend file:

frontend/src/App.jsx

App.jsx controls authentication state.

The application starts by checking:

localStorage.getItem("datafence_token")

and:

localStorage.getItem("datafence_user")

If a valid local session exists:

    Dashboard

Otherwise:

    Login

The intended flow is:

App
 ↓
Check local session
 ↓
Authenticated?
 ├── YES → Dashboard
 └── NO  → Login

---

# 8. AUTHENTICATION SYSTEM

Authentication is implemented in:

backend/app/api/auth.py

Authentication endpoints:

POST /api/auth/signup

POST /api/auth/login

GET /api/auth/me

POST /api/auth/logout

---

# 9. SIGNUP FLOW

Frontend:

Login.jsx

API service:

frontend/src/services/api.js

Backend:

backend/app/api/auth.py

User provides:

- Name
- Email
- Password

The backend:

1. Validates the name
2. Validates email
3. Requires password >= 8 characters
4. Checks whether the email already exists
5. Generates a random salt
6. Hashes the password using PBKDF2-HMAC-SHA256
7. Stores the user in SQLite
8. Returns the created user

Important:

Passwords must NEVER be stored in plaintext.

---

# 10. LOGIN FLOW

User provides:

- Email
- Password

Backend:

1. Finds the user
2. Verifies the password hash
3. Generates a secure random session token
4. Stores the token in the sessions table
5. Returns the token and user information

Frontend stores:

datafence_token

and:

datafence_user

in localStorage.

---

# 11. PROTECTED ENDPOINTS

Protected endpoints require:

Authorization: Bearer <token>

The backend function:

get_current_user()

validates the token against the SQLite sessions table.

If no valid session exists:

HTTP 401 Unauthorized

must be returned.

This authentication requirement MUST NOT be removed.

---

# 12. CURRENT SECURITY ANALYSIS ENDPOINT

Endpoint:

POST /api/security/full-analysis

Authentication:

REQUIRED

Frontend function:

runFullSecurityAnalysis()

The frontend gets the token from:

localStorage

and sends:

Authorization: Bearer <token>

---

# 13. SECURITY ANALYSIS FLOW

Current flow:

User
 ↓
Authenticated session
 ↓
POST /api/security/full-analysis
 ↓
SecurityRequest
 ↓
User identity
 ↓
Sample data model
 ↓
IntelligencePipeline
 ↓
Exposure
 ↓
Inference
 ↓
Threat
 ↓
Blast Radius
 ↓
SecurityEngine
 ↓
Security Score
 ↓
Dashboard

---

# 14. CURRENT SAMPLE DATA

At the current stage, the security endpoint constructs demonstration data.

Current categories include:

- email
- location
- activity
- purchases
- contacts

Connections currently include:

- email
- contacts
- documents

This is intentional for the foundation/demo phase.

IMPORTANT:

Do not falsely claim that DATAFENCE is currently accessing a user's Gmail, Google account, contacts, browser history, purchases, or private services.

The current implementation does NOT perform live external account collection.

---

# 15. CURRENT DATA ANALYSIS

The project contains multiple engines.

## Data Discovery

File:

backend/app/engines/data/data_discovery.py

Purpose:

Identify and categorize available data points.

---

## Data Exposure

File:

backend/app/engines/data/data_exposure.py

Purpose:

Estimate exposure based on discovered data.

---

## Inference Engine

Files:

backend/app/engines/inference/inference_engine.py

backend/app/engines/intelligence/inference_engine.py

Purpose:

Determine what characteristics or information could potentially be inferred from available data.

---

## Profile Reconstruction

File:

backend/app/engines/inference/profile_reconstructor.py

Purpose:

Construct a high-level inferred profile from inference results.

---

## Threat Engine

File:

backend/app/engines/threat/threat_engine.py

Purpose:

Estimate potential security threats based on exposure and inferred information.

---

## Intelligence Pipeline

File:

backend/app/engines/intelligence/intelligence_pipeline.py

Purpose:

Coordinate:

- normalization
- exposure
- inference
- threat
- blast radius

---

## Blast Radius

File:

backend/app/engines/intelligence/blast_radius.py

Purpose:

Estimate how many connected services or data relationships could increase the impact of compromise/exposure.

---

## Security Engine

File:

backend/app/engines/security/security_engine.py

Purpose:

Combine multiple risk dimensions into an overall security assessment.

Current dimensions include:

- exposure
- inference
- threat
- blast radius

---

# 16. CURRENT DASHBOARD

File:

frontend/src/pages/Dashboard.jsx

The dashboard currently displays:

## Security Score

Shows:

- security score
- risk level
- risk score

---

## Data Exposure

Shows:

- exposure score
- number of data points

---

## Inference Risk

Shows:

- inference score
- inferred profiles/findings

---

## Threat Level

Shows:

- threat score
- threat level

---

## Blast Radius

Shows:

- blast radius score
- connected services

---

## Inference Findings

Displays:

- inferred characteristic
- source categories
- severity

---

# 17. PROTECTION SYSTEM

Current frontend action:

PROTECT ME

Current implementation is a placeholder response.

It currently returns:

PROTECTION_READY

with:

successful: 0

pending: 0

This is NOT yet a complete real-world remediation system.

Future versions should connect this to:

- remediation engine
- verification engine
- defense orchestrator
- security policies

---

# 18. FRONTEND API SERVICE

File:

frontend/src/services/api.js

API base:

http://127.0.0.1:8000

Important functions:

signup()

login()

getCurrentUser()

runAnalysis()

runFullSecurityAnalysis()

activateProtection()

Authentication token is retrieved using:

getToken()

---

# 19. CURRENT API CONTRACT

## Signup

POST:

/api/auth/signup

Request:

{
    "name": "Jai Krishna",
    "email": "user@example.com",
    "password": "password123"
}

---

## Login

POST:

/api/auth/login

Request:

{
    "email": "user@example.com",
    "password": "password123"
}

Response contains:

{
    "token": "...",
    "user": {
        "id": 1,
        "name": "...",
        "email": "..."
    }
}

---

## Current User

GET:

/api/auth/me

Header:

Authorization: Bearer <token>

---

## Full Security Analysis

POST:

/api/security/full-analysis

Header:

Authorization: Bearer <token>

No email should be manually entered by the user for this request.

The backend should obtain the identity from the authenticated session.

---

# 20. SECURITY REQUIREMENTS

These rules are extremely important.

## Authentication

Never allow:

POST /api/security/full-analysis

without authentication.

---

## Passwords

Never store plaintext passwords.

---

## Tokens

Never expose session tokens in UI.

---

## Database

Do not commit:

datafence.db

---

## Secrets

Never commit:

.env

API keys

OAuth secrets

access tokens

private keys

passwords

---

## User Data

Do not fabricate claims that external accounts were accessed.

If external integrations are not implemented, clearly identify the data as:

- sample data
- imported data
- user-provided data
- simulated data

---

# 21. CORS

Current allowed frontend origins:

http://localhost:5173

http://127.0.0.1:5173

Backend CORS is configured in:

backend/app/main.py

---

# 22. RUNNING LOCALLY

## Backend

Open CMD:

cd C:\Users\jaikr\DATAFENCE\backend

Activate environment:

venv\Scripts\activate

Run:

python -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

---

## Frontend

Open another CMD:

cd C:\Users\jaikr\DATAFENCE\frontend

Run:

npm run dev

Frontend:

http://localhost:5173

---

# 23. DEVELOPMENT RULES FOR AI ASSISTANTS

When another AI model is asked to modify DATAFENCE, it MUST follow these rules.

## Rule 1 — Understand before modifying

Inspect the relevant existing files before proposing replacement code.

Do not blindly overwrite the entire project.

---

## Rule 2 — Preserve working authentication

Do not remove:

- signup
- login
- logout
- sessions
- bearer authentication
- get_current_user()
- protected analysis endpoints

---

## Rule 3 — Preserve working dashboard flow

Current flow:

Login
 ↓
Dashboard
 ↓
Analyze
 ↓
Security Analysis
 ↓
Results

Do not break this flow while adding new functionality.

---

## Rule 4 — Avoid fake integrations

Do not claim DATAFENCE has access to:

Gmail

Google Drive

WhatsApp

Instagram

banking accounts

browser history

contacts

shopping accounts

unless a real integration has been implemented.

---

## Rule 5 — Build modularly

New functionality should preferably be added as:

API module
+
Engine
+
Service
+
Frontend component/page

rather than putting everything into one large file.

---

## Rule 6 — Keep the architecture understandable

Avoid unnecessary dependencies.

Avoid unnecessary frameworks.

Avoid introducing complex infrastructure unless required.

---

## Rule 7 — Explain security implications

Any feature involving personal data must consider:

- authentication
- authorization
- data minimization
- encryption
- privacy
- consent
- secure storage
- auditability

---

# 24. NEXT DEVELOPMENT PHASE

The next major phase should move DATAFENCE from:

"Demo security analysis"

to:

"Evidence-based personal data intelligence."

The planned architecture is:

User
 ↓
Data Import
 ↓
Data Normalization
 ↓
Data Classification
 ↓
Data Lineage
 ↓
Cross-Source Correlation
 ↓
Inference Graph
 ↓
Risk Engine
 ↓
Explainable Report
 ↓
Protection Recommendations

---

# 25. PLANNED DATA SOURCES

Future data sources may include:

## User-uploaded data

Examples:

- JSON
- CSV
- exported account data
- browser export
- application export

---

## Optional integrations

Potential future integrations:

- Google account exports
- GitHub account data
- social platform exports
- cloud storage exports
- browser history exports

These should require explicit user consent.

---

# 26. DATA NORMALIZATION

Different sources should be converted into a common internal structure.

Example:

{
    "source": "github",
    "category": "identity",
    "type": "email",
    "value": "user@example.com",
    "timestamp": "...",
    "confidence": 0.98
}

This allows different sources to be analyzed consistently.

---

# 27. DATA LINEAGE

Future DATAFENCE versions should track:

WHERE the data came from.

WHAT data was used.

WHAT inference was produced.

WHY the inference was produced.

HOW confident the system is.

Example:

GitHub email
    ↓
Identity linkage
    ↓
Public account association
    ↓
Potential professional profile
    ↓
Inference confidence: 0.91

This makes the system explainable.

---

# 28. INFERENCE GRAPH

A major future feature is an inference graph.

Example:

Email
   │
   ├── GitHub
   │
   ├── Shopping account
   │
   └── Social account
          │
          ↓
      Interest profile
          │
          ↓
   Behavioral inference
          │
          ↓
    Privacy risk

The system should explain relationships rather than only showing scores.

---

# 29. EXPLAINABLE RISK

Instead of:

"Risk = 78"

DATAFENCE should eventually explain:

Risk Score: 78/100

Why:

- 4 exposed identity attributes
- 3 linked services
- 2 high-confidence inferred attributes
- 1 reusable identifier
- multiple cross-source relationships

This makes the result understandable to normal users and judges.

---

# 30. FUTURE SECURITY SCORE

Potential scoring model:

Overall Risk =
    Exposure Risk
    +
    Inference Risk
    +
    Threat Risk
    +
    Blast Radius
    +
    Correlation Risk

The exact formula should be validated and documented before implementation.

Do not claim scientific accuracy without evidence.

---

# 31. FUTURE PROTECTION ENGINE

Future protection should NOT automatically perform destructive actions.

Preferred model:

Detect
 ↓
Explain
 ↓
Recommend
 ↓
Ask user approval
 ↓
Execute
 ↓
Verify
 ↓
Record result

Example:

"Your email is publicly exposed on Service X."

Recommended action:

"Review account privacy settings."

User:

[Approve]

Then DATAFENCE performs the supported remediation.

---

# 32. AUDIT TRAIL

Future versions should maintain an audit trail.

Example:

{
    "timestamp": "...",
    "action": "ANALYSIS_RUN",
    "user_id": 12,
    "source": "uploaded_export",
    "result": "completed"
}

For remediation:

{
    "timestamp": "...",
    "action": "REMEDIATION",
    "target": "service",
    "status": "approved"
}

---

# 33. PRIVACY PRINCIPLES

DATAFENCE should follow:

## Data minimization

Only collect what is required.

## User consent

External data access must require explicit consent.

## Transparency

Explain why information was analyzed.

## Explainability

Show why a risk or inference was generated.

## Security

Protect stored data and credentials.

## User control

Users should be able to remove their imported data.

---

# 34. CURRENT LIMITATIONS

The current version is NOT yet a complete privacy protection platform.

Known limitations:

1. Security analysis currently uses sample/demo data.
2. External account integrations are not implemented.
3. Protection/remediation is currently a placeholder.
4. No complete data-import subsystem exists yet.
5. No complete inference graph UI exists yet.
6. No production-grade deployment architecture exists yet.
7. SQLite is currently used for local development.
8. Session management is currently basic.
9. The current security score is an application-level heuristic, not a certified security metric.

These limitations should NOT be hidden.

They represent the next development targets.

---

# 35. DEVELOPMENT ROADMAP

## Phase 1 — Foundation

COMPLETED / WORKING

- FastAPI backend
- React frontend
- Authentication
- SQLite
- Dashboard
- Security analysis pipeline
- Exposure analysis
- Inference analysis
- Threat analysis
- Blast radius
- Security scoring

---

## Phase 2 — Real Data Input

NEXT

- Upload data
- JSON support
- CSV support
- Data validation
- Data normalization
- Data classification
- User-owned datasets
- Dataset management

---

## Phase 3 — Data Lineage

- Source tracking
- Data provenance
- Relationship tracking
- Evidence storage
- Confidence scores

---

## Phase 4 — Advanced Inference

- Cross-source correlation
- Identity linking
- Behavioral inference
- Interest inference
- Relationship inference
- Inference graph

---

## Phase 5 — Advanced Threat Intelligence

- Threat modeling
- Attack-path analysis
- Correlation risk
- Credential reuse risk
- Account takeover indicators
- Blast-radius visualization

---

## Phase 6 — Protection

- Privacy recommendations
- User approval
- Remediation engine
- Verification engine
- Defense orchestration
- Audit logs

---

## Phase 7 — Production

- PostgreSQL
- secure secret management
- HTTPS
- proper session lifecycle
- rate limiting
- logging
- monitoring
- deployment
- automated testing

---

# 36. TESTING CHECKLIST

Every major modification should verify:

## Authentication

[ ] Signup works

[ ] Duplicate email rejected

[ ] Password validation works

[ ] Login works

[ ] Incorrect password rejected

[ ] Logout works

[ ] Session token required

[ ] Invalid token rejected

---

## Dashboard

[ ] Dashboard only accessible after authentication

[ ] Username displayed

[ ] Email displayed where appropriate

[ ] Logout available

[ ] Analyze button works

[ ] Analysis results render

[ ] Protection button works

---

## Backend

[ ] FastAPI starts

[ ] /docs works

[ ] Authentication endpoints work

[ ] Protected endpoints return 401 without authentication

[ ] Valid authenticated requests return 200

---

# 37. IMPORTANT CURRENT API BEHAVIOR

Unauthenticated:

POST /api/security/full-analysis

must return:

401 Unauthorized

Authenticated request:

POST /api/security/full-analysis

should return:

200 OK

with:

status

identity

intelligence

security

---

# 38. AI TASK INSTRUCTIONS

If you are an AI assistant working on DATAFENCE:

1. Read this README first.
2. Identify the current phase.
3. Inspect the existing relevant source files.
4. Understand dependencies between modules.
5. Do not break authentication.
6. Do not remove working functionality.
7. Do not invent integrations.
8. Implement changes incrementally.
9. Provide exact file paths.
10. Provide complete code when replacement is required.
11. Mention any new dependencies.
12. Mention database/schema changes.
13. Provide commands to test the changes.
14. Check both backend and frontend compatibility.
15. Preserve the existing API contract unless there is a strong reason to change it.
16. If changing an API contract, update both backend and frontend.
17. Prefer secure defaults.
18. Never expose credentials or secrets.
19. Never claim sample data is real user data.
20. Explain what is implemented versus simulated.

---

# 39. DEFINITION OF DONE

A feature is considered complete only when:

- Backend implementation exists
- Frontend integration exists if required
- Authentication/authorization is respected
- Errors are handled
- Existing functionality still works
- The feature is testable locally
- No secrets are committed
- Documentation is updated
- The feature's limitations are clearly stated

---

# 40. PROJECT VISION

DATAFENCE should ultimately become:

> An explainable personal data security intelligence platform that maps what information a person exposes, discovers what can be inferred from the relationships between those data points, measures the resulting security and privacy risk, and helps the user reduce that risk with transparent, consent-based protection actions.

The key differentiator should be:

DATA → RELATIONSHIPS → INFERENCES → RISK → EXPLANATION → ACTION

not simply:

EMAIL → SCORE

---

# END OF DATAFENCE README