# Infrastructure Tasks & User Journeys

## Infrastructure Tasks

### IT-01: Project Scaffolding + Docker Compose
- **Purpose**: Base project structure with dev environment
- **Components**: FastAPI app (Poetry), Next.js app (pnpm), docker-compose with PostgreSQL 16 + pgvector, Dockerfiles
- **Acceptance Criteria**: `docker-compose up` starts all services, backend responds on /health, frontend renders
- **Security**: .env.example with placeholders only, .gitignore covers secrets

### IT-02: Database Schema + Alembic Migrations
- **Purpose**: All 12 tables created with proper types, indexes, constraints
- **Components**: Alembic config, initial migration (pgvector extension + all tables), IVFFlat index on content_vector
- **Acceptance Criteria**: `alembic upgrade head` succeeds, all tables exist with correct columns
- **Security**: No default passwords in migrations

### IT-03: SQLAlchemy Async Models
- **Purpose**: ORM layer for all entities
- **Components**: TimestampedBase (UUID + timestamps), all 12 model classes, relationships, metadata_ pattern
- **Acceptance Criteria**: Models import without errors, relationships resolve correctly
- **Security**: N/A

### IT-04: Authentication System
- **Purpose**: JWT auth with httpOnly cookies + API key auth for tools
- **Components**: Login, logout, refresh, me, setup wizard endpoints. Middleware dependencies. Rate limiting (5/min on auth).
- **Acceptance Criteria**: Login returns httpOnly cookie, protected routes reject without token, setup wizard creates first admin then disables
- **Security**: bcrypt cost 12, SameSite=Strict, Secure=True in prod, no token in response body

### IT-05: Frontend Base Layout + Auth Flow
- **Purpose**: Authenticated shell with navigation
- **Components**: (auth) and (dashboard) route groups, login page, sidebar (8 nav items), auth middleware, glassmorphism tokens, PostCSS config
- **Acceptance Criteria**: Unauthenticated → redirected to login. Authenticated → sidebar layout with all nav items. Theme renders correctly.
- **Security**: Middleware rejects expired/invalid tokens, no client-side token storage

### IT-06: Credential Encryption Service
- **Purpose**: Store Level 3 secrets (API keys) encrypted in DB
- **Components**: AES-256-GCM encrypt/decrypt service, encrypted_credentials CRUD, master key from env
- **Acceptance Criteria**: Store credential → retrieve decrypted → matches original. Cannot read without master key.
- **Security**: Never log decrypted values, never return encrypted raw bytes to frontend

### IT-07: Shared AI Clients
- **Purpose**: Reusable OpenAI (embeddings) and Anthropic (chat) client wrappers
- **Components**: Embedding client (batch support, retry), Claude chat client (streaming, retry), background task utility
- **Acceptance Criteria**: Embed text → returns 1536d vector. Chat with context → streams response.
- **Security**: API keys from Level 3 credential store, never in logs

### IT-08: Error Handling + Middleware
- **Purpose**: Consistent API responses, logging, CORS
- **Components**: Exception handlers, structured logging, request ID, CORS config (credentials: true), health endpoint
- **Acceptance Criteria**: Errors return consistent JSON format, request IDs traceable, CORS allows frontend origin
- **Security**: No stack traces in production responses, no sensitive data in logs

---

## User Journeys

### UJ-01: Gestionar Propiedades (Manage Properties)
- **Description**: User creates, lists (with filters), views detail, edits, and deactivates properties
- **Backend**: Properties CRUD (6 endpoints), filter by region/type/status, pagination
- **Frontend**: `/propiedades` list page (grid + filters), `/propiedades/[slug]` detail page (inline edit), create form
- **Acceptance Criteria**: Create property → appears in list → open detail → edit fields → save → changes persist
- **Security**: Auth required, all inputs validated (Pydantic), slug uniqueness enforced
- **Tests**: Property CRUD endpoints, slug generation, filter combinations

### UJ-02: Gestionar Sistemas (Manage Systems)
- **Description**: User creates, lists, views detail, edits systems. Pre-seeded with 12 known systems.
- **Backend**: Systems CRUD (6 endpoints), filter by category/status
- **Frontend**: `/sistemas` list page (grid + category badges), `/sistemas/[slug]` detail page, create form
- **Acceptance Criteria**: 12 systems pre-seeded → visible in list → create new → edit existing → category filter works
- **Security**: Auth required, input validation
- **Tests**: System CRUD, pre-seed script verification

### UJ-03: Vincular Propiedades ↔ Sistemas (Link Relations)
- **Description**: From property detail, user links/unlinks systems with config notes. Bidirectional navigation.
- **Backend**: Relations CRUD (4 endpoints), nested under properties and systems
- **Frontend**: "Sistemas vinculados" section on property detail, "Propiedades" section on system detail, link dialog
- **Acceptance Criteria**: Link system to property with notes → visible on both sides → edit config → unlink
- **Security**: Auth required, validate both IDs exist
- **Tests**: Relation CRUD, cascade behavior on entity deletion

