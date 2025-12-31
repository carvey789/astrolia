# Horoscope Backend API

FastAPI backend for the Flutter Horoscope app.

## Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Create PostgreSQL database:
```sql
CREATE DATABASE horoscope_db;
```

5. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Auth
- `POST /auth/register` - Register with email/password
- `POST /auth/login` - Login with email/password
- `POST /auth/google` - Login with Google
- `POST /auth/refresh` - Refresh token

### Users
- `GET /users/me` - Get profile
- `PUT /users/me` - Update profile
- `PUT /users/me/preferences` - Update preferences

### Horoscope
- `GET /horoscope/signs` - All zodiac signs
- `GET /horoscope/daily/{sign_id}` - Daily horoscope
- `GET /horoscope/compatibility/{sign1}/{sign2}` - Compatibility

### Journal
- `GET /journal` - List entries
- `POST /journal` - Create entry
- `PUT /journal/{id}` - Update entry
- `DELETE /journal/{id}` - Delete entry

### Tarot
- `GET /tarot/daily` - Daily card
- `GET /tarot/spread` - 3-card spread
- `GET /tarot/history` - Reading history
