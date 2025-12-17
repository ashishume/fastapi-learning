# Nginx Reverse Proxy Setup

This nginx configuration acts as a reverse proxy for all microservices, providing a single entry point for all API requests.

## Quick Start

### 1. Start all services with Docker Compose

```bash
# From the project root directory
docker-compose up -d
```

This will start:

- All backend services (auth, booking, etc.)
- Databases
- Redis
- Elasticsearch
- **Nginx** (on port 80)

### 2. Access services through Nginx

Once running, you can access all services through nginx on port 80:

- **Frontend**: http://localhost/
- **Auth Service**: http://localhost/auth/
- **Booking Service**: http://localhost/booking/
- **Product Service**: http://localhost/product/ (when enabled)
- **Inventory Service**: http://localhost/inventory/ (when enabled)
- **Food Service**: http://localhost/food/ (when enabled)

### 3. API Documentation

Each service's API docs are available at:

- Auth: http://localhost/auth/docs
- Booking: http://localhost/booking/docs
- Product: http://localhost/product/docs (when enabled)
- Inventory: http://localhost/inventory/docs (when enabled)
- Food: http://localhost/food/docs (when enabled)

### 4. Health Check

Check if nginx is running:

```bash
curl http://localhost/health
```

## Running Individual Services

If you want to run services individually (not through nginx):

- Auth Service: http://localhost:8000
- Booking Service: http://localhost:8003
- Product Service: http://localhost:8001 (when enabled)
- Inventory Service: http://localhost:8002 (when enabled)
- Food Service: http://localhost:8004 (when enabled)

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Viewing Logs

```bash
# View nginx logs
docker logs nginx

# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f auth-service
docker-compose logs -f booking-service
```

## Troubleshooting

### Nginx can't connect to services

1. Check if services are running:

   ```bash
   docker-compose ps
   ```

2. Verify services are on the same network:

   ```bash
   docker network inspect fastapi-learning_microservices-network
   ```

3. Test service connectivity from nginx container:
   ```bash
   docker exec -it nginx sh
   # Inside container:
   wget -O- http://auth-service:8000/
   ```

### Port 80 already in use

If port 80 is already in use, change the nginx port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8080:80" # Use port 8080 instead
```

Then access via: http://localhost:8080

### Service not responding

1. Check service health:

   ```bash
   curl http://localhost/auth/
   curl http://localhost/booking/
   ```

2. Check nginx error logs:

   ```bash
   docker logs nginx
   ```

3. Verify nginx configuration:
   ```bash
   docker exec -it nginx nginx -t
   ```

## Enabling Commented Services

To enable product, inventory, or food services:

1. Uncomment the service blocks in `docker-compose.yml`
2. Uncomment the corresponding database services
3. Restart docker-compose:
   ```bash
   docker-compose up -d
   ```

The nginx configuration already includes routing for all services, so no changes needed there.
