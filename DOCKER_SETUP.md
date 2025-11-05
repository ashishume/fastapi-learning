# Docker Setup Guide

This guide explains how to run all FastAPI microservices using Docker and Docker Compose.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)

## Services Overview

The application consists of 3 microservices, each with its own PostgreSQL database:

| Service           | Port | Database Port | Description                        |
| ----------------- | ---- | ------------- | ---------------------------------- |
| auth-service      | 8000 | 5432          | Authentication and user management |
| product-service   | 8001 | 5433          | Product and category management    |
| inventory-service | 8002 | 5434          | Inventory management               |

## Quick Start

### 1. Start All Services

From the project root directory, run:

```bash
docker-compose up -d
```

This command will:

- Build Docker images for all services
- Create and start all containers
- Set up the network for inter-service communication
- Create persistent volumes for databases

### 2. View Running Containers

```bash
docker-compose ps
```

### 3. View Logs

View logs for all services:

```bash
docker-compose logs -f
```

View logs for a specific service:

```bash
docker-compose logs -f auth-service
docker-compose logs -f product-service
docker-compose logs -f inventory-service
```

### 4. Stop All Services

```bash
docker-compose down
```

To stop and remove volumes (database data):

```bash
docker-compose down -v
```

## Access Services

Once all services are running, you can access them at:

- **Auth Service**: http://localhost:8000

  - API Docs: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

- **Product Service**: http://localhost:8001

  - API Docs: http://localhost:8001/docs
  - ReDoc: http://localhost:8001/redoc

- **Inventory Service**: http://localhost:8002
  - API Docs: http://localhost:8002/docs
  - ReDoc: http://localhost:8002/redoc

## Database Access

You can connect to the PostgreSQL databases using these credentials:

`docker exec -it product-db psql -U postgres -d product_service`

`docker exec -it auth-db psql -U postgres -d auth_service`

`docker exec -it inventory-db psql -U postgres -d inventory_service`

### Auth Service Database

- Host: localhost
- Port: 5432
- Database: auth_service
- User: postgres
- Password: admin

### Product Service Database

- Host: localhost
- Port: 5433
- Database: product_service
- User: postgres
- Password: admin

### Inventory Service Database

- Host: localhost
- Port: 5434
- Database: inventory_service
- User: postgres
- Password: admin

## Common Docker Commands

### Build Services

Rebuild all services:

```bash
docker-compose build
```

Rebuild a specific service:

```bash
docker-compose build auth-service
```

Rebuild without cache:

```bash
docker-compose build --no-cache
```

### Start/Stop Services

Start all services:

```bash
docker-compose up -d
```

Start specific services:

```bash
docker-compose up -d auth-service product-service
```

Stop all services:

```bash
docker-compose stop
```

Stop specific service:

```bash
docker-compose stop auth-service
```

Restart services:

```bash
docker-compose restart
```

### Execute Commands in Containers

Open a shell in a container:

```bash
docker-compose exec auth-service sh
```

Run a command in a container:

```bash
docker-compose exec auth-service python -c "print('Hello')"
```

### Database Migrations

Run Alembic migrations for auth-service:

```bash
docker-compose exec auth-service alembic upgrade head
```

Run Alembic migrations for product-service:

```bash
docker-compose exec product-service alembic upgrade head
```

Create a new migration:

```bash
docker-compose exec auth-service alembic revision --autogenerate -m "description"
```

## Troubleshooting

### Service won't start

1. Check logs:

```bash
docker-compose logs auth-service
```

2. Ensure no port conflicts:

```bash
lsof -i :8000  # Check if port is already in use
```

3. Rebuild the service:

```bash
docker-compose build auth-service
docker-compose up -d auth-service
```

### Database connection issues

1. Check if database is healthy:

```bash
docker-compose ps
```

2. Wait for database to be ready (healthcheck):

```bash
docker-compose logs auth-db
```

3. Test database connection:

```bash
docker-compose exec auth-db psql -U postgres -d auth_service
```

### Clear all data and restart

```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up -d --build
```

## Development Mode

The services are configured with volume mounts, so code changes will automatically reload:

- Edit your Python files locally
- The changes are synced to the container
- Uvicorn will automatically reload the application

## Production Considerations

For production deployment, consider:

1. **Remove `--reload` flag** from Dockerfiles (CMD line)
2. **Use environment files** instead of hardcoded values
3. **Set strong passwords** for databases
4. **Use secrets management** for sensitive data
5. **Configure proper logging** and monitoring
6. **Set resource limits** in docker-compose.yml
7. **Use Docker swarm or Kubernetes** for orchestration
8. **Implement health checks** for load balancers
9. **Use multi-stage builds** to reduce image size
10. **Scan images** for security vulnerabilities

## Environment Variables

Each service can be configured using environment variables. See the `env.example` files in each service directory:

- `auth-service/env.example`
- `product-service/env.example`
- `inventory-service/env.example`

## Network Configuration

All services are connected to a custom bridge network called `microservices-network`. This allows services to communicate with each other using their service names as hostnames.

Example: From product-service, you can reach auth-service at `http://auth-service:8000`

## Volume Management

Persistent volumes are created for each database:

- `auth-db-data`: Auth service database data
- `product-db-data`: Product service database data
- `inventory-db-data`: Inventory service database data

To backup a database:

```bash
docker-compose exec auth-db pg_dump -U postgres auth_service > backup.sql
```

To restore a database:

```bash
cat backup.sql | docker-compose exec -T auth-db psql -U postgres auth_service
```

## Support

For issues or questions, please refer to the individual service README files or check the application logs.
