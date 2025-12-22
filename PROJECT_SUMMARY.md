# FastAPI Microservices Project - Complete Reference

## 📋 Project Overview

This is a **comprehensive microservices-based application** built with FastAPI, demonstrating modern backend architecture with multiple independent services that communicate via HTTP/REST APIs, WebSockets, and message queues. The project showcases authentication, product management, inventory management, booking systems, food ordering, and a React frontend in a distributed system.

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    React Client (TypeScript + Tailwind CSS)                 │
│                         Port: 5173                                           │
└────────┬──────────────────────┬──────────────────────┬─────────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
   ┌──────────┐          ┌──────────┐          ┌──────────┐
   │   Auth   │          │ Booking  │          │   Food   │
   │ Service  │          │ Service  │          │ Service  │
   │ Port:8000│          │Port: 8003│          │Port: 8004│
   └─────┬────┘          └─────┬────┘          └─────┬────┘
         │                    │                     │
         ▼                    ▼                     ▼
   ┌──────────┐          ┌──────────┐          ┌──────────┐
   │ auth_db  │          │booking_db│          │ food_db  │
   │Port:5435 │          │Port:5436 │          │Port:5437 │
   └──────────┘          └─────┬────┘          └─────┬────┘
                               │                     │
                               ▼                     ▼
                       ┌──────────────┐      ┌──────────┐
                       │ Elasticsearch│      │  Redis   │
                       │  Port: 9200  │      │Port:6379 │
                       └──────────────┘      └──────────┘
```

---

## 🏗️ Services Architecture

### 1. Auth Service (Port 8000) ✅ Active

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

| Method | Endpoint       | Description              | Auth Required |
| ------ | -------------- | ------------------------ | ------------- |
| GET    | `/`            | Health check             | No            |
| POST   | `/auth/`       | User registration/signup | No            |
| POST   | `/auth/login`  | User login (sets cookie) | No            |
| POST   | `/auth/logout` | User logout              | No            |

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

### 2. Booking Service (Port 8003) ✅ Active

**Purpose**: Movie theater booking system with Elasticsearch integration

**Database**: `booking_service` on PostgreSQL (Port 5436)

**Key Responsibilities**:

- Theater management
- Movie management
- Showtime/showing management
- Seat management and availability
- Booking creation and management
- Booking seat associations
- Full-text search across movies, theaters, showings, and bookings using Elasticsearch
- Web scraping for upcoming IPOs (optional feature)

**Database Schema**:

```sql
Table: theaters
- id: UUID (Primary Key)
- name: VARCHAR(255)
- address: TEXT
- capacity: INTEGER

Table: movies
- id: UUID (Primary Key)
- title: VARCHAR(255)
- description: TEXT
- duration: INTEGER
- genre: VARCHAR(100)

Table: showings
- id: UUID (Primary Key)
- movie_id: UUID (Foreign Key -> movies.id)
- theater_id: UUID (Foreign Key -> theaters.id)
- show_time: TIMESTAMP
- price: DECIMAL

Table: seats
- id: UUID (Primary Key)
- theater_id: UUID (Foreign Key -> theaters.id)
- row_number: VARCHAR(10)
- seat_number: INTEGER
- seat_type: VARCHAR(50)

Table: bookings
- id: UUID (Primary Key)
- user_id: UUID
- showing_id: UUID (Foreign Key -> showings.id)
- booking_number: VARCHAR(255) (Unique)
- total_price: DECIMAL
- status: ENUM (confirmed, cancelled, refunded)
- created_at: TIMESTAMP

Table: booking_seats
- id: UUID (Primary Key)
- booking_id: UUID (Foreign Key -> bookings.id)
- seat_id: UUID (Foreign Key -> seats.id)
- showing_id: UUID (Foreign Key -> showings.id)
```

**API Endpoints**:

| Method | Endpoint                 | Description                     | Auth Required |
| ------ | ------------------------ | ------------------------------- | ------------- |
| GET    | `/`                      | Health check                    | No            |
| POST   | `/theaters/`             | Create theater                  | Yes           |
| GET    | `/theaters/`             | List all theaters               | Yes           |
| POST   | `/movies/`               | Create movie                    | Yes           |
| GET    | `/movies/`               | List all movies                 | Yes           |
| POST   | `/showings/`             | Create showing                  | Yes           |
| GET    | `/showings/`             | List all showings               | Yes           |
| POST   | `/seats/`                | Create seat                     | Yes           |
| GET    | `/seats/`                | List all seats                  | Yes           |
| POST   | `/bookings/`             | Create booking                  | Yes           |
| GET    | `/bookings/`             | List all bookings               | Yes           |
| POST   | `/booking_seats/`        | Create booking seat association | Yes           |
| GET    | `/search/?query={query}` | Search across indices           | Yes           |
| POST   | `/scrap/`                | Scrape upcoming IPOs            | No            |

**Elasticsearch Integration**:

- Automatic index creation on startup
- Multi-index search (movies, theaters, showings, bookings)
- Full-text search with relevance scoring
- Indexed fields: titles, descriptions, addresses, booking numbers
- Health check integration

**Features**:

- Seat availability validation
- Booking status management (confirmed, cancelled, refunded)
- Unique booking number generation
- Showing expiration validation
- Repository pattern for data access
- Service layer for business logic
- Comprehensive error handling

**Technologies Used**:

- FastAPI for API framework
- SQLAlchemy with UUID primary keys
- PostgreSQL for data storage
- Elasticsearch 8.11.0 for search functionality
- Playwright/Chromium for web scraping (optional)

---

### 3. Food Service (Port 8004) ⚠️ Commented in Docker

**Purpose**: Food ordering system with restaurant and menu management

**Database**: `food_service` on PostgreSQL (Port 5437)

**Key Responsibilities**:

- Category management for food items
- Restaurant management
- Food item management
- Menu management (linking foods to restaurants)
- Order management with user association
- WebSocket support for real-time updates
- Optional database sharding for horizontal scaling
- Rate limiting with Redis
- Inter-service HTTP communication using httpx
- Rate limit headers middleware for all responses

**Database Schema**:

```sql
Table: categories
- id: UUID (Primary Key)
- name: VARCHAR(255)
- description: TEXT

Table: restaurants
- id: UUID (Primary Key)
- name: VARCHAR(255)
- address: TEXT
- phone: VARCHAR(50)

Table: foods
- id: UUID (Primary Key)
- name: VARCHAR(255)
- description: TEXT
- category_id: UUID (Foreign Key -> categories.id)
- price: DECIMAL

Table: menu
- id: UUID (Primary Key)
- restaurant_id: UUID (Foreign Key -> restaurants.id)
- food_id: UUID (Foreign Key -> foods.id)
- category_id: UUID (Foreign Key -> categories.id)
- price: DECIMAL

Table: orders
- id: UUID (Primary Key)
- user_id: UUID
- total_amount: DECIMAL
- status: VARCHAR(50)
- created_at: TIMESTAMP

Table: food_orders
- id: UUID (Primary Key)
- order_id: UUID (Foreign Key -> orders.id)
- food_id: UUID (Foreign Key -> foods.id)
- quantity: INTEGER
- price: DECIMAL
```

**API Endpoints**:

| Method | Endpoint                            | Description                  | Auth Required |
| ------ | ----------------------------------- | ---------------------------- | ------------- |
| GET    | `/`                                 | Health check                 | No            |
| GET    | `/health/shards`                    | Shard health status          | No            |
| POST   | `/categories/`                      | Create category              | Yes           |
| GET    | `/categories/`                      | Get all categories           | Yes           |
| GET    | `/categories/{id}`                  | Get category by ID           | Yes           |
| POST   | `/restaurants/`                     | Create restaurant            | Yes           |
| GET    | `/restaurants/`                     | Get all restaurants          | Yes           |
| GET    | `/restaurants/{id}`                 | Get restaurant by ID         | Yes           |
| POST   | `/foods/`                           | Create food item             | Yes           |
| GET    | `/foods/`                           | Get all foods (rate limited) | Yes           |
| GET    | `/foods/{id}`                       | Get food by ID               | Yes           |
| POST   | `/menu/`                            | Create menu item             | Yes           |
| GET    | `/menu/`                            | Get all menus                | Yes           |
| GET    | `/menu/{id}`                        | Get menu by ID               | Yes           |
| GET    | `/menu/restaurants/{restaurant_id}` | Get menus by restaurant ID   | Yes           |
| POST   | `/orders/`                          | Create order                 | Yes           |
| GET    | `/orders/`                          | Get all orders               | Yes           |
| GET    | `/orders/{id}`                      | Get order by ID              | Yes           |
| WS     | `/ws`                               | WebSocket endpoint           | No            |

**Advanced Features**:

- **Database Sharding**: Optional horizontal scaling with multiple database shards
  - Enable with `ENABLE_SHARDING=true` environment variable
  - Automatic table creation on all shards
  - Health check endpoint for shard status
  - Shard-aware query routing
- **Rate Limiting**: Redis-based rate limiting (5 requests per 30 seconds for foods endpoint)
  - Rate limit headers middleware adds `X-RateLimit-*` headers to all responses
  - Configurable via `RATE_LIMIT_ENABLED`, `RATE_LIMIT_MAX_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS`
- **Inter-Service Communication**: HTTP client utility for calling other microservices
  - Generic `fetch_from_service()` function for HTTP requests (GET, POST, PUT, DELETE)
  - Helper functions: `fetch_product()`, `fetch_category()`, `fetch_user()`, `fetch_inventory_item()`
  - Automatic token extraction from cookies
  - Comprehensive error handling with HTTPException
- **WebSocket Support**: Real-time communication for order updates
- **Repository Pattern**: Clean separation of data access logic
- **Service Layer**: Business logic abstraction

**Technologies Used**:

- FastAPI for API framework
- SQLAlchemy with UUID primary keys
- PostgreSQL for data storage
- Redis for caching and rate limiting
- httpx for async HTTP client (inter-service communication)
- WebSocket support for real-time updates
- Alembic for database migrations

---

### 4. Client (React Frontend) ⚠️ Commented in Docker

**Purpose**: Modern React frontend for interacting with all microservices

**Port**: 5173 (development)

**Key Features**:

- TypeScript for type safety
- React Router for navigation
- Axios for API communication
- Tailwind CSS for styling
- Vite for fast development and building
- Context API for state management

**Technologies Used**:

- React 19.2.0
- TypeScript 5.9.3
- Vite 7.2.2
- Tailwind CSS 4.1.17
- React Router DOM 7.9.6
- Axios 1.13.2

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
- **Redis** 7-alpine - Caching and rate limiting
- **Elasticsearch** 8.11.0 - Full-text search engine

### Frontend

- **React** 19.2.0 - UI framework
- **TypeScript** 5.9.3 - Type safety
- **Vite** 7.2.2 - Build tool
- **Tailwind CSS** 4.1.17 - Styling
- **React Router** 7.9.6 - Routing

---

## 🔄 Inter-Service Communication

### Communication Patterns

**1. Synchronous HTTP/REST**:

- Food Service → Auth Service (user details, token validation)
- Food Service → Product Service (product/category details - if needed)
- Booking Service → Auth Service (token validation)
- Uses async httpx client for non-blocking operations
- JWT cookie forwarding for authentication
- Timeout handling (10 seconds)
- Follow redirects enabled
- Generic HTTP client utility in Food Service for inter-service communication

**2. WebSocket (Real-time)**:

- Food Service provides WebSocket endpoint at `/ws`
- Real-time order updates and notifications
- Bidirectional communication

**3. Search Integration**:

- Booking Service → Elasticsearch (full-text search)
- Multi-index search across movies, theaters, showings, bookings
- Async Elasticsearch client

**4. Caching & Rate Limiting**:

- Food Service → Redis (rate limiting and caching)
- Rate limit headers middleware adds `X-RateLimit-*` headers to all responses
- In-memory caching for frequently accessed data

### Service Discovery

**Docker Environment** (Production-like):

```
Services communicate using container names:
- http://auth-service:8000
- http://booking-service:8003
- http://food-service:8004
- http://elasticsearch:9200
- redis://redis:6379
```

**Local Development**:

```
Services communicate using localhost:
- http://localhost:8000 (Auth)
- http://localhost:8003 (Booking)
- http://localhost:8004 (Food)
- http://localhost:9200 (Elasticsearch)
- redis://localhost:6379 (Redis)
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

**Active Services**:

```yaml
Networks:
- microservices-network (bridge driver)

Active Services:
1. auth-service + auth-db (PostgreSQL) ✅
2. booking-service + booking-db (PostgreSQL) ✅
3. elasticsearch ✅
4. redis ✅

Commented Services (can be enabled):
5. food-service + food-db (PostgreSQL) ⚠️
6. client (React frontend) ⚠️

Note: Product Service and Inventory Service have been removed. Their functionality (httpx usage patterns, rate limiting) has been integrated into Food Service.

Volumes:
- auth-db-data (persistent storage)
- booking-db-data (persistent storage)
- elasticsearch-data (persistent storage)
- redis-data (persistent storage)
- food-db-data (commented)
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
  - ./booking-service:/app
  - ./food-service:/app
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

Booking Service:
- POSTGRES_DB=booking_service
- POSTGRES_HOST=booking-db
- ELASTICSEARCH_HOST=elasticsearch
- ELASTICSEARCH_PORT=9200
- ELASTICSEARCH_URL=http://elasticsearch:9200

Food Service (commented):
- POSTGRES_DB=food_service
- POSTGRES_HOST=food-db
- REDIS_URL=redis://redis:6379
- AUTH_SERVICE_URL=http://auth-service:8000 (for inter-service calls)
- PRODUCT_SERVICE_URL=http://product-service:8001 (optional, if needed)
- INVENTORY_SERVICE_URL=http://inventory-service:8002 (optional, if needed)
- RATE_LIMIT_ENABLED=true (default)
- RATE_LIMIT_MAX_REQUESTS=100 (default)
- RATE_LIMIT_WINDOW_SECONDS=60 (default)
- ENABLE_SHARDING=false (set to true for sharding)
```

---

## 📊 Database Migrations (Alembic)

**Auth Service, Booking Service, and Food Service** use Alembic for schema management.

### Migration Files

**Auth Service**:

- `b573df09ec59_initial_migration.py` - Initial users table
- `746836963f64_token_added_in_user_table.py` - Token field added
- `840c09b4f9e0_token_removed.py` - Token field removed

**Booking Service**:

- Manages theaters, movies, showings, seats, bookings, and booking_seats tables

**Food Service**:

- Manages categories, restaurants, foods, menu, orders, and food_orders tables

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
# Terminal 1 - Auth Service
cd auth-service && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2 - Booking Service
cd booking-service && source venv/bin/activate && uvicorn main:app --reload --port 8003

# Terminal 3 - Food Service (if enabled)
cd food-service && source venv/bin/activate && uvicorn main:app --reload --port 8004

# Terminal 4 - Client (React Frontend)
cd client && npm run dev
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
- `booking-service/app.log`
- `food-service/app.log`

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

   - Database access abstraction (Booking Service, Food Service)
   - Dependency injection via FastAPI's Depends()

3. **Service Layer Pattern**

   - Business logic separation (Booking Service, Food Service)
   - Clean architecture principles

4. **Middleware Pattern**

   - CORS middleware
   - Authentication middleware (can be enabled globally)

5. **Lifespan Events**

   - Database initialization on startup
   - Elasticsearch index creation (Booking Service)
   - Redis connection management (Food Service)
   - Graceful connection cleanup on shutdown

6. **Request/Response Pattern**

   - Pydantic schemas for validation
   - Clear separation of models and schemas

7. **Database Sharding Pattern** (Food Service - Optional)
   - Horizontal scaling support
   - Shard-aware routing
   - Health monitoring per shard

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

**3. Create Booking** (Booking Service):

```bash
POST http://localhost:8003/bookings/
Cookie: access_token=<jwt_token>
Body: {
  "showing_id": "uuid-here",
  "seats_ids": ["uuid1", "uuid2"],
  "total_price": 25.99
}
Response: Booking with booking_number and status
```

**4. Search** (Booking Service - Elasticsearch):

```bash
GET http://localhost:8003/search/?query=action&indices=movies,theaters
Cookie: access_token=<jwt_token>
Response: Search results from specified indices
```

**5. Create Food Order** (Food Service):

```bash
POST http://localhost:8004/orders/
Cookie: access_token=<jwt_token>
Body: {
  "foods": [
    {"food_id": "uuid-here", "quantity": 2}
  ],
  "total_amount": 29.98
}
Response: Order with user association
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
├── booking-service/
│   ├── alembic/              # Database migrations
│   ├── api/v1/routes/        # API routes (theaters, movies, showings, etc.)
│   ├── core/                 # Elasticsearch client, utils
│   ├── models/               # SQLAlchemy models (Theater, Movie, Booking, etc.)
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic layer
│   ├── repository/           # Data access layer
│   ├── venv/                 # Virtual environment
│   ├── main.py               # Application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Container definition
│   └── Booking_Service.postman_collection.json
│
├── food-service/
│   ├── alembic/              # Database migrations
│   ├── api/v1/routes/        # API routes (categories, restaurants, foods, etc.)
│   ├── core/                 # Redis client, sharding, rate limiter, WebSocket, HTTP client
│   │   ├── http_client.py    # Inter-service HTTP communication utility
│   │   ├── rate_limiter.py   # Rate limiting with headers middleware
│   │   ├── rate_limit_config.py  # Rate limit configuration
│   │   └── ...               # Other core utilities
│   ├── models/               # SQLAlchemy models (Category, Restaurant, Food, etc.)
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic layer
│   ├── repository/           # Data access layer
│   ├── venv/                 # Virtual environment
│   ├── main.py               # Application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Container definition
│   └── RATE_LIMITER_EXPLANATION.md
│
├── client/
│   ├── src/                  # React source code
│   │   ├── api/              # API clients
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── context/          # Context providers
│   │   └── utils/            # Utility functions
│   ├── public/               # Static assets
│   ├── package.json          # Dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── tailwind.config.js    # Tailwind configuration
│   └── Dockerfile            # Container definition
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
5. ✅ **Inter-Service Communication** - HTTP client with httpx, async operations
6. ✅ **Docker Containerization** - Multi-container setup with compose
7. ✅ **Database Migrations** - Schema versioning with Alembic
8. ✅ **Error Handling** - Comprehensive exception management
9. ✅ **Logging** - Structured logging across services
10. ✅ **API Documentation** - Auto-generated with OpenAPI/Swagger
11. ✅ **Dependency Injection** - FastAPI's Depends system
12. ✅ **Environment Configuration** - Secure config management
13. ✅ **Type Safety** - Pydantic validation
14. ✅ **Async Programming** - Async/await for I/O operations
15. ✅ **Elasticsearch Integration** - Full-text search across multiple indices
16. ✅ **Redis Integration** - Caching and rate limiting
17. ✅ **WebSocket Support** - Real-time communication
18. ✅ **Repository Pattern** - Clean data access layer
19. ✅ **Service Layer Pattern** - Business logic separation
20. ✅ **Database Sharding** - Optional horizontal scaling
21. ✅ **Rate Limiting** - Redis-based request throttling with configurable headers
22. ✅ **HTTP Client Utility** - Reusable inter-service communication patterns
23. ✅ **React Frontend** - Modern TypeScript-based UI

---

## 🚧 Known Limitations & Future Improvements

### Current Limitations

1. **No Circuit Breaker** - Service failures not isolated
2. **No Message Queue** - Only synchronous communication (WebSocket available in Food Service)
3. **Limited Caching** - Redis used for rate limiting, not general caching
4. **Partial Rate Limiting** - Implemented in Food Service with configurable headers middleware
5. **Basic Logging** - No centralized log aggregation
6. **No Monitoring** - No metrics collection
7. **No Service Mesh** - Manual service discovery
8. **No API Gateway** - Direct service access
9. **Some Services Commented** - Food Service and Client commented in docker-compose

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
- `auth-service/README.md` - Auth service details
- `food-service/RATE_LIMITER_EXPLANATION.md` - Rate limiter implementation details

### External References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [JWT Introduction](https://jwt.io/introduction)

---

## 🎉 Summary

This project demonstrates a **comprehensive microservices architecture** with:

- ✅ 3 independent services (Auth, Booking, Food)
- ✅ 3 separate PostgreSQL databases (one per service)
- ✅ React frontend with TypeScript
- ✅ JWT-based authentication with secure password hashing
- ✅ Inter-service HTTP communication using httpx (Food Service)
- ✅ WebSocket support for real-time updates (Food Service)
- ✅ Elasticsearch integration for full-text search (Booking Service)
- ✅ Redis for caching and rate limiting (Food Service)
- ✅ Rate limit headers middleware (Food Service)
- ✅ Docker containerization with compose
- ✅ Database migrations with Alembic
- ✅ Optional database sharding (Food Service)
- ✅ Repository and Service layer patterns
- ✅ Comprehensive error handling and logging
- ✅ Auto-generated API documentation
- ✅ Type-safe validation with Pydantic
- ✅ Rate limiting implementation with configurable headers

**Active Services**: Auth Service, Booking Service, Elasticsearch, Redis
**Available Services** (commented in docker-compose): Food Service, Client

**Note**: Product Service and Inventory Service have been removed. Their key functionality (httpx usage patterns, rate limiting configuration, and HTTP client utilities) has been integrated into Food Service.

**Perfect for**: Learning microservices, building MVPs, understanding distributed systems, implementing search functionality, real-time applications, or as a template for larger projects.

---

**Last Updated**: January 2025
**Project Status**: Active Development
**License**: MIT
