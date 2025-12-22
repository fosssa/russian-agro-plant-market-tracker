# Docker Setup Documentation

This document provides instructions for running the FastAPI backend and frontend applications using Docker.

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher

## Project Structure

```
project-root/
├── backend/
│   ├── docker-compose.yml          # Service orchestration configuration
│   ├── docker/
│   │   ├── Dockerfile              # Backend multi-stage build
│   │   ├── Dockerfile.frontend     # Frontend multi-stage build
│   │   ├── nginx.conf              # Nginx configuration for frontend
│   │   └── entrypoint.sh           # Frontend container entrypoint
│   ├── .env                        # Environment variables (git-ignored)
│   ├── .env.example                # Environment variables template
│   └── .dockerignore               # Build context exclusions
└── frontend/
    └── (Vite application files)
```

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and customize as needed:

```bash
# Copy template
cp .env.example .env

# Edit .env with your preferred editor
# The default values are suitable for development
```

### 2. Build and Start Services

```bash
# Build the Docker image and start the container
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the Application

- **Frontend**: http://localhost:7073 (requires basic authentication)
  - Default username: `admin`
  - Default password: `changeme`
- **Backend API Base URL**: http://localhost:7000
- **Health Check (Backend)**: http://localhost:7000/healthcheck
- **Health Check (Frontend)**: http://localhost:7073/health (no authentication required)
- **API Documentation**: http://localhost:7000/docs (FastAPI auto-generated Swagger UI)
- **ReDoc**: http://localhost:7000/redoc

## Docker Commands Reference

### Service Management

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v

# Restart services
docker-compose restart

# View service status and health
docker-compose ps
```

### Building and Updating

```bash
# Rebuild images (after code changes)
docker-compose build

# Rebuild without cache (force fresh build)
docker-compose build --no-cache

# Pull latest base images and rebuild
docker-compose build --pull
```

### Logs and Monitoring

```bash
# View logs from all services
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# View last 100 lines
docker-compose logs --tail=100
```

### Container Access

```bash
# Execute commands in running container
docker-compose exec backend sh
docker-compose exec frontend sh

# Run one-off commands
docker-compose run --rm backend python db_operations.py init

# Check health status
docker-compose exec backend curl http://localhost:7000/healthcheck
docker-compose exec frontend wget -O- http://localhost:7073/health
```

### Database Management

#### CLI Commands

```bash
# Initialize database tables
docker-compose exec backend python db_operations.py init

# Initialize and seed with sample data
docker-compose exec backend python db_operations.py seed

# Drop all tables (with confirmation prompt)
docker-compose exec backend python db_operations.py drop

# Reset database (drop, recreate, and seed with confirmation)
docker-compose exec backend python db_operations.py reset
```

#### API Endpoints

Alternatively, use the utility API endpoints:

```bash
# Initialize database
curl -X POST http://localhost:7000/utility/init

# Seed database
curl -X POST http://localhost:7000/utility/seed

# Drop all tables (requires confirmation)
curl -X DELETE http://localhost:7000/utility/drop \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'

# Reset database (requires confirmation)
curl -X POST http://localhost:7000/utility/reset \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

#### Database Backup

```bash
docker cp agro-backend:/app/app.db ./backup-$(date +%Y%m%d-%H%M%S).db

# Access database file via volume
docker volume inspect agro-db-data
```

## Environment Variables

See `docs/ENV.md` for the authoritative list of variables, defaults, and usage. `.env.example` provides non-secret defaults; do not commit secrets to `.env`.

## Network Configuration

The setup creates a custom Docker network `agro-network` for service isolation and communication.

```bash
# Inspect network
docker network inspect agro-network

# View connected containers
docker network inspect agro-network --format '{{range .Containers}}{{.Name}} {{end}}'
```

## Volume Management

### Database Volume

The SQLite database is persisted in a named volume `agro-db-data`.

```bash
# List volumes
docker volume ls

# Inspect database volume
docker volume inspect agro-db-data

# Backup volume data
docker run --rm -v agro-db-data:/data -v $(pwd):/backup alpine tar czf /backup/db-backup.tar.gz /data

