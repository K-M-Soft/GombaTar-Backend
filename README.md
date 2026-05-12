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
