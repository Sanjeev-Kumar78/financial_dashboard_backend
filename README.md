# Finance Dashboard API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com)
[![Security](https://img.shields.io/badge/Security-Argon2-green.svg)](https://github.com/P-H-C/phc-winner-argon2)

A highly secure, production-ready financial records management backend engineered for scale. Built top-to-bottom with **FastAPI**, **SQLAlchemy 2.0 ORM**, and seamlessly orchestrated for **PostgreSQL** via Docker.

## Core Features

*   **Bank-Grade Security:** Replaces legacy bcrypt with OWASP-recommended **Argon2** (`argon2-cffi`) for GPU-resistant, memory-hard password hashing. 
*   **Impenetrable Object Reference (IDOR) & Mass-Assignment Defenses:** Enforces strict role-based vertical traversal and horizontally blocks param pollution inside update payloads via immutability checks.
*   **Dual-Dialect SQLAlchemy ORM:** Entirely raw-SQL free. All aggregation logic securely builds cross-dialect ASTs natively executing SQLite locally and shifting to PostgreSQL's `FILTER` aggregates in production without touching python logic.
*   **True Multiprocessing (Gunicorn-Ready):** 100% server stateless. Combines cryptographically verified JWT bearer tokens with robust SQLAlchemy DB connection pooling so multiple workers can scale horizontally without sync drift.

---
> [!TIP]
> **Before testing, you must read the [Request/Response Examples](#requestresponse-examples).**

### 1. Launch with Docker Compose (Full Stack)

The easiest way to run the entire backend is via Docker. This will simultaneously build the Python API container and spin up a dedicated PostgreSQL 16 container, perfectly networked together.

```bash
docker compose up --build -d
```

This starts:
- **Finance API**: `http://localhost:8000`
- **PostgreSQL Database**: Port `5432` with credentials `financeuser` / `financepass`

*If you use this method, you can skip steps 2, 3, 4, and 5 and jump straight to the OpenAPI docs on port 8000!*

### 2. Install Dependencies

```bash
pip install fastapi "uvicorn[standard]" "sqlalchemy>=2.0" psycopg2-binary alembic \
    pydantic-settings "python-jose[cryptography]" passlib argon2-cffi email-validator httpx pytest
```

### 3. Configure Environment

```bash
cp .env.example .env
```
By default, the application runs on **SQLite** for rapid local testing. To switch entirely to **PostgreSQL** for production, simply edit the `.env` file:
```ini
# Comment out SQLite
# DATABASE_URL=sqlite:///./financedb.sqlite

# Uncomment PostgreSQL
DATABASE_URL=postgresql://financeuser:financepass@localhost:5432/financedb
```
The codebase uses pure SQLAlchemy ORM, meaning the backend perfectly natively adapts generated SQL without requiring *zero* code changes.

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload
```

### 6. Open API Docs

Browse to **http://localhost:8000/docs** for interactive Swagger UI.

---

## API Routes

### Open (no auth)

| Method | Route              | Description                |
|--------|--------------------|----------------------------|
| GET    | `/health`          | Liveness check             |
| POST   | `/auth/register`   | Create a new user account  |
| POST   | `/auth/login`      | Get a JWT access token     |

### Protected — Users (Admin only)

| Method | Route                    | Description              |
|--------|--------------------------|--------------------------|
| GET    | `/users/`                | List all users           |
| PATCH  | `/users/{id}/role`       | Change a user's role     |
| PATCH  | `/users/{id}/status`     | Activate/deactivate user |

### Protected — Transactions

| Method | Route                  | Roles Allowed        | Description                      |
|--------|------------------------|----------------------|----------------------------------|
| POST   | `/transactions/`       | admin, analyst       | Create a record                  |
| GET    | `/transactions/`       | admin, analyst, viewer | List with filters + pagination |
| GET    | `/transactions/{id}`   | admin, analyst, viewer | Get single record              |
| PATCH  | `/transactions/{id}`   | admin, analyst       | Update fields                    |
| DELETE | `/transactions/{id}`   | admin                | Soft-delete                      |

**Query parameters for `GET /transactions/`:**
- `type` — `income` or `expense`
- `category` — one of: salary, freelance, investment, food, transport, utilities, healthcare, education, rent, other
- `date_from` / `date_to` — ISO date (e.g. `2024-01-01`)
- `page` (default 1), `page_size` (default 20, max 100)

### Protected — Dashboard (all authenticated roles)

| Method | Route                    | Description                          |
|--------|--------------------------|--------------------------------------|
| GET    | `/dashboard/summary`     | Total income, expense, net balance   |
| GET    | `/dashboard/by-category` | Grouped totals per category          |
| GET    | `/dashboard/trends`      | Monthly income vs expense breakdown  |
| GET    | `/dashboard/recent`      | Last N transactions                  |

---

## Request/Response Examples
> [!IMPORTANT]
> Test credentials already created:
> john@example.com : viewer
> john1@example.com : admin
> john2@example.com : analyst

### Register
```json
// POST /auth/register
{ "email": "john@example.com", "password": "securePassword123" }

// Response 201
{ "id": 1, "email": "john@example.com", "role": "viewer", "is_active": true }
```

### Login
```json
// POST /auth/login 
// Note: Accepts `application/x-www-form-urlencoded` standard OAuth2 form-data
// This integrates natively with the FastAPI Swagger UI "Authorize" button!
{ "username": "john@example.com", "password": "securePassword123" }

// Response 200
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

### Create Transaction
```json
// POST /transactions/  (Authorization: Bearer <token>)
{
  "amount": "2500.00",
  "type": "income",
  "category": "salary",
  "date": "2024-06-15",
  "notes": "Monthly salary for June"
}

// Response 201
{
  "id": 1, "amount": "2500.00", "type": "income",
  "category": "salary", "date": "2024-06-15",
  "notes": "Monthly salary for June", "user_id": 1
}
```

### Dashboard Summary
```json
// GET /dashboard/summary
{
  "total_income": "15000.00",
  "total_expense": "8500.00",
  "net_balance": "6500.00"
}
```

### Error Responses (uniform shape)
```json
// 403 Forbidden
{ "error": "FORBIDDEN", "detail": "Role 'viewer' is not permitted to perform this action" }

// 422 Validation Error
{ "error": "VALIDATION_ERROR", "detail": [ ... ] }
```

---

## Seeding an Admin User

New users get the `viewer` role by default. To create an admin for testing:

1. Promote in the DB:
   ```sql
   UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
   ```

---

## Architecture Decisions

| Decision | Why |
|---|---|
| **SQLAlchemy 2.0 ORM** | Pure ORM aggregation (`func.sum`, `case()`) removes all SQL strings, completely avoiding SQL-injection vulnerabilities, while natively generating perfect cross-dialect aggregates for both SQLite and PostgreSQL. |
| **Worker safe multiprocessing** | State is entirely managed statelessly via JWT signatures and precise connection pooling. You can confidently deploy this logic via Gunicorn with multiple Python workers without sync mismatches. |
| **Argon2** over legacy bcrypt | Utilizes `argon2-cffi` by default; it is currently the OWASP gold standard over bcrypt since it natively resists GPU brute forcing operations. |
| **Sync psycopg2** over async | Async SQLAlchemy adds session complexity with no meaningful throughput gain at this scale. Sync is simpler to read, test, and debug. |
| **`require_role()` factory** | Authorization is declared at the route level, readable at a glance — not buried in middleware. |
| **Soft delete** | Financial records are never permanently removed. `is_deleted=True` hides them without destroying audit history. |
| **Category as Enum** | Keeps the DB consistent and makes aggregation queries trivial. Trade-off: adding a category needs a code change + migration. |

## Assumptions

- All users start as `viewer` — an admin must explicitly elevate roles
- Dashboard queries scope to the user's own data unless the caller is an `admin`
- Transaction dates cannot be in the future (Pydantic validator)
- Amounts must be positive — direction is conveyed by the `type` field (income/expense)

---

## Running Tests

```bash
pytest -v
```

Tests use an **in-memory SQLite database** for full isolation from the dev/prod DB.
