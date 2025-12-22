# GitLab CI/CD Deployment Checklist

Use this checklist to ensure successful deployment setup and execution.

## Pre-Deployment Setup

### ☐ 1. GitLab CI/CD Variables Configuration

Navigate to: **Your GitLab Project → Settings → CI/CD → Variables**

- [ ] Add `DEPLOY_HOST` variable
  - Value: Your server IP or domain (e.g., `192.168.1.100`)
  - Protected: ✅ Yes
  - Masked: ❌ No

- [ ] Add `DEPLOY_USER` variable
  - Value: SSH username (e.g., `ubuntu`, `deploy`)
  - Protected: ✅ Yes
  - Masked: ❌ No

- [ ] Add `DEPLOY_SSH_KEY` variable
  - Type: File
  - Value: Paste your SSH private key (entire content including BEGIN/END lines)
  - Protected: ✅ Yes
  - Masked: ✅ Yes

- [ ] Confirm runtime variables in root `.env` (see `docs/ENV.md`)
- [ ] Set/override `DEPLOY_TAG` if needed (default: `latest`)

### ☐ 2. Remote Host Preparation

SSH into your remote server and execute:

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Install Docker Compose V2
sudo apt-get install -y docker-compose-plugin

# Verify installations
docker --version
docker compose version

# Add your user to docker group
sudo usermod -aG docker $USER

# ⚠️ IMPORTANT: Logout and login again for group changes to take effect
exit
```

After logging back in:

```bash
# Verify docker works without sudo
docker ps

# Create deployment directory
mkdir -p ~/agro-deployment
```

### ☐ 3. SSH Key Setup

On your local machine:

```bash
# Generate SSH key pair (if you don't have one)
ssh-keygen -t ed25519 -C "gitlab-ci-agro" -f ~/.ssh/agro_deploy

# Copy public key to remote server
ssh-copy-id -i ~/.ssh/agro_deploy.pub your-user@your-server

# Test SSH connection
ssh -i ~/.ssh/agro_deploy your-user@your-server
# If successful, exit the SSH session
exit

# Display private key for GitLab variable (copy ALL output)
cat ~/.ssh/agro_deploy
```

Copy the entire output (including the BEGIN and END lines) and paste it into the `DEPLOY_SSH_KEY` variable in GitLab.

### ☐ 4. Environment File (choose one approach)

- Recommended for this pipeline (compose over SSH): keep `.env` in the repo (non-sensitive) or generate it during the deploy job from GitLab masked variables. Compose reads `.env` on the CI runner, not on the host.
- Optional host-managed secrets: if you prefer the host to own secrets, place `.env` on the server (e.g., `~/agro-deployment/.env`) and adjust the deploy job to scp it or run compose directly on the host. The current flow does **not** read host `.env` by default.

### ☐ 5. Firewall Configuration

On remote server:

```bash
# Install UFW if not installed
sudo apt-get install -y ufw

# Allow SSH (important - don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow application ports
sudo ufw allow 7000/tcp  # Backend
sudo ufw allow 7073/tcp  # Frontend

# Check rules before enabling
sudo ufw status

# Enable firewall
sudo ufw enable

# Verify
sudo ufw status numbered
```

### ☐ 6. Verify GitLab Runner

In GitLab:

- [ ] Navigate to: **Settings → CI/CD → Runners**
- [ ] Verify at least one shared or project runner is available and active
- [ ] Runner should have Docker executor

## Pre-Deployment Verification

### ☐ 7. Local Testing

```bash
# Navigate to project root
cd d:\projects\agro_frontend

# Verify all required files exist
ls .gitlab-ci.yml
ls docker-compose.prod.yml
ls .env.example

# Optional: Test docker-compose syntax locally
docker compose -f docker-compose.yml config
docker compose -f docker-compose.prod.yml config
```

### ☐ 8. Git Repository Check

```bash
# Check current branch
git branch

# Ensure you're on master branch
git checkout master

# Verify remote is set
git remote -v

# Ensure working directory is clean
git status
```

## Deployment Execution

### ☐ 9. First Deployment

```bash
# Stage all changes
git add .

# Commit
git commit -m "Add GitLab CI/CD pipeline for Docker deployment"

# Push to master branch (triggers pipeline)
git push origin master
```

### ☐ 10. Monitor Pipeline

In GitLab:

- [ ] Navigate to: **CI/CD → Pipelines**
- [ ] Click on the running pipeline
- [ ] Monitor stages: Build → Deploy
- [ ] Check logs for each job
- [ ] Verify all stages complete successfully (green checkmarks)

## Post-Deployment Verification

### ☐ 11. Service Health Checks

From your local machine or any computer:

```bash
# Replace YOUR_SERVER with your actual server IP/domain

# Test backend
curl http://YOUR_SERVER:7000/healthcheck
# Expected: HTTP 200 response

