import os
from functools import wraps

import requests
from flask import g, jsonify, request
from app.helpers import api_response

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def _supabase_headers(include_auth_token: str | None = None):
    headers = {
        "Content-Type": "application/json",
    }
    if SUPABASE_KEY:
        headers["apikey"] = SUPABASE_KEY
    if include_auth_token:
        headers["Authorization"] = f"Bearer {include_auth_token}"
    return headers


def get_current_user_from_token(token: str):
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL environment variable is required")

    response = requests.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers=_supabase_headers(include_auth_token=token),
        timeout=5,
    )
    if response.status_code != 200:
        return None
    return response.json()


def login_with_email_password(email: str, password: str):
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL environment variable is required")

    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers=_supabase_headers(),
        json={"email": email, "password": password},
        timeout=10,
    )

    if response.status_code != 200:
        try:
            body = response.json()
        except ValueError:
            body = {}
        message = (
            body.get("error_description")
            or body.get("msg")
            or body.get("error")
            or "Sikertelen bejelentkezés"
        )
        return False, None, message

    body = response.json()
    auth_data = {
        "access_token": body.get("access_token"),
        "refresh_token": body.get("refresh_token"),
        "expires_in": body.get("expires_in"),
        "token_type": body.get("token_type"),
        "user": body.get("user"),
    }
    return True, auth_data, "Sikeres bejelentkezés"


def logout_with_token(token: str):
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL environment variable is required")

    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/logout",
        headers=_supabase_headers(include_auth_token=token),
        timeout=10,
    )

    if response.status_code in (200, 204):
        return True, "Sikeres kijelentkezés"
    return False, "Sikertelen kijelentkezés"


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
