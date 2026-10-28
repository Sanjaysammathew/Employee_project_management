# Employee Project API

## Setup

1. Create and activate a virtual environment (at the project root):
   ```
   python -m venv venv
   venv\Scripts\activate        
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root:
   ```
   DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@127.0.0.1:5432/employee_project_db
   ```
4. Create the database in PostgreSQL, then apply migrations:
   ```
   alembic upgrade head
   ```

## Run
Always run from the project root:
```
uvicorn main:app --reload
```

## Authentication

Set these values in the root `.env` file. Use a unique random JWT secret of at
least 32 characters, and do not commit `.env`:

```
JWT_SECRET_KEY=<at-least-32-character-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

- `POST /auth/register` creates a user with a securely hashed password.
- `POST /auth/login` accepts OAuth2 form fields (`username` and `password`); the
  username field also accepts the registered email address.
- `GET /auth/me` requires `Authorization: Bearer <access_token>`.
- New accounts receive the `user` role. Use `require_roles("admin")` from
  `app.auth_dependencies` to protect an endpoint; assign the `admin` role only
  to trusted accounts using a controlled database operation.

