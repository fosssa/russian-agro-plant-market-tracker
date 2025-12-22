# Environment Variables

Single `.env` at the repository root is used by both backend and frontend.  
`docker compose` (including CI with `DOCKER_HOST=ssh://...`) reads this root `.env`. Do not commit secrets; keep defaults/non-secret values only.

## Deployment / CI

| Variable | Default | Purpose |
|----------|---------|---------|
| DEPLOY_HOST | _(required)_ | Target host/IP for deployments (used by CI) |
| DEPLOY_USER | _(required)_ | SSH username for `DEPLOY_HOST` |
| DEPLOY_SSH_KEY | _(required)_ | Private SSH key contents for CI deploys (file variable) |
| CI_REGISTRY_IMAGE | _(CI provided)_ | Registry path for built images |
| DEPLOY_TAG | latest | Image tag to deploy (override to pin a tag) |

## Backend Runtime

| Variable | Default | Purpose |
|----------|---------|---------|
| DATABASE_URL | sqlite:////app/data/app.db | SQLAlchemy DB URL (SQLite default) |
| UVICORN_ROOT_PATH | _(empty)_ | Path prefix when served behind a reverse proxy (if back proxied to `<URL>/api`, set this to `/api`) |
| WORKERS | 1 | Uvicorn worker count |
| LOG_LEVEL | info | Uvicorn log level (debug/info/warning/error/critical) |

## Frontend Runtime

| Variable | Default | Purpose |
|----------|---------|---------|
| VITE_API_BASE_URL | http://backend:7000 | Frontend → backend API base URL |
| VITE_API_TIMEOUT | 10000 | Axios timeout in ms |
| BASIC_AUTH_USER | admin | HTTP Basic Auth username |
| BASIC_AUTH_PASSWORD | changeme | HTTP Basic Auth password |

