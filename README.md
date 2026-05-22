# GombaTar-Backend
https://docs.google.com/document/d/1GbCForetIVo9xyoC23PAxRQnfnfezCke3dJJmW8rGT0/edit?tab=t.0

## Backend baseline (init)

Layered architecture:

- API layer: `app/api/routes.py`
- Business/service layer: `app/services/auth_service.py`
- Data access/repository layer: `app/repositories/database.py`

Entry points:

- App factory: `app/main.py`
- Vercel handler: `api/index.py`

Notes:

- No runtime `CREATE TABLE` is executed by the application.
- Database schema changes should be handled by migrations outside runtime.

## API route lista

| Method | Route | Auth | Payload (JSON body) | Response |
| --- | --- | --- | --- | --- |
| GET | / | Nem | Nincs | 200: `{ "message": "GombaTar Backend API" }` |
| GET | /health | Nem | Nincs | 200: `{ "status": "ok" }` |
| GET | /health/db | Nem | Nincs | 200: `{ "status": "ok", "database": "reachable" }` |
| GET | /auth/me | Igen (Bearer token) | Nincs | 200: `{ "ok": true, "data": { "user": { ... } }, "message": null }` 401: `{ "ok": false, "data": null, "message": "Nincs jogosultság" }` vagy `{ "ok": false, "data": null, "message": "Érvénytelen vagy lejárt token" }` |
| GET | /api/sync | Nem | Query param: `since` (ISO timestamp, pl. `2024-05-18T12:00:00Z`), ha nincs: 1970-01-01T00:00:00Z | 200: `{ "ok": true, "data": { "server_time": "...", "mushrooms": [ { ... } ] }, "message": null }` 400: `{ "ok": false, "data": null, "message": "Invalid since format, expected ISO timestamp" }` |
| POST | /auth/login | Nem | `{ "email": "string", "password": "string" }` | 200: `{ "ok": true, "data": { "access_token": "...", "refresh_token": "...", "expires_in": 3600, "token_type": "bearer", "user": { ... } }, "message": "Sikeres bejelentkezés" }` 400: `{ "ok": false, "data": null, "message": "Email és jelszó kötelező" }` 401: `{ "ok": false, "data": null, "message": "Sikertelen bejelentkezés" }` vagy Supabase hibaüzenet |
| POST | /auth/logout | Igen (Bearer token) | Nincs | 200: `{ "ok": true, "data": null, "message": "Sikeres kijelentkezés" }` 400: `{ "ok": false, "data": null, "message": "Sikertelen kijelentkezés" }` 401: `{ "ok": false, "data": null, "message": "Nincs jogosultság" }` vagy `{ "ok": false, "data": null, "message": "Érvénytelen vagy lejárt token" }` |
