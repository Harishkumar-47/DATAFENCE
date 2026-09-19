"""Authentication endpoints backed by expiring, hashed opaque sessions."""

import hashlib
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.rate_limit import RateLimiter

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
BACKEND_DIR = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("DATAFENCE_DB_PATH", str(BACKEND_DIR / "datafence.db")))
SESSION_HOURS = max(1, int(os.getenv("SESSION_HOURS", "24")))
auth_limiter = RateLimiter(limit=10, window_seconds=60)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        columns = {row["name"] for row in db.execute("PRAGMA table_info(sessions)").fetchall()}
        expected = {"id", "token_hash", "user_id", "created_at", "expires_at"}
        if columns and not expected.issubset(columns):
            # Invalidate legacy sessions, which stored raw tokens and never expired.
            db.execute("DROP TABLE sessions")
        db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
        db.execute("DELETE FROM sessions WHERE expires_at <= ?", (utc_now().isoformat(),))
        db.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                scanned_at TEXT NOT NULL,
                security_score INTEGER NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                breach_status TEXT NOT NULL,
                breach_count INTEGER NOT NULL,
                discovery_status TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_user ON scan_history(user_id, scanned_at DESC)")
        db.execute("""
            CREATE TABLE IF NOT EXISTS remediation_status (
                user_id INTEGER NOT NULL,
                action_id TEXT NOT NULL,
                resolved INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                PRIMARY KEY(user_id, action_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)


init_db()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        if "$" in encoded:
            algorithm, rounds, salt_hex, digest_hex = encoded.split("$")
            if algorithm != "pbkdf2_sha256":
                return False
        else:  # Read the previous format during migration.
            salt_hex, digest_hex = encoded.split(":")
            rounds = "200000"
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds)
        )
        return secrets.compare_digest(actual, bytes.fromhex(digest_hex))
    except (ValueError, TypeError):
        return False


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(user_id: int, db: sqlite3.Connection) -> tuple[str, str]:
    raw_token = secrets.token_urlsafe(48)
    created_at = utc_now()
    expires_at = created_at + timedelta(hours=SESSION_HOURS)
    db.execute(
        "INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token_hash(raw_token), user_id, created_at.isoformat(), expires_at.isoformat()),
    )
    return raw_token, expires_at.isoformat()


class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=256)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


def bearer_token(authorization: str | None) -> str:
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="Authentication required")
    return token.strip()


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    token = bearer_token(authorization)
    now = utc_now().isoformat()
    with get_db() as db:
        user = db.execute("""
            SELECT users.id, users.name, users.email, users.created_at
            FROM sessions JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = ? AND sessions.expires_at > ?
        """, (token_hash(token), now)).fetchone()
        if not user:
            db.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash(token),))
            raise HTTPException(status_code=401, detail="Session expired or invalid")
        return dict(user)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, request: Request):
    auth_limiter.check(request)
    name = " ".join(payload.name.split())
    email = str(payload.email).lower()
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Name must contain at least 2 characters")
    with get_db() as db:
        try:
            cursor = db.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name, email, hash_password(payload.password), utc_now().isoformat()),
            )
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
        user_id = cursor.lastrowid
        token, expires_at = create_session(user_id, db)
    return {
        "status": "ACCOUNT_CREATED", "token": token, "expires_at": expires_at,
        "user": {"id": user_id, "name": name, "email": email},
    }


@router.post("/login")
def login(payload: LoginRequest, request: Request):
    auth_limiter.check(request)
    email = str(payload.email).lower()
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token, expires_at = create_session(user["id"], db)
        return {
            "status": "LOGIN_SUCCESS", "token": token, "expires_at": expires_at,
            "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
        }


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"status": "AUTHENTICATED", "user": current_user}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(authorization: str | None = Header(default=None)):
    token = bearer_token(authorization)
    with get_db() as db:
        db.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash(token),))
