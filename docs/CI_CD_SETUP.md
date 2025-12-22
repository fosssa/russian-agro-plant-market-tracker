# GitLab CI/CD Deployment Setup

This document describes the GitLab CI/CD pipeline configuration for deploying the Agro frontend and backend services via Docker Compose to a remote host.

## Overview

The pipeline automatically:
- Builds Docker images for both frontend and backend services
- Pushes images to GitLab Container Registry (master branch only)
- Deploys both services to a remote host via SSH (master branch only)

## Required GitLab CI/CD Variables

Configure the following variables in your GitLab project settings (Settings > CI/CD > Variables):

### Required Variables

- `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` (set in GitLab CI/CD → Variables; SSH key as a File variable)
- `CI_REGISTRY_IMAGE` (provided by GitLab)

### Runtime / Optional Variables

- Defined in the root `.env`; see `docs/ENV.md` for the authoritative list, defaults, and usage (includes `DEPLOY_TAG`, backend runtime, and frontend runtime variables).

## Remote Host Prerequisites

The deployment host must have the following configured:

### 1. Software Requirements

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installations
docker --version
docker compose version
```

### 2. User Configuration

```bash
# Add deployment user to docker group
sudo usermod -aG docker $DEPLOY_USER

# Verify docker access (logout and login required)
docker ps
```

### 3. SSH Key Setup

```bash
# On your local machine, generate SSH key pair if not exists
ssh-keygen -t ed25519 -C "gitlab-ci-deployment" -f ~/.ssh/agro_deploy_key

# Copy public key to remote host
ssh-copy-id -i ~/.ssh/agro_deploy_key.pub $DEPLOY_USER@$DEPLOY_HOST

# Test SSH connection
ssh -i ~/.ssh/agro_deploy_key $DEPLOY_USER@$DEPLOY_HOST

# Copy private key content for GitLab CI/CD variable
cat ~/.ssh/agro_deploy_key
```

### 4. Environment Configuration

By default, `docker compose` is executed from the CI runner with `DOCKER_HOST=ssh://...`, so it reads `.env` from the runner’s workspace (the repository). Keep non-secret defaults in a tracked `.env.example`, and supply real values either:
- by committing a non-sensitive `.env` (not recommended for secrets), or
- by generating `.env` during the deploy job from GitLab masked variables.

If you prefer host-managed secrets, you can place `.env` on the server and switch the deploy job back to copying it or running compose directly on the host, but the current flow does not read host `.env`.

### 5. Firewall Configuration

```bash
# Allow SSH access
sudo ufw allow 22/tcp

# Allow application ports
sudo ufw allow 7000/tcp  # Backend
sudo ufw allow 7073/tcp  # Frontend

# Enable firewall
sudo ufw enable
```

## Pipeline Workflow

### Stages

1. **Build Stage** (All branches and MRs)
   - `build-push-backend`: Builds and pushes backend image (tags: commit SHA + latest)
   - `build-push-frontend`: Builds and pushes frontend image (tags: commit SHA + latest)

2. **Deploy Stage** (Master branch only)
   - `deploy`: Runs `docker compose` over SSH against the remote Docker daemon

### Branch Policy

- **All branches / merge requests**: Build and push images for testing
- **Master branch only**: Deploy to production

This ensures only validated code from the master branch is deployed.

## Files Overview

### `.gitlab-ci.yml`

Main GitLab CI/CD pipeline configuration located in the project root. It builds and pushes images (combined) and deploys via `DOCKER_HOST=ssh://...`.

### `docker-compose.prod.yml`

Production Docker Compose configuration that:
- References pre-built images from GitLab Container Registry
- Uses `${CI_REGISTRY_IMAGE}` and `${DEPLOY_TAG:-latest}` to select versions
- Maintains volumes, networks, and health checks

### `docker-compose.yml`

Development Docker Compose configuration that builds images locally from Dockerfiles for local development.

## Deployment Process

When you push to the master branch:

1. **Build+Push Phase**
   - Both images are built in parallel
   - Tagged with commit SHA and `latest`
   - Pushed to GitLab Container Registry

2. **Deploy Phase**
   - SSH connection established to remote host using `DOCKER_HOST=ssh://...`
   - Docker login performed against registry (from CI)
   - `docker compose -f docker-compose.prod.yml pull` executed from CI (remote daemon)
   - Services started with `docker compose up -d --remove-orphans`
   - Health checks performed
   - Old images cleaned up

