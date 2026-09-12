import hashlib
import secrets
import sqlite3

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)

from pydantic import BaseModel, EmailStr


router = APIRouter(
    prefix="/api/auth",
    tags=["DATAFENCE Authentication"],
)


DB_PATH = "datafence.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():

    db = get_db()

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    db.commit()
    db.close()


init_db()


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password: str) -> str:

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )

    return (
        salt.hex()
        + ":"
        + password_hash.hex()
    )


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:

    try:

        salt_hex, hash_hex = stored_hash.split(":")

        salt = bytes.fromhex(salt_hex)

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000,
        )

        return secrets.compare_digest(
            calculated_hash.hex(),
            hash_hex,
        )

    except Exception:

        return False


# ============================================================
# TOKEN
# ============================================================

def create_session(
    user_id: int,
    db,
):

    token = secrets.token_urlsafe(48)

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    db.execute(
        """
        INSERT INTO sessions (
            token,
            user_id,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            token,
            user_id,
            created_at,
        ),
    )

    return token


# ============================================================
# REQUEST MODELS
# ============================================================

class SignupRequest(BaseModel):

    name: str
    email: str
    password: str


class LoginRequest(BaseModel):

    email: str
    password: str


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    authorization: str | None = Header(
        default=None
    ),
):

    if not authorization:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = authorization[
        len("Bearer "):
    ].strip()

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    db = get_db()

    user = db.execute(
        """
        SELECT
            users.id,
            users.name,
            users.email,
            users.created_at
        FROM sessions
        JOIN users
            ON users.id = sessions.user_id
        WHERE sessions.token = ?
        """,
        (token,),
    ).fetchone()

    db.close()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
        )

    return dict(user)


# ============================================================
# SIGNUP
# ============================================================

@router.post("/signup")
def signup(
    request: SignupRequest,
):

    name = request.name.strip()
    email = str(request.email).lower().strip()
    password = request.password

    # -----------------------------
    # VALIDATION
    # -----------------------------

    if len(name) < 2:

        raise HTTPException(
            status_code=400,
            detail="Name must contain at least 2 characters",
        )

    if len(password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters",
        )

    db = get_db()

    # -----------------------------
    # CHECK EXISTING USER
    # -----------------------------

    existing_user = db.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (email,),
    ).fetchone()

    if existing_user:

        db.close()

        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists",
        )

    # -----------------------------
    # CREATE USER
    # -----------------------------

    password_hash = hash_password(
        password
    )

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    cursor = db.execute(
        """
        INSERT INTO users (
            name,
            email,
            password_hash,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            email,
            password_hash,
            created_at,
        ),
    )

    user_id = cursor.lastrowid

    # -----------------------------
    # CREATE SESSION
    # -----------------------------

    token = create_session(
        user_id,
        db,
    )

    db.commit()
    db.close()

    # -----------------------------
    # RETURN USER + TOKEN
    # -----------------------------

    return {
        "status": "ACCOUNT_CREATED",
        "message": "DATAFENCE account created successfully",
        "token": token,
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
        },
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    request: LoginRequest,
):

    email = str(
        request.email
    ).lower().strip()

    db = get_db()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,),
    ).fetchone()

    if not user:
        # Auto-register if user doesn't exist
        password_hash = hash_password(request.password)
        created_at = datetime.now(timezone.utc).isoformat()
        
        # We don't have a name, so use part of email
        name = email.split('@')[0]
        
        cursor = db.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password_hash, created_at),
        )
        user_id = cursor.lastrowid
        user_name = name
    else:
        if not verify_password(
            request.password,
            user["password_hash"],
        ):
            db.close()
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )
        user_id = user["id"]
        user_name = user["name"]

    # -----------------------------
    # CREATE SESSION
    # -----------------------------

    token = create_session(
        user_id,
        db,
    )

    db.commit()
    db.close()

    return {
        "status": "LOGIN_SUCCESS",
        "token": token,
        "user": {
            "id": user_id,
            "name": user_name,
            "email": email,
        },
    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get("/me")
def me(
    current_user=Depends(
        get_current_user
    ),
):

    return {
        "status": "AUTHENTICATED",
        "user": current_user,
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
def logout(
    authorization: str | None = Header(
        default=None
    ),
):

    if (
        authorization
        and authorization.startswith("Bearer ")
    ):

        token = authorization[
            len("Bearer "):
        ].strip()

        db = get_db()

        db.execute(
            """
            DELETE FROM sessions
            WHERE token = ?
            """,
            (token,),
        )

        db.commit()
        db.close()

    return {
        "status": "LOGOUT_SUCCESS"
    }