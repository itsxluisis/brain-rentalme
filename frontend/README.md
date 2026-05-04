# Frontend

Frontend application — populated during project implementation.

## Expected Structure (defined during planning)
```
frontend/
├── src/
│   ├── pages/          — route-level components
│   ├── components/     — shared UI components
│   ├── lib/            — API client, utilities
│   └── main.[ext]      — application entry point
├── public/
├── Dockerfile
└── package.json (or equivalent)
```

## Stack
Defined in `design/stack_selection.md` during planning.

## Design System
Glassmorphism base with light/dark mode. Full spec in `design/style_guide.md`.

## Running Locally
See `docker-compose.yml` in the root, or project-specific instructions added during setup.