## Verification

After deployment, the pipeline automatically verifies:

```bash
# Backend health check
curl http://$DEPLOY_HOST:7000/healthcheck

# Frontend health check
curl http://$DEPLOY_HOST:7073/health
```

You can also manually verify on the remote host:

```bash
ssh $DEPLOY_USER@$DEPLOY_HOST
cd ~/agro-deployment
docker compose ps
docker compose logs -f
```

## Rollback Procedure

If deployment fails or issues are detected:

### Automatic Rollback

Health check failures are reported but don't automatically rollback. Manual intervention required.

### Manual Rollback

1. Identify the last known good commit SHA:
   ```bash
   # From GitLab pipeline history or git log
   git log --oneline
   ```

2. SSH to the remote host:
   ```bash
   ssh $DEPLOY_USER@$DEPLOY_HOST
   cd ~/agro-deployment
   ```

3. Update image tags in environment:
   ```bash
   export CI_REGISTRY_IMAGE=registry.gitlab.com/your-group/your-project
   export TARGET_SHA=abc1234  # Replace with target commit SHA
   
   # Pull specific version
   docker compose pull
   
   # Or manually specify images
   docker pull $CI_REGISTRY_IMAGE/backend:$TARGET_SHA
   docker pull $CI_REGISTRY_IMAGE/frontend:$TARGET_SHA
   
   # Update and restart
   docker compose up -d
   ```

## Monitoring

### View Logs

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# View last 100 lines
docker compose logs --tail=100
```

### Check Service Status

```bash
# List running containers
docker compose ps

# Check resource usage
docker stats

# Inspect specific container
docker inspect agro-backend
docker inspect agro-frontend
```

## Troubleshooting

### Pipeline Fails at Build Stage

- Check Dockerfile syntax
- Verify build context paths
- Review build logs in GitLab CI/CD

### Pipeline Fails at Push Stage

- Ensure you're on master branch
- Verify GitLab Container Registry is enabled
- Check registry permissions

### Pipeline Fails at Deploy Stage

**SSH Connection Issues:**
```bash
# Test SSH connection manually
ssh -i /path/to/key $DEPLOY_USER@$DEPLOY_HOST

# Check SSH key format (should be PEM format)
ssh-keygen -p -f /path/to/key -m PEM
```

**Docker Permission Issues:**
```bash
# Verify user is in docker group
groups $DEPLOY_USER

# Add user to docker group if missing
sudo usermod -aG docker $DEPLOY_USER
```

**Image Pull Issues:**
```bash
# Verify registry login on remote host
docker login registry.gitlab.com

# Check network connectivity
ping registry.gitlab.com
```

### Services Not Starting

```bash
# Check container logs
docker compose logs backend
docker compose logs frontend

# Check if ports are already in use
sudo netstat -tulpn | grep 7000
sudo netstat -tulpn | grep 7073

# Verify .env file exists and is readable
cat ~/agro-deployment/.env
```

## Security Best Practices

1. **SSH Keys**: Use dedicated deployment keys, not personal SSH keys
2. **Firewall**: Restrict SSH access to GitLab Runner IP addresses
3. **Secrets**: Store sensitive data in GitLab CI/CD variables with masked flag
4. **Registry**: Use GitLab's built-in Container Registry with access tokens
5. **Updates**: Regularly update base images and dependencies

## Maintenance

### Update Dependencies

```bash
# On remote host
cd ~/agro-deployment
docker compose pull
docker compose up -d
```

### Clean Up Old Images

```bash
# Remove dangling images
docker image prune -f

# Remove all unused images
docker image prune -a -f

# Clean up everything (use with caution)
docker system prune -a --volumes -f
```

### Database Backup

The SQLite database is persisted in the `agro-db-data` volume. To back it up:

```bash
# Create backup directory
mkdir -p ~/backups

# Backup database
docker run --rm -v agro-db-data:/data -v ~/backups:/backup \
  alpine tar czf /backup/db-backup-$(date +%Y%m%d-%H%M%S).tar.gz /data

# List backups
ls -lh ~/backups
```

## Support

For issues or questions:
1. Check GitLab CI/CD pipeline logs
2. Review remote host logs: `docker compose logs`
3. Verify all prerequisites are met
4. Check firewall and network connectivity

## Additional Resources

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitLab Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/)
