# 🐾 VetNurse Backend API

Pet Medication Diary Backend - FastAPI + MySQL

## 📋 Requirements

- Python 3.11.9
- MySQL 8.0
- pip 26.0+

## 🚀 Installation

### 1. Create Virtual Environment

```bash
# Create venv with Python 3.11.9
python -m venv .venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Run FastAPI

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### With Gunicorn (Production)

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root Endpoint**: http://localhost:8000/

## 🔧 Configuration

Create a `.env` file in the root directory:

```ini
# LINE Login
CHANNEL_ID=your_channel_id
KEY_ID=your_key_id
LOGIN_CLIENT_ID=your_login_client_id
LOGIN_CLIENT_SECRET=your_login_client_secret

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=pet_medic_user
MYSQL_PASSWORD=secure_password_2026
MYSQL_DATABASE=pet_medic_db

# JWT
JWT_SECRET=vetnurse-secret-key
```

## 🗄️ Database Setup

Start MySQL with Docker:

```bash
cd database
docker-compose up -d mysql
```

## 📦 Project Structure

```
Backend/
├── app/
│   ├── models_sql/         # SQLAlchemy models
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   ├── schemas/            # Pydantic schemas
│   ├── config.py           # Configuration
│   ├── database_sql.py     # Database connection
│   └── main.py             # FastAPI application
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```