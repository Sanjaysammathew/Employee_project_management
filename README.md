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
uvicorn app.main:app --reload
```
