# FastAPI Microservices Project - Complete Reference

## 📋 Project Overview

This is a **microservices-based application** built with FastAPI, demonstrating modern backend architecture with three independent services that communicate via HTTP/REST APIs. The project showcases authentication, product management, and inventory management in a distributed system.

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client / Browser                              │
└────────┬───────────────┬─────────────────┬─────────────────────┘
         │               │                 │
         ▼               ▼                 ▼
   ┌──────────┐   ┌──────────┐    ┌──────────────┐
   │   Auth   │   │ Product  │◄───│  Inventory   │
   │ Service  │   │ Service  │    │   Service    │
   │ Port:8000│   │Port: 8001│    │  Port: 8002  │
   └─────┬────┘   └─────┬────┘    └──────┬───────┘
         │              │                 │
         ▼              ▼                 ▼
   ┌──────────┐   ┌──────────┐    ┌──────────────┐
   │ auth_db  │   │product_db│    │ inventory_db │
   │Port: 5435│   │Port: 5433│    │  Port: 5434  │
   └──────────┘   └──────────┘    └──────────────┘
```

---

## 🏗️ Services Architecture

### 1. Auth Service (Port 8000)

**Purpose**: Central authentication and user management service

**Database**: `auth_service` on PostgreSQL (Port 5435)

**Key Responsibilities**:
- User registration and authentication
- JWT token generation and validation
- Password hashing with bcrypt (with SHA-256 pre-hashing)
- Role-based access control (SUPER_ADMIN, ADMIN, USER, MODERATOR)

**Database Schema**:

```sql
Table: users
- id: INTEGER (Primary Key, Auto-increment)
- email: VARCHAR(255) (Unique, Indexed)
- hashed_password: VARCHAR(255)
- name: VARCHAR(255)
- role: ENUM (super_admin, admin, user, moderator) - Default: user
```

**API Endpoints**:

| Method | Endpoint        | Description              | Auth Required |
|--------|-----------------|--------------------------|---------------|
| GET    | `/`             | Health check             | No            |
| POST   | `/auth/`        | User registration/signup | No            |
| POST   | `/auth/login`   | User login (sets cookie) | No            |
| POST   | `/auth/logout`  | User logout              | No            |

**Authentication Flow**:
1. User registers with email, name, and password
2. Password is SHA-256 hashed, then bcrypt hashed
3. On login, JWT token is generated and stored in HTTP-only cookie
4. Token expires in 60 minutes (configurable)
5. Other services validate tokens using auth_guard

**Technologies Used**:
- FastAPI for API framework
- SQLAlchemy for ORM
- Alembic for database migrations
- python-jose for JWT handling
- passlib + bcrypt for password hashing
- PostgreSQL for data storage

---

### 2. Product Service (Port 8001)

**Purpose**: Product and category management system

**Database**: `product_service` on PostgreSQL (Port 5433)

**Key Responsibilities**:
- CRUD operations for items
- CRUD operations for categories
- Item-category relationship management
- Protected endpoints (requires authentication)

**Database Schema**:

```sql
Table: categories
- id: INTEGER (Primary Key, Auto-increment)
- name: VARCHAR(100) (Indexed)
- slug: VARCHAR(50) (Indexed)
- description: TEXT (Nullable)

Table: items
- id: INTEGER (Primary Key, Auto-increment)
- name: VARCHAR(100) (Indexed)
- description: TEXT (Nullable)
- category_id: INTEGER (Foreign Key -> categories.id)

