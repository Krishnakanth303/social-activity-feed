# Social Activity Feed Backend

A production-ready FastAPI backend for a social activity feed with user authentication, posts, likes, follows, blocks, activity wall, admin/owner permissions, logging, rate limiting, security, and Docker deployment.

## Features
- User signup/login (JWT)
- Create, list, and delete posts
- Like, follow, block users
- Activity wall with filters
- Admin/owner role management
- Error handling and validation
- Logging, rate limiting, security headers
- Alembic migrations
- Docker and docker-compose for deployment
- Automated tests

## Prerequisites
- Python 3.9+
- PostgreSQL (local or Docker)
- Docker (optional)

## Local Setup
1. **Clone the repository**
2. **Create and activate a virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Create PostgreSQL database**
   - Locally: Use pgAdmin or psql to create a database named `inkle_feed`
   - With Docker:
     ```powershell
     docker-compose up db
     ```
5. **Configure environment variables**
   - Copy `.env.example` to `.env` and update values as needed
6. **Run Alembic migrations**
   ```powershell
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```
7. **Start the FastAPI server**
   ```powershell
   uvicorn app.main:app --reload
   ```
8. **Access API docs**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs)

## Run with Docker
```powershell
docker-compose up --build
```

## Running Tests
```powershell
pytest
```

## Postman Collection
- See `postman_collection.json` for ready-to-import API requests.

## Alembic Migrations
- To create new migrations:
  ```powershell
  alembic revision --autogenerate -m "Your message"
  alembic upgrade head
  ```

## License
MIT
