"""Compatibility exports for the auth service layer."""

from app.services.auth_service import get_current_user_from_token, require_auth

__all__ = ["require_auth", "get_current_user_from_token"]