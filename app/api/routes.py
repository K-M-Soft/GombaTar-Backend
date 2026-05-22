from datetime import datetime, timezone

from flask import Blueprint, g, request

from app.helpers import api_response
from app.helpers.datetime import parse_since
from app.repositories import check_database_connection
from app.services import login_with_email_password, logout_with_token, require_auth
from app.services.sync_service import get_mushrooms_delta_service

api_bp = Blueprint("api", __name__)


@api_bp.get("/")
def index():
    return {"message": "GombaTar Backend API"}


@api_bp.get("/health")
def health():
    return {"status": "ok"}


@api_bp.get("/health/db")
def health_db():
    check_database_connection()
    return {"status": "ok", "database": "reachable"}


@api_bp.get("/auth/me")
@require_auth
def me():
    return api_response(True, {"user": getattr(g, "current_user", None)}, None)


@api_bp.post("/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    email = str(body.get("email", "")).strip()
    password = str(body.get("password", ""))

    if not email or not password:
        return api_response(False, None, "Email és jelszó kötelező"), 400

    ok, data, message = login_with_email_password(email=email, password=password)
    status = 200 if ok else 401
    return api_response(ok, data, message), status


@api_bp.post("/auth/logout")
@require_auth
def logout():
    authorization = request.headers.get("Authorization", "")
    token = authorization.split()[1]

    ok, message = logout_with_token(token)
    status = 200 if ok else 400
    return api_response(ok, None, message), status

@api_bp.get("/api/sync")
def sync_mushrooms_delta():
    since_raw = request.args.get("since")
    try:
        since = parse_since(since_raw)
    except ValueError:
        return api_response(False, None, "Invalid since format, expected ISO timestamp"), 400

    mushrooms = get_mushrooms_delta_service(since)
    server_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    data = {
        "server_time": server_time,
        "mushrooms": mushrooms,
    }
    return api_response(True, data, None), 200
