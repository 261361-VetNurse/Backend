# Backend API

FastAPI + MongoDB backend application

## Prerequisites

- Python 3.11.9
- Docker & Docker Compose
- pip (Python package manager)

## Setup Instructions for Development

### 0. Install Python (if not already installed)

If you don't have Python installed, download and install Python 3.11.9 from:
- **Windows/macOS:** https://www.python.org/downloads/
- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update
  sudo apt install python3.11 python3.11-venv python3-pip
  ```

Verify installation:
```bash
python --version
```

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Backend
```

### 2. Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup MongoDB with Docker Compose

Use Docker Compose to run MongoDB and Mongo Express (Web UI):

**Start MongoDB:**
```bash
docker-compose up -d
```

**Check status:**
```bash
docker-compose ps
```

**Stop MongoDB:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f mongodb
```

**Access:**
- MongoDB: `mongodb://localhost:27017`
- Mongo Express (Web UI): http://localhost:8081 (admin/admin)

### 5. Configure Environment Variables (Optional)

The `.env` file is already created and ready to use. Edit if needed:
```bash
# Edit .env file as needed
```

### 6. Run the Application

**Development mode with auto-reload:**
```bash
uvicorn app.main:app --reload
```

**Production mode:**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

The API will be available at:
- Main API: http://localhost:8000
- Interactive API docs (Swagger): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

---

## Quick Start Commands

```bash
# 1. Start MongoDB
docker-compose up -d

# 2. Install dependencies (in virtual environment)
pip install -r requirements.txt

# 3. Run the app
uvicorn app.main:app --reload

# 4. Open browser
http://localhost:8000/docs
```

---

## Project Structure

```
Backend/
├── app/                        # Main application package
│   ├── __init__.py            # Package initializer
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection
│   ├── schemas/               # Pydantic schemas (validation)
│   │   ├── __init__.py
│   │   └── item.py           # Item schemas
│   ├── routers/               # API endpoints
│   │   ├── __init__.py
│   │   └── items.py          # Items CRUD routes
│   └── services/              # Business logic
│       ├── __init__.py
│       └── item_service.py   # Item service
├── .env                       # Environment variables (created)
├── .env.example               # Example environment variables
├── .gitignore                # Git ignore file
├── docker-compose.yml        # Docker Compose for MongoDB
├── requirements.txt          # Python dependencies
└── README.md                 # This file (English)
```

---

## Tech Stack

- **Framework:** FastAPI 0.115.6
- **Web Server:** Uvicorn 0.34.0 / Gunicorn 23.0.0
- **Database:** MongoDB (via Motor 3.6.0 & PyMongo 4.9.1)
- **Validation:** Pydantic 2.10.3

---

## Architecture

```
Request → Router → Service → MongoDB
              ↓
           Schema (Validate)
```

**Layered Architecture:**
- **Routers** (`app/routers/`): Handle HTTP requests/responses
- **Services** (`app/services/`): Business logic and database operations
- **Schemas** (`app/schemas/`): Pydantic models for validation
- **Config** (`app/config.py`): Application settings
- **Database** (`app/database.py`): MongoDB connection

### Key Features

- ✅ **Async/Await**: Full async with Motor (async MongoDB driver)
- ✅ **Data Validation**: Automatic validation with Pydantic
- ✅ **API Documentation**: Auto-generated with Swagger UI
- ✅ **Docker Compose**: Easy MongoDB setup
- ✅ **Environment Config**: `.env` file support

---

## API Endpoints

### General
- `GET /` - Root endpoint with API information

### Items (CRUD)
- `GET /items/` - Get all items
- `GET /items/{item_id}` - Get item by ID
- `POST /items/` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item

📖 **API Documentation:** http://localhost:8000/docs (Swagger UI)

---

## Troubleshooting

### Virtual environment not activating on Windows
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### MongoDB connection issues
```bash
# Check MongoDB status
docker-compose ps

# Restart MongoDB
docker-compose restart mongodb

# View logs
docker-compose logs -f mongodb
```

### Port already in use
```bash
# Change port
uvicorn app.main:app --reload --port 8001

# Or kill process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Import errors
Make sure you run from project root and use `app.main:app` (not `main:app`)

---

## Adding New Features

See detailed guide in **[SIMPLE_README.md](SIMPLE_README.md)** (Thai)

**Steps:**
1. Create Schema (`app/schemas/`)
2. Create Service (`app/services/`)
3. Create Router (`app/routers/`)
4. Register in `app/main.py`

---

## Next Steps

- [ ] Add Authentication (Login/Register)
- [ ] Add User management
- [ ] Add File upload
- [ ] Add Tests
- [ ] Deploy to production

---

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **MongoDB Motor Documentation**: https://motor.readthedocs.io/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Docker Compose Documentation**: https://docs.docker.com/compose/

---

