# Docker

Docker configuration files for local development and production builds.

## Expected Contents (populated during planning/implementation)
- `Dockerfile.backend` — backend production image
- `Dockerfile.frontend` — frontend production image (or static build)
- `.dockerignore` — files excluded from Docker build context

## Notes
- Development: use `docker-compose.yml` in the root (bind mounts, hot reload)
- Production: multi-stage builds to minimize image size
- No internal ports exposed except those required by EasyPanel reverse proxy
- `NODE_ENV=production` must be set in production images
