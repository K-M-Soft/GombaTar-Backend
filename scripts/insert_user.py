import base64
import hashlib
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Requested default credentials.
USERNAME = ""
PLAINTEXT_PASSWORD = ""
EMAIL = ""
ITERATIONS = 120_000


def hash_password(password: str, iterations: int = ITERATIONS) -> str:
    """
    Create a PBKDF2-HMAC-SHA256 hash string in this format:
    pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
    """
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return (
        f"pbkdf2_sha256${iterations}$"
        f"{base64.b64encode(salt).decode('ascii')}$"
        f"{base64.b64encode(digest).decode('ascii')}"
    )


def verify_hash_format(hash_value: str) -> bool:
    parts = hash_value.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    if not parts[1].isdigit():
        return False
    try:
        base64.b64decode(parts[2], validate=True)
        base64.b64decode(parts[3], validate=True)
    except Exception:
        return False
    return True


def upsert_user() -> None:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env", override=True)
    password_hash = hash_password(PLAINTEXT_PASSWORD)

    if not verify_hash_format(password_hash):
        raise RuntimeError("Generated password hash is invalid")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    engine = create_engine(database_url, pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO users (email, password_hash, display_name)
                VALUES (:email, :password_hash, :display_name)
                ON CONFLICT (email)
                DO UPDATE SET
                    password_hash = EXCLUDED.password_hash,
                    display_name = EXCLUDED.display_name
                """
            ),
            {
                "email": EMAIL,
                "password_hash": password_hash,
                "display_name": USERNAME,
            },
        )

    print("User inserted/updated successfully")
    print(f"email={EMAIL}")
    print(f"display_name={USERNAME}")


if __name__ == "__main__":
    upsert_user()
