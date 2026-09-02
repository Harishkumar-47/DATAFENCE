import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "datafence_auth.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def init_auth_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            token_hash TEXT NOT NULL UNIQUE,

            created_at TEXT NOT NULL,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE

        )
        """
    )

    connection.commit()

    connection.close()


# --------------------------------------------------
# PASSWORD HASHING
# --------------------------------------------------

def hash_password(password: str) -> str:

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        120_000,
    )

    return (
        salt.hex()
        + ":"
        + password_hash.hex()
    )


def verify_password(
    password: str,
    stored_hash: str
) -> bool:

    try:

        salt_hex, hash_hex = stored_hash.split(":")

        salt = bytes.fromhex(salt_hex)

        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            120_000,
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    except Exception:

        return False


# --------------------------------------------------
# USERS
# --------------------------------------------------

def create_user(
    name: str,
    email: str,
    password: str,
):

    connection = get_connection()

    cursor = connection.cursor()

    password_hash = hash_password(password)

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
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

        connection.commit()

        user_id = cursor.lastrowid

        return {
            "id": user_id,
            "name": name,
            "email": email,
            "created_at": created_at,
        }

    finally:

        connection.close()


def get_user_by_email(email: str):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,),
    )

    user = cursor.fetchone()

    connection.close()

    return user


def get_user_by_id(user_id: int):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    )

    user = cursor.fetchone()

    connection.close()

    return user


# --------------------------------------------------
# SESSIONS
# --------------------------------------------------

def create_session(user_id: int):

    raw_token = secrets.token_urlsafe(48)

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO sessions
        (
            user_id,
            token_hash,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            token_hash,
            created_at,
        ),
    )

    connection.commit()

    connection.close()

    return raw_token


def get_user_from_token(token: str):

    if not token:
        return None

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            users.id,
            users.name,
            users.email,
            users.created_at

        FROM sessions

        INNER JOIN users
            ON users.id = sessions.user_id

        WHERE sessions.token_hash = ?
        """,
        (token_hash,),
    )

    user = cursor.fetchone()

    connection.close()

    return user


def delete_session(token: str):

    if not token:
        return

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM sessions
        WHERE token_hash = ?
        """,
        (token_hash,),
    )

    connection.commit()

    connection.close()