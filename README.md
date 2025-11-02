# FastAPI Learning Project

A well-structured FastAPI application demonstrating best practices for building RESTful APIs with PostgreSQL database integration.

## 🌟 Features

- **RESTful API** with complete CRUD operations
- **PostgreSQL** database integration with SQLAlchemy ORM
- **Environment-based configuration** using `.env` files
- **Comprehensive error handling** with specific exception types
- **Request validation** using Pydantic models
- **API documentation** with Swagger UI and ReDoc
- **Logging** for debugging and monitoring
- **CORS middleware** for cross-origin requests
- **Pagination support** for list endpoints
- **Type hints** throughout the codebase

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd fastapi_learning
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=fastapi_learning
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Application Configuration
APP_NAME=FastAPI Learning
APP_VERSION=1.0.0
DEBUG=True
```

### 5. Set Up Database

Create the PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE fastapi_learning;

# Exit psql
\q
```

### 6. Run Database Migrations

Apply the database schema using Alembic migrations:

```bash
# Using alembic directly (recommended)
alembic upgrade head

# Or using the helper script
python scripts/run_migrations.py upgrade
```

**📖 New to migrations?** Start here:
- 🚀 **Quick Start**: [QUICK_START_MIGRATIONS.md](QUICK_START_MIGRATIONS.md) - Simple guide for beginners
- ⚡ **Cheat Sheet**: [MIGRATION_CHEATSHEET.md](MIGRATION_CHEATSHEET.md) - One-page reference
- ❓ **FAQ**: [MIGRATION_FAQ.md](MIGRATION_FAQ.md) - Common questions answered
- 📊 **Visual Guide**: [MIGRATION_WORKFLOW.md](MIGRATION_WORKFLOW.md) - Diagrams and flowcharts
- 📚 **Detailed Guide**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Company-level best practices
- 🔧 **Quick Commands**: Run `./scripts/migration_guide.sh` for status and help

### 7. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Root

- `GET /` - Welcome message and API status

### Categories

- `POST /categories/` - Create a new category
- `GET /categories/` - Get all categories (supports pagination)
- `GET /categories/{category_id}` - Get a specific category by ID
- `PUT /categories/{category_id}` - Update a category
- `DELETE /categories/{category_id}` - Delete a category

### Items

- `POST /items/` - Create a new item
- `GET /items/` - Get all items (supports pagination)
- `GET /items/{item_id}` - Get a specific item by ID
- `PUT /items/{item_id}` - Update an item
- `DELETE /items/{item_id}` - Delete an item

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user profile

## 📦 Project Structure

```
fastapi_learning/
├── alembic/                 # Database migrations
│   ├── versions/            # Migration scripts
│   ├── env.py              # Alembic environment config
│   ├── README.md           # Migration documentation
│   └── script.py.mako      # Migration template
├── api/
│   ├── __init__.py
│   ├── auth/               # Authentication endpoints
│   │   ├── __init__.py
│   │   └── auth.py
│   └── endpoints/
│       ├── __init__.py
│       ├── categories.py   # Category endpoints
│       └── items.py        # Item endpoints
├── core/
│   ├── __init__.py
│   ├── database.py         # Database configuration
│   ├── middleware.py       # Custom middleware
│   └── utils.py           # Utility functions
├── models/
│   ├── __init__.py
│   ├── category.py        # Category model
│   ├── item.py            # Item model
│   └── user.py            # User model
├── schemas/
│   ├── __init__.py
│   ├── category.py        # Category schemas
│   ├── item.py            # Item schemas
│   └── user.py            # User schemas
├── scripts/
│   └── run_migrations.py  # Migration helper script
├── .env                   # Environment variables (git-ignored)
├── .gitignore            # Git ignore rules
├── alembic.ini           # Alembic configuration
├── app.log               # Application logs (git-ignored)
├── main.py               # Application entry point
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## 🛠️ Development Best Practices Implemented

### 1. **Security**

- ✅ No hardcoded credentials
- ✅ Environment variable management with `python-dotenv`
- ✅ Proper `.gitignore` to prevent sensitive data leaks

### 2. **Code Quality**

- ✅ Comprehensive docstrings for all functions and classes
- ✅ Type hints throughout the codebase
- ✅ Proper package structure with `__init__.py` files
- ✅ PEP 8 compliant code formatting

### 3. **Error Handling**

- ✅ Specific exception handling (SQLAlchemyError, IntegrityError)
- ✅ Proper HTTP status codes (201, 200, 404, 400, 500)
- ✅ Descriptive error messages
- ✅ Database rollback on errors

### 4. **API Design**

- ✅ RESTful endpoint naming conventions
- ✅ Proper HTTP methods (POST, GET, PUT, DELETE)
- ✅ Request/response validation with Pydantic
- ✅ Pagination support
- ✅ Complete CRUD operations

### 5. **Database**

- ✅ Connection pooling configuration
- ✅ Health checks with `pool_pre_ping`
- ✅ Proper session management
- ✅ Lifespan events for startup/shutdown
- ✅ Database migrations with Alembic

### 6. **Observability**

- ✅ Structured logging
- ✅ Log levels (INFO, WARNING, ERROR)
- ✅ File and console logging
- ✅ Request/operation logging

### 7. **Documentation**

- ✅ OpenAPI/Swagger documentation
- ✅ Endpoint descriptions and examples
- ✅ Schema documentation with examples
- ✅ Comprehensive README

## 🧪 Testing the API

### Create an Item

```bash
curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "A high-performance laptop"}'
```

### Get All Items

```bash
curl -X GET "http://localhost:8000/items/"
```

### Get Item by ID

```bash
curl -X GET "http://localhost:8000/items/1"
```

### Update an Item

```bash
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Gaming Laptop", "description": "An updated description"}'
```

### Delete an Item

```bash
curl -X DELETE "http://localhost:8000/items/1"
```

## 📝 Validation Rules

### Item Name

- Required field
- Minimum length: 1 character
- Maximum length: 100 characters

### Item Description

- Optional field
- Maximum length: 500 characters

## 🔍 Logging

Application logs are written to:

- **Console**: Real-time output
- **File**: `app.log` (rotating logs recommended for production)

Log format:

```
YYYY-MM-DD HH:MM:SS - module_name - LOG_LEVEL - Message
```

## 🚧 Future Enhancements

- [ ] Add role-based access control (RBAC)
- [ ] Add JWT token refresh mechanism
- [ ] Add unit and integration tests
- [ ] Add request rate limiting
- [ ] Implement caching with Redis
- [ ] Add background tasks with Celery
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
- [ ] Add monitoring with Prometheus/Grafana

## 📖 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 📄 License

This is a learning project for educational purposes.

## 🤝 Contributing

This is a personal learning project, but suggestions and improvements are welcome!

---

**Happy Coding! 🚀**
