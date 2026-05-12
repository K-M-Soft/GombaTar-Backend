from flask import Blueprint, request

from app.repositories import check_database_connection
from app.services import require_auth

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
    return {"user": getattr(request, "user", None)}
