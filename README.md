# DATAFENCE

DATAFENCE is a personal security dashboard that checks the authenticated account email against a breach-data provider, calculates explainable risk indicators, and produces practical remediation guidance.

Scan summaries and remediation progress are saved per account, enabling users to track security posture over time. Results can be exported as a readable text report or structured JSON.

It distinguishes verified provider results from unavailable services. Phone lookup is limited to public numbering-plan metadata; it does not claim to trace a device, enumerate SIM cards, or discover linked applications.

## Security model

- Signup and login are separate; login never creates an account.
- Analysis is scoped to the signed-in account email. Arbitrary email targets are rejected.
- Passwords use salted PBKDF2-SHA256 with 310,000 iterations.
- Opaque sessions expire and only SHA-256 token hashes are stored server-side.
- Authentication and analysis endpoints have in-process rate limits.
- CORS is restricted through `CORS_ORIGINS`.
- Account discovery is disabled by default and must be explicitly enabled.
- Scan history stores scores and provider statuses, not raw third-party response bodies.

For an internet-facing deployment, add email ownership verification, TLS at the edge, a shared Redis-backed rate limiter, managed backups, and privacy/legal review before enabling account discovery.

## Stack

- React 19 and Vite
- FastAPI and Pydantic
- SQLite for users and sessions
- XposedOrNot for breach lookup
- `phonenumbers` for optional offline numbering metadata
- Docker Compose for local development

## Run with Docker

```bash
docker compose up --build
```

Open <http://localhost:5173>. API documentation is at <http://localhost:8000/docs> and health status at <http://localhost:8000/health>.

The default Compose configuration stores the database under `backend/data/`, restricts browser access to `http://localhost:5173`, and leaves account discovery disabled.

## Run locally

Backend:

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
DATAFENCE_DB_PATH=/tmp/datafence-dev.db .venv/bin/uvicorn app.main:app --app-dir backend --reload
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

## Verification

```bash
.venv/bin/pytest -q backend/tests
cd frontend && npm run lint && npm run build
```

Tests cover session hashing and revocation, rejection of unknown logins, scan ownership boundaries, history and remediation persistence, domain sanitization, and external-provider failure handling.

## Configuration

See [.env.example](.env.example).

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATAFENCE_DB_PATH` | `backend/datafence.db` | SQLite database path |
| `SESSION_HOURS` | `24` | Session lifetime |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed browser origins |
| `ENABLE_ACCOUNT_DISCOVERY` | `false` | Enables Holehe for the signed-in email |

## Limitations

- “No breach reported” is not proof that an account has never been compromised.
- External data services have their own availability and privacy terms.
- Risk scores are heuristic prioritization aids, not guarantees or professional security advice.
- Rate limiting is process-local and should be replaced for multi-worker deployments.
