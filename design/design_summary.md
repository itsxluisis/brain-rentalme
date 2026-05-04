# Design Summary

## Stack
- Backend: Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + Alembic
- Frontend: Next.js 14 (App Router) + TypeScript 5 + Tailwind 3 + Zustand + TanStack Query 5
- DB: PostgreSQL 16 + pgvector, 12 tables, UUID PKs, JSONB metadata, VARCHAR+CHECK enums
- Auth: JWT (httpOnly cookie, 24h), bcrypt, roles: admin|user. Tool API: SHA-256 hashed API keys
- AI: OpenAI (embeddings text-embedding-3-small 1536d) + Anthropic Claude (RAG chat)

## Module Map
- Backend: 12 modules in `backend/app/` — pattern: router.py → service.py → models.py + schemas.py
- Frontend: 8 pages in `frontend/src/app/(dashboard)/`, components in ui/layout/data-display/domain

## Entity Overview
- **User** — email, role (admin|user), password_hash
- **Property** — name, slug, type, region, capacity, guesty_listing_id, status, tags, metadata_
- **System** — name, slug, category, has_api, status, tags, metadata_
- **KnowledgeBlock** — entity_type+entity_id (polymorphic), block_type, title, content, content_vector(1536), source, language
- **PropertySystemRelation** — property_id, system_id, notes, config (JSONB)
- **SyncLog** — provider, status, listings_processed, blocks_created/updated, errors
- **ChatSession** — user_id, title, scope, scope_entity_id
- **ChatMessage** — session_id, role, content, sources (JSONB), token_count
- **ToolApiKey** — name, key_hash, is_active, created_by
- **EncryptedCredential** — service_name, encrypted_value, iv, tag
- **AutomationTask** — name, action_type, schedule_type, schedule_config, is_active

## Key Patterns
- `metadata_` naming (SQLAlchemy collision avoidance) + Pydantic `Field(alias="metadata_")`
- Async embedding via BackgroundTasks (never in request cycle)
- pgvector: IVFFlat cosine index, CREATE EXTENSION in first migration
- Guesty sync: provider abstraction, exponential backoff, conflict detection (source field)
- WebSocket chat: JWT validated on handshake, chunked streaming from Claude
- Glassmorphism UI: dark theme default, blur(16px) cards, electric blue accent #3B82F6

## Credential Map
- Level 1 (.env): DATABASE_URL, JWT_SECRET, ENCRYPTION_MASTER_KEY
- Level 2 (deployment): APP_ENV, PORT, CORS_ORIGIN, BACKEND_URL
- Level 3 (admin panel): GUESTY_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, CLOUDBEDS_KEY (future)

## Installed Skills & MCPs
(To be populated during skill/MCP discovery step)