### UJ-04: Gestionar Bloques de Conocimiento (Knowledge Blocks)
- **Description**: User creates/edits knowledge blocks attached to properties or systems. Inline editor with block type selector. Async embedding on save.
- **Backend**: Knowledge CRUD (6 endpoints), background embedding trigger, embed status field
- **Frontend**: Knowledge block list on property/system detail, inline editor (monospace), block type badge, save button, "indexando..." state
- **Acceptance Criteria**: Add block to property → content saved → embedding generated (async) → searchable → edit content → re-embedded
- **Security**: Auth required, content sanitized, embedding errors don't block user
- **Tests**: Block CRUD, embedding trigger, polymorphic query (blocks for property vs system)

### UJ-05: Configurar Integración Guesty
- **Description**: Admin enters Guesty API credentials, tests connection, configures sync preferences
- **Backend**: Credential store/retrieve (encrypted), Guesty API test endpoint, sync config
- **Frontend**: `/configuracion/integraciones` tab, credential form (masked), "Probar conexión" button
- **Acceptance Criteria**: Enter API key → test connection succeeds → credential encrypted in DB → can trigger sync
- **Security**: Admin only, credential encrypted AES-256-GCM, test call validates before storing

### UJ-06: Sincronizar Propiedades desde Guesty
- **Description**: User triggers manual sync OR system runs scheduled sync. Listings → properties + knowledge blocks.
- **Backend**: Sync orchestrator, Guesty provider (listings fetch, rate limiting), property mapping, conflict detection, sync_logs
- **Frontend**: `/sincronizacion` page, "Sincronizar ahora" button, progress indicator, results summary
- **Acceptance Criteria**: Trigger sync → listings fetched → new properties created → existing updated (no overwrite of manual edits) → sync log recorded
- **Security**: Admin only for manual trigger, Guesty credentials from encrypted store
- **Tests**: Sync with mock Guesty responses, conflict detection, rate limit handling

### UJ-07: Historial de Sincronización y Conflictos
- **Description**: User views sync history log and resolves conflicts (local vs remote edits)
- **Backend**: Sync logs paginated, conflict list, conflict resolution endpoints
- **Frontend**: Sync history table, conflict list with diff view, "Mantener local" / "Aceptar remoto" buttons
- **Acceptance Criteria**: View past syncs with stats → see conflicts → resolve each → conflict cleared
- **Security**: Auth required

### UJ-08: Gestionar Automatizaciones
- **Description**: Admin creates/edits scheduled sync tasks (cron/interval), pauses/resumes
- **Backend**: AutomationTask CRUD, APScheduler 4.x integration, job store in PostgreSQL
- **Frontend**: Automations section in configuración, task list, create/edit form (schedule selector)
- **Acceptance Criteria**: Create daily sync task → runs automatically → can pause → resume → edit schedule
- **Security**: Admin only

### UJ-09: Búsqueda Semántica (Semantic Search)
- **Description**: User searches knowledge by natural language. Query embedded → pgvector cosine search → top-K results with relevance scores.
- **Backend**: RAG search endpoint (embed query, pgvector query, score + source), scope filter
- **Frontend**: Search component (used in chat and standalone), results with relevance indicator, scope selector
- **Acceptance Criteria**: Search "instrucciones check-in Cala Bona" → returns relevant knowledge block with high score
- **Security**: Auth required, query length limited
- **Tests**: Search relevance with seeded data, scope filtering

### UJ-10: Chat RAG con Streaming (RAG Chat)
- **Description**: User opens chat, optionally scopes to property/system. Messages streamed via WebSocket. Claude answers with retrieved context. Sources cited.
- **Backend**: WebSocket endpoint, RAG pipeline (embed → search → context build → Claude stream), message persistence
- **Frontend**: `/chat` page, chat window, message bubbles, streaming text, source cards, scope selector
- **Acceptance Criteria**: Send question → see streaming response → sources shown below → conversation persisted
- **Security**: WS auth via cookie on handshake, content not logged in plain text
- **Tests**: WebSocket connection, RAG pipeline with mock data, source attribution accuracy

### UJ-11: Gestionar Sesiones de Chat
- **Description**: User views past sessions, resumes, renames, deletes. Auto-named from first message.
- **Backend**: Chat session CRUD, auto-title generation
- **Frontend**: Session sidebar on chat page, rename/delete actions
- **Acceptance Criteria**: Multiple sessions → switch between → rename → delete → new session
- **Security**: Users can only see own sessions

