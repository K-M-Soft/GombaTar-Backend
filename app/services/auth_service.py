import os
from functools import wraps

import requests
from flask import jsonify, request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")


def get_current_user_from_token(token: str):
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL environment variable is required")

    response = requests.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    if response.status_code != 200:
        return None
    return response.json()


def require_auth(handler):
    @wraps(handler)
    def decorated(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"detail": "Unauthorized"}), 401

        user = get_current_user_from_token(parts[1])
        if not user:
            return jsonify({"detail": "Invalid or expired token"}), 401

        request.user = user
        return handler(*args, **kwargs)

    return decorated