Relationship: One Category -> Many Items
```

**API Endpoints**:

| Method | Endpoint              | Description               | Auth Required |
|--------|-----------------------|---------------------------|---------------|
| GET    | `/`                   | Health check              | No            |
| POST   | `/items/`             | Create new item           | Yes           |
| GET    | `/items/`             | List all items (paginated)| Yes           |
| GET    | `/items/{item_id}`    | Get specific item         | Yes           |
| PUT    | `/items/{item_id}`    | Update item               | Yes           |
| POST   | `/categories/`        | Create new category       | Yes           |
| GET    | `/categories/`        | List all categories       | Yes           |
| GET    | `/categories/{id}`    | Get specific category     | Yes           |

**Features**:
- Pagination support (skip/limit parameters)
- Eager loading with joinedload for efficient queries
- Category validation on item creation
- Comprehensive error handling
- Structured logging

**Technologies Used**:
- FastAPI for API framework
- SQLAlchemy with relationship mapping
- Alembic for database migrations
- Pydantic for data validation
- PostgreSQL for data storage

---

### 3. Inventory Service (Port 8002)

**Purpose**: Inventory management with product service integration

**Database**: `inventory_service` on PostgreSQL (Port 5434)

**Key Responsibilities**:
- Inventory tracking and management
- Inter-service communication with Product Service
- Category validation against Product Service
- Stock level management

**Database Schema**:

```sql
Table: inventory
- id: INTEGER (Primary Key, Auto-increment)
- product_name: TEXT
- category: VARCHAR(500)
- quantity_in_stock: INTEGER
- unit_price: FLOAT
- last_restock_date: DATETIME
- supplier: TEXT
- reorder_point: INTEGER
```

**API Endpoints**:

| Method | Endpoint         | Description                          | Auth Required |
|--------|------------------|--------------------------------------|---------------|
| GET    | `/`              | Health check                         | No            |
| POST   | `/inventory/`    | Create inventory with validation     | Yes           |
| GET    | `/inventory/`    | List all inventory items             | Yes           |

**Inter-Service Communication**:
- Uses `httpx` AsyncClient for HTTP requests
- Fetches category details from Product Service
- Validates category existence before inventory creation
- Forwards authentication cookies to Product Service
- Configurable Product Service URL via environment variable

**Integration Pattern**:
```python
# Example flow:
1. Inventory service receives create request with category_id
2. Makes async HTTP call to Product Service: GET /categories/{id}
3. Validates category exists
4. Creates inventory record with category name
5. Returns response to client
```

**Technologies Used**:
- FastAPI for API framework
- SQLAlchemy for ORM
- httpx for async HTTP client
- PostgreSQL for data storage

---

## 🔐 Authentication & Security

### JWT Token Authentication

**Token Generation** (Auth Service):
```python
- Algorithm: HS256
- Expiration: 60 minutes (configurable)
- Secret Key: TOKEN_SECRET environment variable
- Token Payload: {"auth_user": user_email, "exp": expiration_time}
- Storage: HTTP-only cookie named "access_token"
```

**Cookie Configuration**:
```python
- httponly: True (prevents JavaScript access)
- secure: True (HTTPS only in production)
- samesite: "lax" (CSRF protection)
- max_age: 3600 seconds (1 hour)
```

**Auth Guard Implementation**:
```python
# All protected routes use auth_guard dependency
# Validates token from cookie
# Extracts user email and attaches to request.state.user
# Raises 401 if token missing or invalid
```

### Password Security

**Hashing Strategy**:
1. SHA-256 pre-hashing (handles passwords > 72 bytes)
2. Bcrypt hashing (industry standard, with salt)
3. Automatic deprecation handling via passlib

### CORS Configuration

```python
- Allow Origins: "*" (development) - restrict in production
- Allow Credentials: True
- Allow Methods: All
- Allow Headers: All
```

**Production Recommendations**:
- ✅ Set specific allowed origins
- ✅ Use HTTPS/TLS
- ✅ Implement rate limiting
- ✅ Add API gateway
- ✅ Service-to-service authentication
- ✅ Secret management (e.g., AWS Secrets Manager)

---

## 🛠️ Technology Stack

### Core Framework
- **FastAPI** 0.120.1 - Modern, fast web framework
- **Python** 3.14 - Programming language
- **Uvicorn** 0.38.0 - ASGI server with auto-reload

### Database & ORM
- **PostgreSQL** 16 (Alpine) - Relational database
- **SQLAlchemy** 2.0.23 - Python SQL toolkit and ORM
- **Alembic** 1.13.1 - Database migration tool
- **psycopg2-binary** 2.9.11 - PostgreSQL adapter

### Authentication & Security
- **python-jose** 3.3.0 - JWT token handling
- **passlib** 1.7.4 - Password hashing library
- **bcrypt** 4.1.2 - Password hashing algorithm

### Data Validation
- **Pydantic** 2.12.3 - Data validation using Python type hints
- **pydantic_core** 2.41.4 - Core validation logic

### HTTP Client
- **httpx** - Async HTTP client for inter-service communication

### Utilities
- **python-dotenv** 1.0.0 - Environment variable management

### Infrastructure
- **Docker** & **Docker Compose** - Containerization
- Custom bridge network for service communication
- Persistent volumes for database data

---

## 🔄 Inter-Service Communication

### Communication Pattern

**Synchronous HTTP/REST**:
- Inventory Service → Product Service (category validation)
- Uses async httpx client for non-blocking operations
- JWT cookie forwarding for authentication
- Timeout handling (10 seconds)
- Follow redirects enabled

### Service Discovery

**Docker Environment** (Production-like):
```
Services communicate using container names:
- http://auth-service:8000
- http://product-service:8001
- http://inventory-service:8002
```

**Local Development**:
```
Services communicate using localhost:
- http://localhost:8000
- http://localhost:8001
- http://localhost:8002
```

### Error Handling

**Strategies**:
- HTTP status code propagation
- Graceful degradation
- Timeout management
- Detailed error messages in logs
- Client-friendly error responses

---

## 🐳 Docker Configuration

### Docker Compose Setup

**3 Services + 3 Databases**:
```yaml
Networks:
- microservices-network (bridge driver)

