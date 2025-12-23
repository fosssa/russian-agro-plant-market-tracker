# russian-agro-plant-market-tracker
Сервис по сбору и анализу данных по емкости предложения, предлагаемой конкретной компанией и цен предложения в России по отрасли "Сельское хозяйство и пищевая промышленность" в товарной группе "Растениеводство"


This project uses Docker Compose to orchestrate both backend (FastAPI) and frontend (Vite + React) services.

## Project Structure

```
agro_frontend/
├── docker-compose.yml          # Main orchestration file (launches both services)
├── .env                        # Environment variables (git-ignored) - SINGLE SOURCE OF TRUTH
├── .env.example                # Environment template
├── backend/
│   ├── docker/
│   │   └── Dockerfile          # Backend-specific Docker build
│   ├── .dockerignore           # Backend build exclusions
│   └── (backend source files)
└── frontend/
    ├── docker/
    │   ├── Dockerfile          # Frontend-specific Docker build
    │   ├── nginx.conf          # Nginx configuration
    │   └── entrypoint.sh       # Container startup script
    ├── .dockerignore           # Frontend build exclusions
    └── (frontend source files)
```

**Note**: Both services share the **same `.env` file** located at the project root. There are no `.env` files in backend/ or frontend/ folders.

## Quick Start

### 1. Configure Environment

Copy the example environment file and update credentials:

```bash
# From project root
cp .env.example .env

# Edit .env and update:
# - BASIC_AUTH_USER (default: admin)
# - BASIC_AUTH_PASSWORD (default: changeme)
```

### 2. Build and Launch

From the **project root** directory:

```bash
# Build and start both services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 3. Access Services

- **Frontend**: http://localhost:7073
  - Username: `admin` (or your BASIC_AUTH_USER)
  - Password: `changeme` (or your BASIC_AUTH_PASSWORD)
- **Backend API**: http://localhost:7000
- **API Docs**: http://localhost:7000/docs
- **Health Checks**:
  - Backend: http://localhost:7000/healthcheck
  - Frontend: http://localhost:7073/health (no auth required)

## Architecture

### Services

| Service | Port | Technology | Docker Context |
|---------|------|------------|----------------|
| Backend | 7000 | FastAPI + Python + uv | `./backend` |
| Frontend | 7073 | Vite + React + nginx | `./frontend` |

### Network

Both services run on a shared Docker network `agro-network`, allowing:
- Frontend to reach backend at `http://backend:7000`
- Isolated communication between containers
- DNS-based service discovery

### Volumes

- `agro-db-data`: Persists SQLite database across container restarts

## Common Operations

### View Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 50 lines
docker-compose logs --tail=50
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart frontend
docker-compose restart backend
```

### Rebuild After Code Changes

```bash
# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

docker-compose build frontend
docker-compose up -d frontend

# Or rebuild everything
docker-compose up --build
```

### Stop Services

```bash
# Stop containers (data preserved)
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v
```

### Access Container Shell

```bash
# Backend
docker-compose exec backend sh

# Frontend
docker-compose exec frontend sh
```

## Environment Variables

- Single `.env` at project root is shared by backend and frontend (no per-service `.env` files).
- See `docs/ENV.md` for the full list of variables, defaults, and purpose.

## Development Workflow

### Backend Development

The backend Dockerfile is located in `backend/docker/Dockerfile`:
- Uses multi-stage build with `uv` for dependency management
- Python 3.12 slim base image
- Optimized for production deployment

For backend-specific Docker operations:

```bash
# Build backend only
docker-compose build backend

# View backend logs
docker-compose logs -f backend

# Access backend shell
docker-compose exec backend sh
```

### Frontend Development

The frontend Dockerfile is located in `frontend/docker/Dockerfile`:
- Multi-stage build: Node.js (builder) + nginx:alpine (production)
- Compiles Vite application to static assets
- Serves via nginx with basic authentication

For frontend-specific Docker operations:

```bash
# Build frontend only
docker-compose build frontend

# View frontend logs
docker-compose logs -f frontend

# Access frontend shell
docker-compose exec frontend sh

# Check nginx config
docker-compose exec frontend nginx -T
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs for errors
docker-compose logs

# Verify configuration
docker-compose config

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Port Conflicts

If ports 7000 or 7073 are in use:

```bash
# Windows
netstat -ano | findstr :7000
netstat -ano | findstr :7073

# Update .env and docker-compose.yml accordingly
```

### Authentication Issues (Frontend)

```bash
# Verify credentials are set
docker-compose exec frontend env | grep BASIC_AUTH

# Check htpasswd file
docker-compose exec frontend cat /etc/nginx/auth/.htpasswd

# Restart to regenerate
docker-compose restart frontend
```

### Backend-Frontend Communication Issues

```bash
# Verify both services are on same network
docker network inspect agro-network

# Test connectivity from frontend to backend
docker-compose exec frontend wget -O- http://backend:7000/healthcheck
```

### Database Issues

```bash
# Check database file exists
docker-compose exec backend ls -la /app/app.db

# Reinitialize database (WARNING: deletes data)
docker-compose exec backend python init_db.py

# Backup database
docker cp agro-backend:/app/app.db ./backup-$(Get-Date -Format "yyyyMMdd-HHmmss").db
```

## Production Deployment

### Security Checklist

- [ ] Update `BASIC_AUTH_PASSWORD` to strong password
- [ ] Set specific `ALLOWED_ORIGINS` (not `*`)
- [ ] Configure HTTPS/SSL termination (reverse proxy)
- [ ] Use secrets management (not .env file)
- [ ] Regular security updates for base images
- [ ] Set `DEBUG=false` and `APP_ENV=production`

### Performance Optimization

```yaml
# Add resource limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Monitoring

```bash
# View resource usage
docker stats

# Check health status
docker-compose ps
```

## Additional Documentation

- Backend Docker: `backend/docker/README.md`
- Frontend Quick Guide: `backend/FRONTEND_DOCKER_SETUP.md` (legacy location)
- API Documentation: http://localhost:7000/docs (when running)

## Support

For issues:
1. Check service logs: `docker-compose logs -f [service]`
2. Verify health: `docker-compose ps`
3. Review configuration: `docker-compose config`
4. Consult service-specific README files

## License

[Your License Here]
