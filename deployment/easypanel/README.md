# EasyPanel

EasyPanel-specific configuration and deployment files.

## Expected Contents (populated during deployment preparation)
- `easypanel.yml` — service definitions if using EasyPanel schema format
- `compose.prod.yml` — production-oriented Docker Compose override (if needed)

## Deployment Model
- Source: GitHub repository (private)
- Build trigger: push to main branch (or manual deploy)
- Environment variables: set in EasyPanel dashboard (Level 2 secrets)
- SSL: handled automatically by EasyPanel

## EasyPanel Service Requirements
- Each container service (backend, frontend, db) defined as a separate service
- Persistent volumes for database data
- Internal network between services — database port not exposed publicly
- Health check endpoint: `GET /health` on backend