Services:
1. auth-service + auth-db (PostgreSQL)
2. product-service + product-db (PostgreSQL)
3. inventory-service + inventory-db (PostgreSQL)

Volumes:
- auth-db-data (persistent storage)
- product-db-data (persistent storage)
- inventory-db-data (persistent storage)
```

### Health Checks

All databases include health checks:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Volume Mounts

Development mode with hot reload:
```yaml
volumes:
  - ./auth-service:/app
  - ./product-service:/app
  - ./inventory-service:/app
```

### Environment Variables

**Common across services**:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
TOKEN_SECRET=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Service-specific**:
```
Auth Service:
- POSTGRES_DB=auth_service
- POSTGRES_HOST=auth-db

Product Service:
- POSTGRES_DB=product_service
- POSTGRES_HOST=product-db
- INVENTORY_SERVICE_URL=http://inventory-service:8002

Inventory Service:
- POSTGRES_DB=inventory_service
- POSTGRES_HOST=inventory-db
- PRODUCT_SERVICE_URL=http://product-service:8001
```

---

## 📊 Database Migrations (Alembic)

**Auth Service & Product Service** use Alembic for schema management.

### Migration Files

**Auth Service**:
- `b573df09ec59_initial_migration.py` - Initial users table
- `746836963f64_token_added_in_user_table.py` - Token field added
- `840c09b4f9e0_token_removed.py` - Token field removed

**Product Service**:
- Uses same migration structure
- Manages categories and items tables

### Common Commands

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

---

## 🚀 Deployment Options

### 1. Local Development

```bash
# Terminal 1
cd auth-service && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2
cd product-service && source venv/bin/activate && uvicorn main:app --reload --port 8001

# Terminal 3
cd inventory-service && source venv/bin/activate && uvicorn main:app --reload --port 8002
```

### 2. Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### 3. Production (Future)

**Options**:
- **Kubernetes**: Container orchestration
- **AWS ECS/Fargate**: Managed container service
- **Docker Swarm**: Native Docker clustering
- **Traditional VMs**: Separate servers with nginx reverse proxy

---

## 📝 Logging & Monitoring

### Current Logging Setup

```python
Format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
Handlers:
- StreamHandler (console output)
- FileHandler (app.log in each service)
Level: INFO
```

### Log Files

Each service maintains its own log:
- `auth-service/app.log`
- `product-service/app.log`
- `inventory-service/app.log`

### Future Enhancements

- 🔲 Centralized logging (ELK Stack)
- 🔲 Prometheus metrics
- 🔲 Grafana dashboards
- 🔲 Distributed tracing (Jaeger/Zipkin)
- 🔲 APM tools (New Relic, DataDog)

---

## 🎯 Key Features & Patterns

### Design Patterns Implemented

1. **Microservices Architecture**
   - Service isolation
   - Independent databases
   - Autonomous deployment

2. **Repository Pattern**
   - Database access abstraction
   - Dependency injection via FastAPI's Depends()

3. **Middleware Pattern**
   - CORS middleware
   - Authentication middleware (can be enabled globally)

4. **Lifespan Events**
   - Database initialization on startup
   - Graceful connection cleanup on shutdown

5. **Request/Response Pattern**
   - Pydantic schemas for validation
   - Clear separation of models and schemas

### Error Handling Strategy

```python
Try-Catch Hierarchy:
1. HTTPException (re-raise)
2. SQLAlchemyError (database errors)
3. IntegrityError (constraint violations)
4. Generic Exception (unexpected errors)

