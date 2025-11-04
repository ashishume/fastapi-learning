# FastAPI Microservices Project

This project demonstrates a microservices architecture using FastAPI, where two independent services communicate with each other via HTTP/REST APIs.

## 📁 Project Structure

```
Fast-api/
├── fastapi_learning/          # Main Service (Port 8000)
│   ├── api/
│   │   ├── auth/              # Authentication endpoints
│   │   └── endpoints/         # Items & Categories endpoints
│   ├── core/                  # Database & utilities
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   └── main.py                # Main application
│
├── inventory-service/         # Inventory Service (Port 8001)
│   ├── api/
│   │   ├── inventory.py       # Inventory endpoints
│   │   └── integration.py     # Integration with main service
│   ├── services/
│   │   └── fastapi_client.py  # Client for calling main service
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   └── main.py                # Main application
│
├── MICROSERVICES_GUIDE.md     # Detailed architecture guide
├── QUICKSTART.md              # Quick start instructions
├── setup_microservices.sh     # Setup script
├── test_microservices.py      # Test script
└── Microservices.postman_collection.json  # Postman collection
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
./setup_microservices.sh
```

### 2. Start Services

**Terminal 1 - Main Service:**

```bash
cd fastapi_learning
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Inventory Service:**

```bash
cd inventory-service
source venv/bin/activate
uvicorn main:app --reload --port 8001
```

### 3. Test Communication

```bash
python3 test_microservices.py
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client / Browser                      │
└────────────┬───────────────────────┬────────────────────┘
             │                       │
             ▼                       ▼
   ┌─────────────────┐    ┌──────────────────┐
   │ fastapi_learning│    │ inventory-service│
   │   Port: 8000    │◄───│   Port: 8001     │
   └─────────────────┘    └──────────────────┘
             │                       │
             ▼                       ▼
   ┌─────────────────┐    ┌──────────────────┐
   │  PostgreSQL DB  │    │  PostgreSQL DB   │
   │   (main_db)     │    │   (inventory_db) │
   └─────────────────┘    └──────────────────┘
```

### Communication Flow

1. **Direct Client Requests**: Clients can call either service directly
2. **Inter-Service Communication**: Inventory service can call main service via HTTP
3. **Service Client**: Uses `FastAPILearningClient` for type-safe communication

## 🔑 Key Features

### Main Service (fastapi_learning)

- ✅ User authentication (JWT)
- ✅ Items management
- ✅ Categories management
- ✅ PostgreSQL database
- ✅ Alembic migrations

### Inventory Service

- ✅ Inventory management
- ✅ Integration with main service
- ✅ Category validation from main service
- ✅ Async HTTP client
- ✅ Health check endpoints

### Inter-Service Communication

- ✅ HTTP/REST API calls
- ✅ Async operations with httpx
- ✅ Error handling and retries
- ✅ Service health monitoring
- ✅ Type-safe client library

## 📚 Documentation

| Document                                                    | Description                      |
| ----------------------------------------------------------- | -------------------------------- |
| [QUICKSTART.md](QUICKSTART.md)                              | Get started in 5 minutes         |
| [MICROSERVICES_GUIDE.md](MICROSERVICES_GUIDE.md)            | Comprehensive architecture guide |
| [Postman Collection](Microservices.postman_collection.json) | API testing collection           |

## 🔗 API Endpoints

### Main Service (http://localhost:8000)

| Endpoint         | Method   | Description           |
| ---------------- | -------- | --------------------- |
| `/`              | GET      | Health check          |
| `/items`         | GET/POST | Items management      |
| `/categories`    | GET/POST | Categories management |
| `/auth/register` | POST     | User registration     |
| `/auth/login`    | POST     | User login            |

### Inventory Service (http://localhost:8001)

| Endpoint                                  | Method   | Description                               |
| ----------------------------------------- | -------- | ----------------------------------------- |
| `/`                                       | GET      | Health check                              |
| `/inventory`                              | GET/POST | Inventory management                      |
| `/inventory/with-validation`              | POST     | Create inventory with category validation |
| `/inventory/categories/from-main-service` | GET      | Get categories from main service          |
| `/integration/items`                      | GET      | Get items from main service               |
| `/integration/categories`                 | GET      | Get categories from main service          |
| `/integration/health/main-service`        | GET      | Check main service health                 |

## 🧪 Testing

### Automated Test Script

```bash
python3 test_microservices.py
```

### Manual Testing with cURL

**Test Health:**

```bash
curl http://localhost:8001/integration/health/main-service
```

**Get Categories:**

```bash
curl http://localhost:8001/integration/categories
```

**Create Inventory with Validation:**

```bash
curl -X POST http://localhost:8001/inventory/with-validation \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Laptop",
    "category": "Electronics",
    "quantity_in_stock": 50,
    "unit_price": 999.99,
    "last_restock_date": "2024-01-15T10:00:00",
    "supplier": "Tech Supplier Inc",
    "reorder_point": 10
  }'
