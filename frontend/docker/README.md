# Frontend Docker Configuration

This directory contains Docker configuration files for the frontend service.

## Files

- **Dockerfile**: Multi-stage build definition
  - Stage 1: Node.js 20 alpine - builds the Vite application
  - Stage 2: nginx:alpine - serves static files with authentication

- **nginx.conf**: Nginx server configuration
  - HTTP Basic Authentication
  - SPA routing (fallback to index.html)
  - gzip compression
  - Security headers
  - Health check endpoint at `/health`

- **entrypoint.sh**: Container startup script
  - Generates `.htpasswd` from environment variables
  - Validates nginx configuration
  - Starts nginx in foreground mode

## Build Context

The Dockerfile expects to be built from the **frontend directory** as the build context:

```bash
# From project root
docker-compose build frontend

# Or manually
cd frontend
docker build -f docker/Dockerfile -t agro-frontend .
```

## Environment Variables

Required environment variables (set in root `.env` file):

- `BASIC_AUTH_USER`: Username for HTTP Basic Authentication
- `BASIC_AUTH_PASSWORD`: Password for HTTP Basic Authentication
- `VITE_API_BASE_URL`: Backend API endpoint (default: http://backend:7000)

## Ports

- **7073**: Frontend application port (HTTP)

## Health Check

The container exposes a health check endpoint at `/health` that bypasses authentication:

```bash
curl http://localhost:7073/health
# Response: OK
```

## Usage

From the project root:

```bash
# Build
docker-compose build frontend

# Start
docker-compose up -d frontend

# Logs
docker-compose logs -f frontend

# Shell access
docker-compose exec frontend sh
```

## Image Optimization

The multi-stage build reduces the final image size:
- Builder stage: ~1GB (Node.js + dependencies)
- Final image: ~50-100MB (nginx:alpine + static files)

## Notes

- All authentication is handled by nginx
- Static files are served from `/usr/share/nginx/html`
- The entrypoint script must run to generate authentication credentials
- nginx runs in foreground mode (daemon off) to keep container alive