### UJ-12: Monitorización de Embeddings
- **Description**: Admin views embedding coverage (% vectorized), pending/failed counts. Triggers bulk re-indexing.
- **Backend**: Embedding stats endpoint, bulk re-embed endpoint (batched background)
- **Frontend**: AI config tab in configuración, coverage stats, "Re-indexar todo" button with progress
- **Acceptance Criteria**: See 95% coverage → trigger re-index → progress shown → completes
- **Security**: Admin only

### UJ-13: Gestionar API Keys para Agentes
- **Description**: Admin creates tool API keys (shown once), lists (masked), revokes. Keys for external AI agent access.
- **Backend**: Key generation, SHA-256 hash storage, validation middleware, revoke
- **Frontend**: API keys tab in configuración, create dialog (copy key warning), list with revoke button
- **Acceptance Criteria**: Create key → copy → use in API call → works → revoke → fails
- **Security**: Key shown only once, stored as hash, separate from user JWT auth
- **Tests**: Key creation, authentication, revocation

### UJ-14: Tool API para Agentes IA
- **Description**: 6 REST endpoints for AI agent consumption (search, property, system, relations, rag). API key auth. Logged.
- **Backend**: Tool router (6 endpoints), API key auth dependency, structured JSON responses, tool_api_logs
- **Frontend**: N/A (API only, documented via OpenAPI)
- **Acceptance Criteria**: Call each endpoint with valid API key → structured response → call logged
- **Security**: API key required, rate limited, no sensitive data in responses
- **Tests**: All 6 endpoints with valid/invalid keys

### UJ-15: Panel de Configuración Admin
- **Description**: Configuration page with tabs: integraciones, IA config (models, temperature, top-K), general
- **Backend**: Config CRUD endpoints, validation
- **Frontend**: `/configuracion` with tab navigation, forms per section
- **Acceptance Criteria**: Change RAG top-K → save → chat uses new value
- **Security**: Admin only

### UJ-16: Gestión de Usuarios
- **Description**: Admin invites users, assigns roles, deactivates accounts. Users edit own profile.
- **Backend**: User CRUD (admin), profile update (self), invite flow
- **Frontend**: Users tab in configuración, invite dialog, role selector, deactivate toggle
- **Acceptance Criteria**: Invite user → they can log in → change role → deactivate → can't log in
- **Security**: Admin only for management, users can only edit own profile

### UJ-17: Logs de Actividad
- **Description**: Admin views activity: sync events, tool API calls, token usage. Filterable.
- **Backend**: Aggregated logs endpoints (sync_logs + tool_api_logs + chat token usage)
- **Frontend**: Logs section in configuración, table with filters, usage summary cards
- **Acceptance Criteria**: See recent syncs, API calls, token consumption in one view
- **Security**: Admin only

### UJ-18: Dashboard
- **Description**: Landing page with stat cards, recent activity feed, quick actions
- **Backend**: Stats endpoint (counts, last sync, recent activity)
- **Frontend**: `/dashboard` with StatCards, ActivityFeed, QuickActions components
- **Acceptance Criteria**: Shows accurate counts, recent events, quick actions navigate correctly
- **Security**: Auth required

### UJ-19: Vista de Mapa (Map View)
- **Description**: Interactive map on dashboard with property pins (Leaflet + OpenStreetMap). Click → popup with details.
- **Backend**: Properties endpoint includes lat/lng coordinates
- **Frontend**: PropertyMap component (react-leaflet), clustering, color-coded by status, click → popup → link to detail
- **Acceptance Criteria**: All properties with coordinates appear on map → click pin → see info → navigate to detail
- **Security**: N/A (uses existing auth-protected data)

### UJ-20: Reservas (Reservations Read-Only)
- **Description**: Read-only list of Guesty reservations. Fetched on-demand (not stored), cached 5min.
- **Backend**: Guesty reservations proxy endpoint, short-term cache (in-memory or Redis)
- **Frontend**: `/reservas` page, reservation list with filters (property, date, status), detail expandable
- **Acceptance Criteria**: See current/upcoming reservations → filter by property → see guest name, dates, status
- **Security**: Auth required, no PII beyond what Guesty provides

### UJ-21: Pulido UI (UI Polish)
- **Description**: Empty states, loading skeletons, error boundaries, responsive checks, Spanish copy review
- **Backend**: N/A
- **Frontend**: All pages reviewed for edge cases
- **Acceptance Criteria**: Every page has: loading state, empty state with CTA, error boundary, responsive layout
- **Security**: Error boundaries don't expose internals

### UJ-22: Script de Datos Demo (Seed Script)
- **Description**: Seed script with 5 real-ish properties, 12 systems, 15+ knowledge blocks, relations, sample chat
- **Backend**: `scripts/seed.py` using async SQLAlchemy
- **Frontend**: N/A
- **Acceptance Criteria**: Run seed → all pages show realistic data → chat has context to answer questions
- **Security**: No real credentials in seed data
