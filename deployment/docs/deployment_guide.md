# Deployment Guide

## Overview
(Summary of deployment topology and services — populated during deployment preparation)

## Prerequisites
- Docker and Docker Compose installed (local)
- EasyPanel instance with GitHub access (production)
- `.env` populated from `.env.example`

## Local Deployment

```bash
# Copy environment template
cp .env.example .env
# Edit .env with real values

# Start all services
docker compose up -d

# Run database migrations
docker compose exec backend [migration command]

# Seed demo data (optional)
docker compose exec backend [seed command]
```

## EasyPanel Deployment

1. Push repository to GitHub (private)
2. In EasyPanel: New App → GitHub → select repository
3. Set environment variables (Level 2 secrets) in EasyPanel dashboard
4. Deploy — EasyPanel pulls from GitHub and builds Docker image
5. Run migrations via EasyPanel terminal or deploy hook

## Environment Variables

| Variable | Level | Required | Notes |
|----------|-------|----------|-------|
| DATABASE_URL | 1 | Yes | Set in .env (local) or EasyPanel (prod) |
| JWT_SECRET | 1 | Yes | |
| ENCRYPTION_MASTER_KEY | 1 | Yes | For Level 3 credential encryption |

(Add project-specific variables during deployment preparation)

## Rollback

1. In EasyPanel: select previous deployment → redeploy
2. For database rollback: run `[rollback command]`

## Health Checks
- Backend: `GET /health`
- Database: connection pool status via Admin panel

## Post-Deployment Checklist
- [ ] All services healthy
- [ ] Database migrations applied
- [ ] Admin panel accessible
- [ ] No secrets in logs
- [ ] HTTPS enabled (EasyPanel handles SSL)
