# Project Memory

## Current State
- **Project**: BrAIn — Business Knowledge Operating System for RentalMe.es
- **Phase**: Ready for EasyPanel deployment — all 30 tasks complete + 6 security fixes applied
- **Last Completed**: Security fixes (2026-05-04) — all critical /review blockers resolved, TypeScript 0 errors
- **Next Step**: Deploy to EasyPanel following `docs/deployment_guide.md`. Set POSTGRES_PASSWORD, JWT_SECRET, ENCRYPTION_MASTER_KEY, CORS_ORIGIN, NEXT_PUBLIC_API_URL.

## Key Decisions
- Chat LLM: Anthropic Claude (OpenAI for embeddings only)
- V1 includes map view + reservations read-only view
- Spanish UI, English code/API
- 30-100 properties scale, IVFFlat pgvector index
- react-leaflet + OpenStreetMap for map
- Grouped non-domain models in shared/models.py (relations, chat, tools, credentials, automations)
- API keys loaded from encrypted credential store (not env)

## Blockers
- Docker not installed on local machine (doesn't block EasyPanel deployment — EasyPanel builds in the cloud)
- POSTGRES_PASSWORD is now mandatory in `.env` / EasyPanel config (no default) — must be set before first run

## Key Context for Next Session
- TypeScript build verified clean (0 errors) — all 30 tasks complete
- Backend not yet runnable locally (needs PostgreSQL + Python 3.12 + env vars)
- Demo data: run `python -m scripts.seed_demo` from backend/ (creates admin@rentalme.es/admin1234)
- All major features implemented: properties, systems, relations, knowledge blocks, Guesty sync, RAG chat, Tool API, user management, map, reservations
- APScheduler uses SQLAlchemy data store — requires DB migration for apscheduler tables (handled at startup)
- react-leaflet installed, requires `ssr: false` dynamic import (already done in mapa/page.tsx)
- Credential key names: GUESTY_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY (uppercase, stored in encrypted_credentials table)

## Recent Changes (2026-05-02 — Full Build)
- M2: Guesty integration, sync, conflicts, automations (APScheduler 4.x)
- M3: RAG service (pgvector), WebSocket chat + Claude streaming, embedding monitoring
- M4: Tool API (6 endpoints), API key management, user management, activity logs
- M5: Dashboard, react-leaflet map, live reservations, demo seed script