# Test frontend
curl http://YOUR_SERVER:7073/health
# Expected: HTTP 200 response

# Or open in browser:
# Backend: http://YOUR_SERVER:7000
# Frontend: http://YOUR_SERVER:7073
```

### ☐ 12. Remote Host Verification

SSH to remote server:

```bash
ssh your-user@your-server
cd ~/agro-deployment

# Check running containers
docker compose ps
# Both containers should show "Up" status

# Check logs
docker compose logs --tail=50

# Check specific service logs
docker compose logs backend --tail=20
docker compose logs frontend --tail=20

# Check resource usage
docker stats --no-stream
```

### ☐ 13. Database Verification

On remote server:

```bash
# Check if database volume exists
docker volume ls | grep agro-db-data

# Inspect volume
docker volume inspect agro-db-data

# Optional: Check database file (if accessible)
docker exec agro-backend ls -lh /app/data/
```

## Ongoing Operations

### ☐ 14. Subsequent Deployments

For future deployments:

```bash
# Make your code changes
# ...

# Commit changes
git add .
git commit -m "Your changes description"

# Push to master (auto-deploys)
git push origin master

# Monitor in GitLab CI/CD → Pipelines
```

### ☐ 15. Monitoring

Set up regular monitoring:

- [ ] Check container status daily: `docker compose ps`
- [ ] Monitor logs: `docker compose logs -f`
- [ ] Check disk space: `df -h`
- [ ] Monitor Docker volumes: `docker volume ls`
- [ ] Review GitLab pipeline history weekly

### ☐ 16. Backup Schedule

Set up regular backups:

```bash
# Create backup script on remote host
cat > ~/backup-agro-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker run --rm -v agro-db-data:/data -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/agro-db-$TIMESTAMP.tar.gz /data
echo "Backup created: agro-db-$TIMESTAMP.tar.gz"
# Keep only last 7 days of backups
find $BACKUP_DIR -name "agro-db-*.tar.gz" -mtime +7 -delete
EOF

chmod +x ~/backup-agro-db.sh

# Test backup
~/backup-agro-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-agro-db.sh") | crontab -
```

## Troubleshooting

### ☐ If Pipeline Fails

1. **Build Stage Failure**
   - [ ] Check Dockerfile syntax
   - [ ] Verify Docker daemon is running on GitLab Runner (dind)
   - [ ] Review build logs in GitLab

2. **Deploy Stage Failure**
   - [ ] Verify SSH connection manually: `ssh -i ~/.ssh/agro_deploy user@host`
   - [ ] Check DEPLOY_SSH_KEY / DEPLOY_HOST / DEPLOY_USER variables
   - [ ] Verify remote host has Docker running
   - [ ] Check firewall rules on remote host

### ☐ If Services Don't Start

On remote server:

```bash
cd ~/agro-deployment

# Check container status
docker compose ps

# View logs
docker compose logs

# Check if ports are in use
sudo netstat -tulpn | grep 7000
sudo netstat -tulpn | grep 7073

# Restart services
docker compose down
docker compose up -d

# Force recreate
docker compose up -d --force-recreate
```

### ☐ Rollback Procedure

If deployment causes issues:

```bash
# On remote host
cd ~/agro-deployment

# Stop services
docker compose down

# Note: Replace COMMIT_SHA with the actual commit hash
export CI_REGISTRY_IMAGE=registry.gitlab.com/your-group/your-project
export COMMIT_SHA=abc1234

# Pull specific version
docker pull $CI_REGISTRY_IMAGE/backend:$COMMIT_SHA
docker pull $CI_REGISTRY_IMAGE/frontend:$COMMIT_SHA

# Tag as latest
docker tag $CI_REGISTRY_IMAGE/backend:$COMMIT_SHA $CI_REGISTRY_IMAGE/backend:latest
docker tag $CI_REGISTRY_IMAGE/frontend:$COMMIT_SHA $CI_REGISTRY_IMAGE/frontend:latest

# Restart with previous version
docker compose up -d
```

## Security Checklist

- [ ] SSH keys are properly secured (not shared)
- [ ] GitLab variables are marked as protected and masked
- [ ] Firewall is enabled and configured
- [ ] Only master branch can deploy
- [ ] .env file contains no sensitive data in repository
- [ ] Remote host has latest security updates
- [ ] Docker daemon is regularly updated

## Documentation References

- **Quick Start Guide**: `QUICK_START.md`
- **Full Setup Documentation**: `CI_CD_SETUP.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **This Checklist**: `DEPLOYMENT_CHECKLIST.md`

## Support

If you encounter issues:

1. Check pipeline logs in GitLab
2. Review documentation files
3. Verify all checklist items are completed
4. Check remote host logs: `docker compose logs`
5. Verify network connectivity: `ping your-server`

---

**Status**: Complete this checklist before and after each deployment  
**Last Updated**: December 9, 2025
