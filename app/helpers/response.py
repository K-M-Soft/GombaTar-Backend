def api_response(ok: bool, data=None, message: str | None = None):
    """Unified API response envelope used by routes and services."""
    return {"ok": ok, "data": data, "message": message}