# Restore volume data
docker run --rm -v agro-db-data:/data -v $(pwd):/backup alpine tar xzf /backup/db-backup.tar.gz -C /
```

## Health Checks

### Backend Health Check

The backend container includes automatic health monitoring:

- **Endpoint**: `/healthcheck`
- **Interval**: Every 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 attempts
- **Start Period**: 40 seconds grace period

### Frontend Health Check

The frontend container includes automatic health monitoring:

- **Endpoint**: `/health` (no authentication required)
- **Interval**: Every 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 attempts
- **Start Period**: 20 seconds grace period

Check health status:

```bash
# Via Docker Compose
docker-compose ps

# Via Docker CLI
docker inspect --format='{{.State.Health.Status}}' agro-backend

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' agro-backend
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose config

# Check build errors
docker-compose build --no-cache
```

### Health check failing

```bash
# Check application logs
docker-compose logs -f backend

# Manually test health endpoint
docker-compose exec backend curl -v http://localhost:7000/healthcheck

# Verify port is accessible
curl http://localhost:7000/healthcheck
```

### Database issues

```bash
# Verify database file exists
docker-compose exec backend ls -la /app/app.db

# Reinitialize database (WARNING: deletes data)
docker-compose exec backend python db_operations.py seed

# Check volume mount
docker inspect agro-backend --format='{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'
```

### Port conflicts

If port 7000 is already in use, modify `.env`:

```env
PORT=7001
```

Then update `docker-compose.yml` port mapping:

```yaml
ports:
  - "7001:7001"
```

Similarly for frontend (port 7073), update the nginx.conf and docker-compose.yml accordingly.

### Frontend Authentication Issues

If you cannot access the frontend due to authentication:

```bash
# Check if htpasswd file was created
docker-compose exec frontend cat /etc/nginx/auth/.htpasswd

# Verify environment variables are set
docker-compose exec frontend env | grep BASIC_AUTH

# Check nginx configuration
docker-compose exec frontend nginx -T
```

To change authentication credentials, update `.env` and restart:

```env
BASIC_AUTH_USER=newuser
BASIC_AUTH_PASSWORD=newpassword
```

```bash
docker-compose restart frontend
```

## Production Deployment

### Security Recommendations

1. **Update CORS Origins**: Set specific allowed origins in `.env`
   ```env
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

2. **Use Strong Database**: Migrate from SQLite to PostgreSQL
   ```env
   DATABASE_URL=postgresql://user:password@postgres:5432/agro_db
   ```

3. **Set Production Mode**:
   ```env
   APP_ENV=production
   DEBUG=false
   LOG_LEVEL=warning
   ```

4. **Use Secrets Management**: Store sensitive values securely (AWS Secrets Manager, HashiCorp Vault, etc.)

### Performance Optimization

1. **Scale Workers**: Increase worker count based on CPU cores
   ```env
   WORKERS=4
   ```

2. **Resource Limits**: Add to `docker-compose.yml`
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 2G
       reservations:
         cpus: '1.0'
         memory: 1G
   ```

3. **Use Production ASGI Server**: Consider Gunicorn with Uvicorn workers for better process management

## Development Workflow

### Live Reload (Optional)

For development with live reload, add volume mount in `docker-compose.yml`:

```yaml
volumes:
  - ./:/app  # Mount source code
  - agro-db-data:/app/app.db
```

Then install dependencies in development mode:

```dockerfile
# In Dockerfile builder stage
RUN uv sync --frozen  # Include dev dependencies
```

### Running Tests

```bash
# Run tests in container
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=. --cov-report=html
```

## CI/CD Integration

### Example GitHub Actions

```yaml
- name: Build Docker image
  run: docker-compose build

- name: Run health check
  run: |
    docker-compose up -d
    sleep 10
    curl -f http://localhost:7000/healthcheck || exit 1
    docker-compose down
```

### Example GitLab CI

```yaml
build:
  script:
    - docker-compose build
    - docker-compose up -d
    - docker-compose exec -T backend curl -f http://localhost:7000/healthcheck
    - docker-compose down
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## Support

For issues or questions:
1. Check application logs: `docker-compose logs -f backend`
2. Verify health status: `docker-compose ps`
3. Review environment configuration: `docker-compose config`
4. Consult the main project README for application-specific details
