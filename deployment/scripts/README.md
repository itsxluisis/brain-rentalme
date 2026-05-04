# Scripts

Deployment and maintenance scripts.

## Expected Contents (populated during implementation)
- `seed.sh` or `seed.[ext]` — populates database with demo data
- `migrate.sh` — runs database migrations
- `health-check.sh` — verifies all services are running correctly

## Notes
- Scripts must be idempotent where possible
- No hardcoded secrets — read from environment variables
- Log meaningful output for debugging