```

### Postman Collection

Import `Microservices.postman_collection.json` into Postman for easy API testing.

## 💻 Code Examples

### Calling Main Service from Inventory Service

```python
from services.fastapi_client import FastAPILearningClient
from fastapi import Depends

@router.get("/example")
async def example(client: FastAPILearningClient = Depends()):
    # Get categories from main service
    categories = await client.get_categories()

    # Get items with authentication
    items = await client.get_items(token="jwt_token_here")

    return {"categories": categories, "items": items}
```

### Category Validation Example

```python
# Validate category before creating inventory
category = await client.get_category_by_name(category_name)
if category:
    # Category exists in main service
    # Proceed with inventory creation
    ...
```

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Language**: Python 3.14
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **HTTP Client**: httpx
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic

## 📈 Use Cases

### 1. Data Validation Across Services

Validate inventory categories against the main service's categories.

### 2. Data Aggregation

Combine inventory data with item details from the main service.

### 3. Service Health Monitoring

Monitor the health of dependent services.

### 4. Centralized Authentication

Use authentication from the main service across all microservices.

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

Run both services locally on different ports.

### Production Options

**Option 1: Traditional Deployment**

- Deploy each service to separate servers
- Use nginx as reverse proxy
- Configure service discovery

**Option 2: Docker**

```bash
# Build and run with docker-compose
docker-compose up -d
```

**Option 3: Kubernetes**

```bash
# Deploy to Kubernetes cluster
kubectl apply -f k8s/
```

## 📊 Monitoring & Observability

### Current Setup

- ✅ Logging with Python logging module
- ✅ Health check endpoints

### Future Enhancements

- 🔲 Prometheus metrics
- 🔲 Grafana dashboards
- 🔲 Distributed tracing (Jaeger)
- 🔲 ELK stack for log aggregation
- 🔲 APM (Application Performance Monitoring)

## 🎯 Roadmap

### Phase 1: Basic Communication (✅ Complete)

- ✅ HTTP client implementation
- ✅ Service-to-service calls
- ✅ Error handling
- ✅ Documentation

### Phase 2: Advanced Features (🔲 TODO)

- 🔲 Circuit breaker pattern
- 🔲 Service mesh (Istio)
- 🔲 Message queue (RabbitMQ/Kafka)
- 🔲 Event-driven architecture
- 🔲 API Gateway (Kong/Traefik)

### Phase 3: DevOps (🔲 TODO)

- 🔲 Docker containerization
- 🔲 Kubernetes orchestration
- 🔲 CI/CD pipeline
- 🔲 Infrastructure as Code (Terraform)

### Phase 4: Production Ready (🔲 TODO)

- 🔲 Comprehensive monitoring
- 🔲 Distributed tracing
- 🔲 Auto-scaling
- 🔲 Disaster recovery
- 🔲 Multi-region deployment

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

**Happy Microservicing! 🎉**

For detailed information, refer to:

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [MICROSERVICES_GUIDE.md](MICROSERVICES_GUIDE.md) - Comprehensive guide
