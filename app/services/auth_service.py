import os
import base64
import hashlib
import hmac
from functools import wraps

from flask import g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import text

from app.helpers import api_response
from app.repositories import get_engine

TOKEN_MAX_AGE_SECONDS = int(os.environ.get("AUTH_TOKEN_MAX_AGE_SECONDS", "2592000"))
AUTH_TOKEN_SALT = "gombatar-auth-token-v1"


def _get_serializer() -> URLSafeTimedSerializer:
    secret = (
        os.environ.get("AUTH_TOKEN_SECRET")
        or os.environ.get("SECRET_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not secret:
        raise RuntimeError("AUTH_TOKEN_SECRET or SECRET_KEY is required")
    return URLSafeTimedSerializer(secret_key=secret)


def _create_access_token(user: dict) -> str:
    serializer = _get_serializer()
    payload = {
        "sub": str(user.get("id")),
        "email": user.get("email"),
        "display_name": user.get("display_name"),
    }
    return serializer.dumps(payload, salt=AUTH_TOKEN_SALT)


def _parse_pbkdf2_hash(hash_value: str):
    parts = (hash_value or "").split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return None
    if not parts[1].isdigit():
        return None
    try:
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2], validate=True)
        expected = base64.b64decode(parts[3], validate=True)
    except (ValueError, TypeError):
        return None
    return iterations, salt, expected


def _verify_password(password: str, stored_hash: str) -> bool:
    parsed = _parse_pbkdf2_hash(stored_hash)
    if not parsed:
        return False

    iterations, salt, expected = parsed
    calculated = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(calculated, expected)


def _get_user_by_email(email: str):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT id, email, password_hash, display_name
                FROM users
                WHERE LOWER(email) = LOWER(:email)
                LIMIT 1
                """
            ),
            {"email": email},
        ).mappings().first()
    return dict(row) if row else None


def get_current_user_from_token(token: str):
    serializer = _get_serializer()
    try:
        payload = serializer.loads(
            token,
            salt=AUTH_TOKEN_SALT,
            max_age=TOKEN_MAX_AGE_SECONDS,
        )
    except (BadSignature, SignatureExpired):
        return None
    return payload


def login_with_email_password(email: str, password: str):
    user = _get_user_by_email(email)
    if not user:
        return False, None, "Helytelen email vagy jelszó"

    if not _verify_password(password, user.get("password_hash", "")):
        return False, None, "Helytelen email vagy jelszó"

    access_token = _create_access_token(user)
    auth_data = {
        "access_token": access_token,
        "refresh_token": None,
        "expires_in": TOKEN_MAX_AGE_SECONDS,
        "token_type": "bearer",
        "user": {
            "id": str(user.get("id")),
            "email": user.get("email"),
            "display_name": user.get("display_name"),
        },
    }
    return True, auth_data, "Sikeres bejelentkezés"


def logout_with_token(token: str):
    if not token:
        return False, "Sikertelen kijelentkezés"
    return True, "Sikeres kijelentkezés"


def require_auth(handler):
    @wraps(handler)
    def decorated(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify(api_response(False, None, "Nincs jogosultság")), 401

        user = get_current_user_from_token(parts[1])
        if not user:
            return jsonify(api_response(False, None, "Érvénytelen vagy lejárt token")), 401

        g.current_user = user
        return handler(*args, **kwargs)

    return decorated
