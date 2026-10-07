import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt


SECRET_KEY = os.getenv(
    "INTERVIEWGUARD_SECRET_KEY",
    "interviewguard-development-secret-change-this"
)

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8


def hash_password(password: str) -> str:
    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        120000,
    )

    return (
        salt.hex()
        + ":"
        + password_hash.hex()
    )


def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt_hex, password_hash_hex = stored_password.split(":", 1)

        salt = bytes.fromhex(salt_hex)
        stored_hash = bytes.fromhex(password_hash_hex)

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            120000,
        )

        return hmac.compare_digest(
            calculated_hash,
            stored_hash,
        )

    except Exception:
        return False


def create_access_token(
    user_id: int,
    username: str,
    role: str,
) -> str:

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )