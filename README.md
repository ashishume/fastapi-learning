# FastAPI Microservices Project

This project demonstrates a microservices architecture using FastAPI, featuring multiple independent services that communicate with each other via HTTP/REST APIs. The project includes authentication, food ordering, booking management, product catalog, and inventory management services.

## 📁 Project Structure

```
fastapi-learning/
├── auth-service/             # Authentication Service (Port 8000)
│   ├── api/auth/              # Authentication endpoints
│   ├── core/                  # Database, middleware, utils
│   ├── models/                # SQLAlchemy models (User)
│   ├── schemas/               # Pydantic schemas
│   ├── alembic/               # Database migrations
│   └── main.py                # Main application
│
├── food-service/              # Food Service (Port 8004)
│   ├── api/v1/routes/         # API routes
│   │   ├── categories.py      # Category endpoints
│   │   ├── restaurants.py     # Restaurant endpoints
│   │   ├── foods.py           # Food items endpoints
│   │   ├── menu.py            # Menu endpoints
│   │   └── orders.py          # Order endpoints
│   ├── services/              # Business logic layer
│   ├── repository/            # Data access layer
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   └── main.py                # Main application
│
├── booking-service/           # Booking Service (Port 8003)
│   ├── api/v1/                # API routes
│   ├── models/                # SQLAlchemy models
│   ├── services/              # Business logic
│   └── main.py                # Main application
│
├── product-service/           # Product Service (Port 8001)
│   ├── api/endpoints/         # Item & Category endpoints
│   ├── core/                  # Database, middleware, rate limiting
│   ├── models/                # SQLAlchemy models
│   └── main.py                # Main application
│
├── inventory-service/         # Inventory Service (Port 8002)
│   ├── api/                   # Inventory endpoints
│   ├── models/                # SQLAlchemy models
│   └── main.py                # Main application
│
├── client/                    # React Frontend
│   ├── src/                   # React source code
│   └── package.json           # Dependencies
│
├── docker-compose.yml         # Multi-service orchestration
├── DOCKER_SETUP.md            # Docker documentation
├── PROJECT_SUMMARY.md          # Comprehensive reference
└── README.md                  # This file
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

Start all services with a single command:

```bash
docker-compose up -d
```

This will start:

- **Auth Service** on `http://localhost:8000`
- **Food Service** on `http://localhost:8004`
- **Redis** on `localhost:6379`
- All required PostgreSQL databases

View logs:

```bash
docker-compose logs -f
```

Stop services:

```bash
docker-compose down
```

### Option 2: Local Development

**Terminal 1 - Auth Service:**

```bash
cd auth-service
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Food Service:**

```bash
cd food-service
source venv/bin/activate
uvicorn main:app --reload --port 8004
```

**Note**: Make sure PostgreSQL databases are running and environment variables are configured.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client / Browser (React)                      │
└────────┬───────────────┬─────────────────┬─────────────────────┘
         │               │                 │
         ▼               ▼                 ▼
   ┌──────────┐   ┌──────────┐    ┌──────────────┐
   │   Auth   │   │  Food    │    │   Booking   │
   │ Service  │   │ Service  │    │   Service   │
   │ Port:8000│   │Port: 8004│    │  Port: 8003  │
   └─────┬────┘   └─────┬────┘    └──────┬───────┘
         │              │                 │
         ▼              ▼                 ▼
   ┌──────────┐   ┌──────────┐    ┌──────────────┐
   │ auth_db  │   │ food_db  │    │ booking_db   │
   │Port: 5435│   │Port: 5437│    │  Port: 5436  │
   └──────────┘   └──────────┘    └──────────────┘
```

### Communication Flow

1. **Client Requests**: React frontend communicates with backend services
2. **Authentication**: All services validate JWT tokens via Auth Service
3. **Inter-Service Communication**: Services communicate via HTTP/REST APIs
4. **Service Isolation**: Each service has its own database
5. **Redis Cache**: Used for rate limiting and caching (product-service)

## 🔑 Key Features

### Auth Service (Port 8000)

- ✅ User registration and authentication
- ✅ JWT token generation and validation
- ✅ Password hashing with bcrypt (SHA-256 pre-hashing)
- ✅ Role-based access control (SUPER_ADMIN, ADMIN, USER, MODERATOR)
- ✅ HTTP-only cookie-based token storage
- ✅ PostgreSQL database with Alembic migrations

### Food Service (Port 8004)

- ✅ **Categories Management**: Create and manage food categories
- ✅ **Restaurants Management**: Restaurant CRUD operations
- ✅ **Foods Management**: Food items with category relationships
- ✅ **Menu Management**: Restaurant menus linking foods, restaurants, and categories
- ✅ **Orders Management**: Food ordering system with user association
- ✅ JWT authentication integration
- ✅ Repository pattern for data access
- ✅ Service layer for business logic
- ✅ PostgreSQL database

### Product Service (Port 8001)

- ✅ Items and categories management
- ✅ Rate limiting with Redis
- ✅ Protected endpoints with JWT
- ✅ Pagination support

### Booking Service (Port 8003)

- ✅ Movie theater booking system
- ✅ Showings and seat management
- ✅ Booking creation and management

### Inventory Service (Port 8002)

- ✅ Inventory tracking and management
- ✅ Integration with Product Service
- ✅ Category validation

### Inter-Service Communication

- ✅ HTTP/REST API calls
- ✅ Async operations with httpx
- ✅ JWT token validation across services
- ✅ Error handling and retries
- ✅ Service health monitoring

## 📚 Documentation

| Document                                                                                      | Description                     |
| --------------------------------------------------------------------------------------------- | ------------------------------- |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)                                                      | Comprehensive project reference |
| [DOCKER_SETUP.md](DOCKER_SETUP.md)                                                            | Docker deployment guide         |
| [auth-service/README.md](auth-service/README.md)                                              | Auth service details            |
| [product-service/README.md](product-service/README.md)                                        | Product service details         |
| [Booking Service Postman Collection](booking-service/Booking_Service.postman_collection.json) | API testing collection          |

## 🔗 API Endpoints

### Auth Service (http://localhost:8000)

| Endpoint       | Method | Description              | Auth Required |
| -------------- | ------ | ------------------------ | ------------- |
| `/`            | GET    | Health check             | No            |
| `/auth/`       | POST   | User registration        | No            |
| `/auth/login`  | POST   | User login (sets cookie) | No            |
| `/auth/logout` | POST   | User logout              | No            |
| `/docs`        | GET    | Swagger UI documentation | No            |

### Food Service (http://localhost:8004)

| Endpoint                            | Method | Description                | Auth Required |
| ----------------------------------- | ------ | -------------------------- | ------------- |
| `/`                                 | GET    | Health check               | No            |
| `/categories/`                      | POST   | Create category            | Yes           |
| `/categories/`                      | GET    | Get all categories         | Yes           |
| `/categories/{id}`                  | GET    | Get category by ID         | Yes           |
| `/restaurants/`                     | POST   | Create restaurant          | Yes           |
| `/restaurants/`                     | GET    | Get all restaurants        | Yes           |
| `/restaurants/{id}`                 | GET    | Get restaurant by ID       | Yes           |
| `/foods/`                           | POST   | Create food item           | Yes           |
| `/foods/`                           | GET    | Get all foods              | Yes           |
| `/foods/{id}`                       | GET    | Get food by ID             | Yes           |
| `/menu/`                            | POST   | Create menu item           | Yes           |
| `/menu/`                            | GET    | Get all menus              | Yes           |
| `/menu/{id}`                        | GET    | Get menu by ID             | Yes           |
| `/menu/restaurants/{restaurant_id}` | GET    | Get menus by restaurant ID | Yes           |
| `/orders/`                          | POST   | Create order               | Yes           |
| `/orders/`                          | GET    | Get all orders             | Yes           |
| `/orders/{id}`                      | GET    | Get order by ID            | Yes           |
| `/docs`                             | GET    | Swagger UI documentation   | No            |

### Product Service (http://localhost:8001)

| Endpoint           | Method | Description            | Auth Required |
| ------------------ | ------ | ---------------------- | ------------- |
| `/`                | GET    | Health check           | No            |
| `/items/`          | GET    | List items (paginated) | Yes           |
| `/items/`          | POST   | Create item            | Yes           |
| `/items/{id}`      | GET    | Get item by ID         | Yes           |
| `/items/{id}`      | PUT    | Update item            | Yes           |
| `/categories/`     | GET    | List categories        | Yes           |
| `/categories/`     | POST   | Create category        | Yes           |
| `/categories/{id}` | GET    | Get category by ID     | Yes           |

### Booking Service (http://localhost:8003)

| Endpoint     | Method | Description    | Auth Required |
| ------------ | ------ | -------------- | ------------- |
| `/`          | GET    | Health check   | No            |
| `/theaters/` | GET    | List theaters  | Yes           |
| `/movies/`   | GET    | List movies    | Yes           |
| `/showings/` | GET    | List showings  | Yes           |
| `/bookings/` | POST   | Create booking | Yes           |
| `/bookings/` | GET    | List bookings  | Yes           |

### Inventory Service (http://localhost:8002)

| Endpoint      | Method | Description      | Auth Required |
| ------------- | ------ | ---------------- | ------------- |
| `/`           | GET    | Health check     | No            |
| `/inventory/` | GET    | List inventory   | Yes           |
| `/inventory/` | POST   | Create inventory | Yes           |

## 🧪 Testing

### API Documentation

All services provide auto-generated interactive documentation:

- **Swagger UI**: `http://localhost:{port}/docs`
- **ReDoc**: `http://localhost:{port}/redoc`

### Manual Testing with cURL

**1. Register a User:**

```bash
curl -X POST http://localhost:8000/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "secure123"
  }'
```

**2. Login (sets cookie):**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "user@example.com",
    "password": "secure123"
  }'
```

**3. Create a Category (Food Service):**

```bash
curl -X POST http://localhost:8004/categories/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Italian",
    "description": "Italian cuisine"
  }'
```

**4. Create a Restaurant:**

```bash
curl -X POST http://localhost:8004/restaurants/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Pizza Palace",
    "address": "123 Main St",
    "phone": "555-1234"
  }'
```

**5. Create a Menu:**

```bash
curl -X POST http://localhost:8004/menu/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "restaurant_id": "uuid-here",
    "food_id": "uuid-here",
    "category_id": "uuid-here",
    "price": 15.99
  }'
```

### Postman Collections

- `Booking_Service.postman_collection.json` - Booking service endpoints
- Import into Postman for easy API testing

## 💻 Code Examples

### Food Service - Menu Creation

```python
from fastapi import APIRouter, Depends, HTTPException
from schemas.menu import MenuCreate, MenuResponse
from services.menu_service import MenuService
from database import get_db

router = APIRouter()

@router.post("/menu/", response_model=MenuResponse)
def create_menu(menu: MenuCreate, db: Session = Depends(get_db)):
    menu_service = MenuService(db)
    return menu_service.create_menu(menu)
```

### Authentication Guard Usage

```python
from core.utils import auth_guard
from fastapi import Depends, Request

@router.post("/orders/")
def create_order(
    order: OrderCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    # User ID is available from request.state.user_id
    user_id = request.state.user_id
    # Create order with user association
    ...
```

### Repository Pattern Example

```python
from repository.menu_repo import MenuRepository
from sqlalchemy.orm import Session

class MenuService:
    def __init__(self, db: Session):
        self.menu_repository = MenuRepository(db)

    def create_menu(self, menu: MenuCreate):
        return self.menu_repository.create_menu(menu)
```

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI 0.120.1
- **Language**: Python 3.14
- **Database**: PostgreSQL 16 (Alpine)
- **ORM**: SQLAlchemy 2.0.23
- **Migrations**: Alembic 1.13.1
- **HTTP Client**: httpx (for inter-service communication)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt + passlib
- **Validation**: Pydantic 2.12.3
- **Caching**: Redis 7 (for rate limiting)

### Frontend

- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Networking**: Custom bridge network for service communication

## 📈 Use Cases

### 1. Food Ordering System

Complete food ordering platform with:

- Restaurant and menu management
- Category-based food organization
- Order creation and tracking
- User authentication and authorization

### 2. Movie Theater Booking

Booking system for:

- Theater and movie management
- Showtime scheduling
- Seat selection and booking
- Booking history tracking

### 3. E-commerce Platform

Product catalog and inventory management:

- Product and category management
- Inventory tracking
- Rate limiting and caching
- Cross-service validation

### 4. Centralized Authentication

JWT-based authentication service used across all microservices:

- User registration and login
- Token generation and validation
- Role-based access control
- Secure password hashing

## 🔒 Security Considerations

### Development

- ✅ CORS enabled for all origins
- ✅ JWT authentication for protected endpoints
- ✅ Password hashing with bcrypt

### Production (TODO)

- 🔲 Configure specific CORS origins
- 🔲 Use HTTPS/TLS
- 🔲 Implement API gateway
- 🔲 Add rate limiting
- 🔲 Service-to-service authentication
- 🔲 Secret management

## 🚀 Deployment

### Development

**Using Docker Compose (Recommended):**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

**Local Development:**

Each service can be run independently:

```bash
cd [service-name]
source venv/bin/activate
uvicorn main:app --reload --port [port]
```

### Production Options

**Option 1: Docker Compose**

- Multi-container orchestration
- Service health checks
- Persistent volumes for databases
- Network isolation

**Option 2: Kubernetes**

- Container orchestration
- Auto-scaling
- Service mesh integration
- Load balancing

**Option 3: Cloud Platforms**

- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## 📊 Monitoring & Observability

### Current Setup

- ✅ Structured logging with Python logging module
- ✅ Log files per service (`app.log`)
- ✅ Health check endpoints (`/`)
- ✅ Auto-generated API documentation (Swagger/ReDoc)
- ✅ Redis health checks (product-service)

### Future Enhancements

- 🔲 Prometheus metrics collection
- 🔲 Grafana dashboards for visualization
- 🔲 Distributed tracing (Jaeger/Zipkin)
- 🔲 ELK stack for centralized log aggregation
- 🔲 APM tools (New Relic, DataDog)
- 🔲 Error tracking (Sentry)

## 🎯 Roadmap

### Phase 1: Core Services (✅ Complete)

- ✅ Auth service with JWT authentication
- ✅ Food service with full CRUD operations
- ✅ Menu management functionality
- ✅ Order management system
- ✅ Docker containerization
- ✅ Inter-service communication
- ✅ Repository and service layer patterns

### Phase 2: Enhanced Features (🔲 TODO)

- 🔲 Circuit breaker pattern for resilience
- 🔲 Message queue (RabbitMQ/Kafka) for async communication
- 🔲 Event-driven architecture
- 🔲 API Gateway (Kong/Traefik)
- 🔲 Service mesh (Istio) for advanced networking

### Phase 3: Observability (🔲 TODO)

- 🔲 Prometheus metrics
- 🔲 Grafana dashboards
- 🔲 Distributed tracing (Jaeger)
- 🔲 Centralized logging (ELK stack)
- 🔲 Error tracking (Sentry)

### Phase 4: Production Readiness (🔲 TODO)

- 🔲 Kubernetes orchestration
- 🔲 CI/CD pipeline (GitHub Actions/GitLab CI)
- 🔲 Infrastructure as Code (Terraform)
- 🔲 Auto-scaling configuration
- 🔲 Disaster recovery plan
- 🔲 Multi-region deployment
- 🔲 Performance testing and optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT License

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

## 📝 Recent Updates

### Food Service - Menu Management (Latest)

- ✅ Added menu endpoints for linking foods to restaurants
- ✅ Menu creation with restaurant, food, and category relationships
- ✅ Get menus by restaurant ID
- ✅ Full CRUD operations for menu items
- ✅ Repository pattern implementation
- ✅ Service layer for business logic

### Architecture Improvements

- ✅ Docker Compose configuration for multi-service deployment
- ✅ Redis integration for caching and rate limiting
- ✅ Improved error handling across services
- ✅ Structured logging implementation

---

**Happy Microservicing! 🎉**

For detailed information, refer to:

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Comprehensive project reference
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker deployment guide
