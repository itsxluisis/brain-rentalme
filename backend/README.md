# Backend

Backend application — populated during project implementation.

## Expected Structure (defined during planning)
```
backend/
├── src/
│   ├── modules/        — feature modules (auth, admin, [domain modules])
│   ├── middleware/     — auth, validation, error handling
│   ├── db/             — database client, migrations, seed
│   └── main.[ext]      — application entry point
├── Dockerfile
├── package.json (or equivalent)
└── .env.example        — backend-specific env vars if needed
```

## Stack
Defined in `design/stack_selection.md` during planning.

## Running Locally
See `docker-compose.yml` in the root, or project-specific instructions added during setup.
