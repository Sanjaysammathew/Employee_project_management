# Employee Management API

FastAPI service for managing employees and projects, with PostgreSQL persistence,
JWT-based authentication, and Alembic migrations.

## Technology stack

- Python, FastAPI, and Uvicorn
- Pydantic Settings for environment-based configuration
- SQLAlchemy's async ORM with PostgreSQL and `asyncpg`
- Alembic for database migrations
- Pytest and FastAPI's `TestClient`

## Project structure

```text
project-root/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, lifespan, and router registration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependency/
│   │   │   ├── __init__.py
│   │   │   ├── auth_dependencies.py
│   │   │   └── dependencies.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth_router.py
│   │       ├── employee_router.py
│   │       ├── health_router.py
│   │       └── project_router.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic application and database settings
│   │   └── security.py         # Password hashing and JWT helpers
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py         # SQLAlchemy engine, sessions, Base, and get_db
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── custom_exceptions.py
│   │   └── exception_handler.py # Central HTTP status mapping
│   ├── models/
│   │   ├── __init__.py
│   │   ├── association.py
│   │   ├── employee.py
│   │   ├── projects.py
│   │   └── user.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── implement/
│   │   │   ├── __init__.py
│   │   │   ├── employee_repository.py
│   │   │   ├── project_repository.py
│   │   │   └── user_repository.py
│   │   └── interface/
│   │       ├── __init__.py
│   │       ├── employee_interface.py
│   │       ├── project_interface.py
│   │       └── user_interface.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth_schema.py
│   │   ├── employee_schema.py
│   │   └── project_schema.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── employee_service.py
│   │   └── project_service.py
│   └── utils/
│       ├── __init__.py
│       └── logging_config.py
├── alembic/
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # Existing database migration history
│       ├── 05906637057c_create_employee_tables.py
│       ├── 375daf279dc2_updated_title_in_projects.py
│       ├── 4c1d8a7e2f90_replace_created_at_with_role.py
│       ├── 9a4b2c7d1e6f_create_users_table.py
│       ├── 9bcc1e7fc2a1_added_column_credits_in_projects.py
│       ├── e4bf19a77c31_replace_date_fields_with_department_and_budget.py
│       └── ee381d7b2572_dropped_coloumn.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_employees.py
│   └── test_health.py
├── .env                        # Local settings; ignored by Git
├── .env.example                # Safe environment-variable template
├── .gitignore
├── alembic.ini
├── employee.sql
├── README.md
└── requirements.txt
```

## Installation

Run commands from the project root:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment and database setup

Create a local `.env` from `.env.example` if you do not already have one:

```powershell
Copy-Item .env.example .env
```

Do not replace an existing `.env`; keep its local credentials and update values
as needed. `.env` is ignored by Git. Set `DATABASE_NAME`, `DATABASE_USER`,
`DATABASE_PASSWORD`, `DATABASE_HOST`, and `DATABASE_PORT` for a PostgreSQL
database that already exists. `DATABASE_DRIVER` defaults to
`postgresql+asyncpg`. The application builds its SQLAlchemy URL from these
values and safely handles URL characters in the raw password.

`TEST_DATABASE_URL` must point to a separate, dedicated test database before
running tests: the test fixtures create and drop tables there. The application
metadata is configured with `APP_NAME` and `APP_VERSION`. Authentication
settings are `JWT_SECRET_KEY`, `JWT_ALGORITHM`, and
`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`. `JWT_REFRESH_TOKEN_EXPIRE_DAYS` controls
refresh token lifetime and defaults to 7 days. Use a unique secret of at least
32 characters outside tests.

Employee-created emails use `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`,
`SMTP_PASSWORD`, and `MAIL_FROM`. For Gmail, use `smtp.gmail.com` with port
587 (STARTTLS) or 465 (implicit TLS), and authenticate with the account email
and a Google App Password rather than the normal account password. App
Passwords require 2-Step Verification and may be unavailable for managed
accounts. Keep `MAIL_FROM` set to the authenticated account. Email failures
are logged in `logs/app.log`; employee creation still succeeds because its
database transaction is already committed before the email is sent.

Apply the existing migrations after configuring the database:

```powershell
alembic upgrade head
```

The checked-in migration history currently references the missing revision
`d0778f02d3fd` from
`alembic/versions/e4bf19a77c31_replace_date_fields_with_department_and_budget.py`.
Restore that existing migration before applying upgrades; this refactor does
not modify or generate migrations.

## Run the application

Run this command from the project root (the directory containing `app/`),
not from inside `app/`:

```powershell
uvicorn app.main:app --reload
```

Interactive Swagger documentation is available at
<http://127.0.0.1:8000/docs> (ReDoc: <http://127.0.0.1:8000/redoc>).

## Health check

`GET /health/` is public and does not require authentication. It returns:

```json
{
  "status": "healthy",
  "message": "Application is running"
}
```

Application exception logs are written to `logs/app.log` with rotation; they
are not propagated to the terminal. The `logs/` directory is created on
startup and ignored by Git.

## Authentication

- `POST /auth/register` creates a user with a securely hashed password.
- `POST /auth/login` accepts OAuth2 form fields (`username` and `password`);
  the username field also accepts the registered email address. It returns an
  access token and a refresh token.
- `POST /auth/refresh` accepts a JSON `refresh_token` and returns a rotated
  access token and refresh token pair.
- `GET /auth/me` requires a bearer access token.
- New accounts receive the `user` role. Protect endpoints with
  `require_roles("admin")` from `app.api.dependency.auth_dependencies`; only
  trusted accounts should be assigned the `admin` role.

## Tests

With the dedicated test database configured in `TEST_DATABASE_URL`, run:

```powershell
pytest
```