All errors logged with context
Client receives sanitized error messages
```

---

## 📖 API Documentation

All services provide auto-generated documentation:

**Swagger UI**: `http://localhost:{port}/docs`
**ReDoc**: `http://localhost:{port}/redoc`

### Example Request Flow

**1. User Registration**:
```bash
POST http://localhost:8000/auth/
Body: {"email": "user@example.com", "name": "John Doe", "password": "secure123"}
Response: {"id": 1, "email": "user@example.com", "name": "John Doe"}
```

**2. User Login**:
```bash
POST http://localhost:8000/auth/login
Body: {"email": "user@example.com", "password": "secure123"}
Response: {"message": "Login success", "email": "user@example.com"}
Sets-Cookie: access_token=<jwt_token>
```

**3. Create Category** (requires authentication):
```bash
POST http://localhost:8001/categories/
Cookie: access_token=<jwt_token>
Body: {"name": "Electronics", "slug": "electronics", "description": "Electronic items"}
Response: {"id": 1, "name": "Electronics", "slug": "electronics", "description": "Electronic items"}
```

**4. Create Item** (requires authentication):
```bash
POST http://localhost:8001/items/
Cookie: access_token=<jwt_token>
Body: {"name": "Laptop", "description": "Gaming laptop", "category_id": 1}
Response: {"id": 1, "name": "Laptop", "description": "Gaming laptop", "category_id": 1, "category": {...}}
```

**5. Create Inventory** (requires authentication + validates category):
```bash
POST http://localhost:8002/inventory/
Cookie: access_token=<jwt_token>
Body: {
  "product_name": "Laptop Pro",
  "category": 1,
  "quantity_in_stock": 50,
  "unit_price": 1299.99,
  "last_restock_date": "2024-01-15T10:00:00",
  "supplier": "Tech Supplier Inc",
  "reorder_point": 10
}
Response: Inventory record with validated category name
```

---

## 🔍 Project Structure

```
fastapi-learning/
├── auth-service/
│   ├── alembic/              # Database migrations
│   ├── api/auth/             # Auth endpoints
│   ├── core/                 # Database, middleware, utils
│   ├── models/               # SQLAlchemy models (User)
│   ├── schemas/              # Pydantic schemas
│   ├── venv/                 # Virtual environment
│   ├── main.py               # Application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Container definition
│   └── env.example           # Environment template
│
├── product-service/
│   ├── alembic/              # Database migrations
│   ├── api/endpoints/        # Item & category endpoints
│   ├── core/                 # Database, middleware, utils
│   ├── models/               # SQLAlchemy models (Item, Category)
│   ├── schemas/              # Pydantic schemas
│   ├── venv/                 # Virtual environment
│   ├── main.py               # Application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Container definition
│   └── env.example           # Environment template
│
├── inventory-service/
│   ├── api/                  # Inventory endpoints
│   ├── core/                 # Utilities
│   ├── models/               # SQLAlchemy models (Inventory)
│   ├── schemas/              # Pydantic schemas
│   ├── venv/                 # Virtual environment
│   ├── database.py           # Database configuration
│   ├── main.py               # Application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Container definition
│   └── env.example           # Environment template
│
├── docker-compose.yml        # Multi-service orchestration
├── DOCKER_SETUP.md           # Docker documentation
├── README.md                 # Project README
└── PROJECT_SUMMARY.md        # This file (comprehensive reference)
```

---

## 🎓 Learning Objectives Demonstrated

This project showcases:

1. ✅ **Microservices Architecture** - Independent, scalable services
2. ✅ **RESTful API Design** - Standard HTTP methods and status codes
3. ✅ **JWT Authentication** - Stateless authentication with cookies
4. ✅ **Database Relationships** - One-to-many with SQLAlchemy
5. ✅ **Inter-Service Communication** - HTTP client, async operations
6. ✅ **Docker Containerization** - Multi-container setup with compose
7. ✅ **Database Migrations** - Schema versioning with Alembic
8. ✅ **Error Handling** - Comprehensive exception management
9. ✅ **Logging** - Structured logging across services
10. ✅ **API Documentation** - Auto-generated with OpenAPI/Swagger
11. ✅ **Dependency Injection** - FastAPI's Depends system
12. ✅ **Environment Configuration** - Secure config management
13. ✅ **Type Safety** - Pydantic validation
14. ✅ **Async Programming** - Async/await for I/O operations

---

## 🚧 Known Limitations & Future Improvements

### Current Limitations

1. **No Circuit Breaker** - Service failures not isolated
2. **No Message Queue** - Only synchronous communication
3. **No Caching** - No Redis or in-memory caching
4. **No Rate Limiting** - Vulnerable to abuse
5. **Basic Logging** - No centralized log aggregation
6. **No Monitoring** - No metrics collection
7. **No Service Mesh** - Manual service discovery
8. **No API Gateway** - Direct service access
9. **Inventory Service** - No Alembic migrations set up

### Roadmap

**Phase 1: Resilience**
- 🔲 Circuit breaker pattern (e.g., with tenacity)
- 🔲 Retry logic with exponential backoff
- 🔲 Health check endpoints
- 🔲 Graceful degradation

**Phase 2: Scalability**
- 🔲 Redis caching layer
- 🔲 Message queue (RabbitMQ/Kafka)
- 🔲 Event-driven architecture
- 🔲 Load balancing

**Phase 3: Observability**
- 🔲 Prometheus metrics
- 🔲 Grafana dashboards
- 🔲 Distributed tracing
- 🔲 ELK stack

**Phase 4: Production Readiness**
- 🔲 API Gateway (Kong/Traefik)
- 🔲 Service mesh (Istio)
- 🔲 Kubernetes deployment
- 🔲 CI/CD pipeline
- 🔲 Infrastructure as Code (Terraform)

---

## 💡 Use Cases

This architecture is suitable for:

1. **E-commerce Platforms** - Product catalog + inventory management
2. **Multi-tenant SaaS** - Isolated services per domain
3. **Learning Projects** - Understanding microservices concepts
4. **MVP Development** - Quick prototyping with clean separation
5. **Scalable Applications** - Independent service scaling

---

## 🤔 When to Use This Architecture

### ✅ Good Fit

- Multiple teams working on different features
- Different scaling requirements per service
- Technology diversity needs
- Independent deployment requirements
- Long-term maintenance and evolution

### ❌ Not Ideal For

- Simple CRUD applications
- Small teams (overhead too high)
- Tight coupling requirements
- Real-time data consistency needs (without event sourcing)
- Limited infrastructure resources

---

## 📚 Additional Resources

### Documentation Files

- `README.md` - Main project documentation
- `DOCKER_SETUP.md` - Docker deployment guide
- `auth-service/ALEMBIC_GUIDE.md` - Alembic migration guide
- `product-service/ALEMBIC_GUIDE.md` - Alembic migration guide
- `auth-service/README.md` - Auth service details
- `product-service/README.md` - Product service details

### External References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [JWT Introduction](https://jwt.io/introduction)

---

## 🎉 Summary

This project demonstrates a **production-ready microservices architecture** with:
- ✅ 3 independent services (Auth, Product, Inventory)
- ✅ 3 separate PostgreSQL databases
- ✅ JWT-based authentication with secure password hashing
- ✅ Inter-service HTTP communication
- ✅ Docker containerization with compose
- ✅ Database migrations with Alembic
- ✅ Comprehensive error handling and logging
- ✅ Auto-generated API documentation
- ✅ Type-safe validation with Pydantic

**Perfect for**: Learning microservices, building MVPs, understanding distributed systems, or as a template for larger projects.

---

**Last Updated**: November 6, 2025
**Project Status**: Active Development
**License**: MIT

