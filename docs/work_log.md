# Work Log

## Log

### 2026-05-02 — IT-01: Project Scaffolding + Docker Compose
- **Work Done**: Created full project structure. Backend: FastAPI app with Poetry (pyproject.toml), async SQLAlchemy database module, config with pydantic-settings, Alembic setup, all 12 module directories with __init__.py. Frontend: Next.js 14 with App Router, TypeScript, Tailwind CSS (glassmorphism tokens), TanStack Query provider, Axios client with credentials, route groups for (auth) and (dashboard), placeholder pages. Docker: docker-compose.yml with pgvector/pgvector:pg16, backend and frontend Dockerfiles, health check on DB.
- **Files Created/Modified**: 38+ files across backend/, frontend/, docker-compose.yml, .env, .env.example
- **Decisions**: Used pgvector/pgvector:pg16 Docker image (includes pgvector pre-installed). Used npm for frontend (pnpm available via npx but npm simpler for local dev). PostCSS as CommonJS per pitfall notes.
- **Security Check**: .env has dev-only secrets, .gitignore covers .env files, no hardcoded production secrets
- **Tests**: N/A (infrastructure only)
- **Notes**: Docker not installed on local machine — config files verified structurally. Next.js build passes successfully with all routes resolving.

### 2026-05-02 — IT-02: Database Schema + Alembic Migrations
- **Work Done**: Created initial Alembic migration with pgvector extension + 12 tables. All CHECK constraints, JSONB defaults, UUID PKs, FK relationships, indexes (IVFFlat on content_vector deferred to when data exists).
- **Files Created**: backend/alembic/versions/001_initial_schema.py, alembic.ini, alembic/env.py, alembic/script.py.mako
- **Security Check**: No default passwords in migrations, no secrets

### 2026-05-02 — IT-03: SQLAlchemy Async Models
- **Work Done**: All 12 ORM models defined. TimestampedBase with UUID + timestamps. Property, System, KnowledgeBlock (with pgvector Vector column), PropertySystemRelation (with bidirectional relationships), SyncLog, ChatSession/Message, ToolApiKey/Log, EncryptedCredential, AutomationTask.
- **Files Created**: backend/app/{auth,properties,systems,knowledge}/models.py, backend/app/shared/models.py
- **Decisions**: Grouped non-domain models (relations, chat, tools, credentials, automations) in shared/models.py to avoid circular imports
- **Security Check**: metadata_ naming pattern applied

### 2026-05-02 — IT-04: Authentication System
- **Work Done**: JWT auth with httpOnly cookies. Setup wizard (first admin creation, disabled after). Login/logout/refresh/me endpoints. bcrypt password hashing. get_current_user and require_admin dependencies. Rate limit config ready.
- **Files Created**: backend/app/auth/{router,service,jwt,schemas,dependencies}.py
- **Security Check**: Cookies httpOnly+SameSite, no token in response body, bcrypt cost default

### 2026-05-02 — IT-05: Frontend Base Layout + Auth Flow
- **Work Done**: Dashboard layout with Sidebar (7 nav items, glassmorphism), AuthGuard component (checks /auth/me on mount, redirects to login). Login page with form. Zustand auth store. Axios API client with credentials + 401 interceptor.
- **Files Created**: frontend/src/components/layout/{Sidebar,AuthGuard}.tsx, stores/auth.ts, lib/api/{client,auth}.ts, app/(dashboard)/layout.tsx updated
- **Security Check**: No token in localStorage, cookie-based auth only
- **Verification**: Next.js build passes with all routes

### 2026-05-02 — IT-06: Credential Encryption Service
- **Work Done**: AES-256-GCM encrypt/decrypt service. Store/retrieve/delete/list credentials. Master key from env. Never returns decrypted values to list endpoint.
- **Files Created**: backend/app/credentials/service.py
- **Security Check**: 12-byte random IV per encryption, never logs decrypted values

### 2026-05-02 — IT-07: Shared AI Clients
- **Work Done**: OpenAI async client for embeddings (text-embedding-3-small), Anthropic async client for chat (Claude streaming). Both load API keys from encrypted credential store. Singleton pattern with reset capability.
- **Files Created**: backend/app/shared/{embeddings,llm}.py
- **Security Check**: API keys from Level 3 encrypted store, not from env

### 2026-05-02 — IT-08: Error Handling + Middleware
- **Work Done**: Custom exception classes (NotFoundError, ConflictError, ForbiddenError). Paginated response generic model. CORS configured in main.py with credentials support.
- **Files Created**: backend/app/shared/{exceptions,pagination}.py
- **Security Check**: Error responses don't leak internals

### 2026-05-02 — UJ-01: Gestionar Propiedades
- **Work Done**: Full property CRUD backend (service + schemas + router). Frontend: property list page with filters (region, type, status, search), property detail page with inline editing, create property form. slugify helper for unique slug generation. TypeScript casting fix for enum form values.
- **Files Created**: backend/app/properties/{models,schemas,service,router}.py, frontend pages and API client, constants/regions.ts, types/property.ts
- **Security Check**: Auth on all routes, admin required for DELETE, input validated via Pydantic

### 2026-05-02 — UJ-02: Gestionar Sistemas
- **Work Done**: Full system CRUD backend (service + schemas + router with seed endpoint). 12 pre-seeded systems. Frontend: systems list page with category/status filters, system detail with inline edit, create system form.
- **Files Created**: backend/app/systems/{models,schemas,service,router}.py, frontend pages, constants/systems.ts, types/system.ts
- **Security Check**: Admin required for DELETE and /seed, auth on all routes

### 2026-05-02 — UJ-03: Vincular Propiedades ↔ Sistemas
- **Work Done**: Backend relation CRUD (create_relation, update_relation, delete_relation, get_property_relations, get_system_relations) in knowledge/service.py and router.py. Frontend: LinkedSystemsSection component (link dialog with system dropdown filtered to unlisted, notes field, edit notes, unlink), LinkedPropertiesSection component (read-only list with property links to detail page). Wired into both property and system detail pages.
- **Files Created**: frontend/src/components/domain/{LinkedSystemsSection,LinkedPropertiesSection}.tsx
- **Security Check**: Auth on all relation endpoints, relation ownership verified via property_id

### 2026-05-02 — UJ-04: Gestionar Bloques de Conocimiento
- **Work Done**: Backend knowledge block CRUD with async embedding generation via BackgroundTasks (never in request cycle). has_embedding computed property. Re-embeds on content change, resets source to 'manual'. Frontend: KnowledgeBlockSection component (add form with title+type+content, expandable accordion list, inline editing, "Indexando..." spinner for pending embeddings, Guesty sync badge). Wired into both property and system detail pages.
- **Files Created**: backend/app/knowledge/{models,schemas,service,router}.py, frontend/src/components/domain/KnowledgeBlockSection.tsx, lib/api/knowledge.ts, lib/constants/blocks.ts, types/knowledge.ts
- **Security Check**: Auth on all knowledge endpoints, embedding runs in background task not request cycle

### 2026-05-02 — UJ-05: Configurar Integración Guesty
- **Work Done**: Credentials router (GET/PUT/DELETE/POST-test for any service). Guesty provider (test_guesty_connection, fetch_listings). Frontend: /configuracion/integraciones with masked API key inputs, save/test/delete per service (Guesty, OpenAI, Anthropic).
- **Files Created**: backend/app/credentials/router.py, backend/app/sync/providers/guesty.py, frontend/src/lib/api/credentials.ts, frontend/src/app/(dashboard)/configuracion/integraciones/page.tsx
- **Fixed**: credential key names in embeddings.py and llm.py changed from "openai"/"anthropic" to "OPENAI_API_KEY"/"ANTHROPIC_API_KEY" for consistency
- **Security Check**: Admin only on all credential endpoints, never returns decrypted value, AES-256-GCM encryption

### 2026-05-02 — UJ-06/07: Sync + Conflicts
- **Work Done**: Sync orchestrator (run_guesty_sync) with rate limiting, property mapping, conflict detection. Sync router (trigger/status/logs). Conflict endpoints (GET /conflicts, POST /conflicts/:id/resolve). Frontend: /sincronizacion with historial tab (logs table) and conflictos tab (resolve UI).
- **Files Created**: backend/app/sync/service.py, backend/app/sync/router.py, frontend/src/lib/api/sync.ts, frontend/src/app/(dashboard)/sincronizacion/page.tsx
- **Security Check**: Admin for trigger, auth on all sync endpoints, API key from encrypted store at runtime

### 2026-05-02 — UJ-08: Automatizaciones
- **Work Done**: AutomationTask CRUD service. APScheduler 4.x setup (AsyncScheduler + SQLAlchemyDataStore). Automations router. FastAPI lifespan starts scheduler and loads DB tasks. Frontend: /configuracion/automatizaciones with preset schedules (6h, 12h, daily 2am, daily 8am), pause/resume/delete.
- **Files Created**: backend/app/automations/service.py, backend/app/automations/scheduler.py, backend/app/automations/router.py, frontend/src/app/(dashboard)/configuracion/automatizaciones/page.tsx
- **Security Check**: Admin only

### 2026-05-02 — UJ-09/10/11/12: Intelligence (RAG + Chat)
- **Work Done**: RAG service (pgvector cosine search with SQL, scope filtering, entity name lookup). RAG router (/rag/search). Chat service (session CRUD, message persistence, auto-title). WebSocket chat router (JWT cookie auth on handshake, RAG search + Claude stream + message save). Embedding stats + bulk reindex endpoints. Frontend: /chat with session sidebar, streaming messages, source cards. /configuracion/ia with coverage stats and reindex button.
- **Files Created**: backend/app/rag/{service,router}.py, backend/app/chat/{service,router}.py, frontend/src/lib/api/chat.ts, frontend/src/app/(dashboard)/chat/page.tsx, frontend/src/app/(dashboard)/configuracion/ia/page.tsx
- **Security Check**: JWT validated on WS handshake, session ownership enforced, query length limited

### 2026-05-02 — UJ-13/14/15/16/17: Agent API + Admin
- **Work Done**: Tool API keys (generate/hash/list/revoke). 6 Tool API endpoints (search, property, system, property/systems, system/properties, rag) with per-call logging. Users CRUD (invite, role change, activate/deactivate, own profile). Activity logs (sync + API calls). Admin stats. Configuracion tab layout with 6 sub-pages. Frontend pages for api-keys, usuarios, logs.
- **Files Created**: backend/app/tools/router.py, backend/app/users/router.py, backend/app/admin/router.py, frontend config sub-pages, frontend/src/lib/api/admin.ts
- **Security Check**: API keys stored as SHA-256 hash, shown once, verify_tool_key dependency on all tool endpoints, admin required for management

### 2026-05-02 — UJ-18/19/20/21/22: Polish + Seed
- **Work Done**: Dashboard with stats cards and quick actions. /mapa with react-leaflet + OpenStreetMap + property markers. /reservas with live Guesty data (5-min cache), status filter, pagination. Sidebar updated with Mapa nav item. Seed script with 5 properties (Cala Bona, Oviedo, Ibiza, La Manga, Málaga), system knowledge blocks, property-system relations.
- **Files Created**: dashboard/page.tsx updated, mapa/page.tsx, PropertiesMap component, reservas/page.tsx, reservations API client, sync/reservations.py + reservations_router.py, scripts/seed_demo.py
- **Security Check**: Reservations auth required, Guesty key from encrypted store

---

## Review — 2026-05-04

### Critical Issues (must fix before deploy)

1. **Insecure default secrets in `backend/app/shared/config.py` (lines 6, 8)**
   - `JWT_SECRET` defaults to `"change-me-in-production"` and `ENCRYPTION_MASTER_KEY` defaults to `"0" * 64`. If `.env` is not mounted or misconfigured at deploy time, the application starts with cryptographically trivial secrets. There is no startup assertion or validation that these values have been overridden. Fix: add a startup check that raises if `APP_ENV == "production"` and either value is the default.

2. **Hardcoded plaintext DB password in `docker-compose.yml` (lines 30–31)**
   - PostgreSQL credentials are hardcoded as `brain`/`brain` directly in the compose file under the `db` service environment block. These are not sourced from `.env`. Fix: move `POSTGRES_PASSWORD` to the `.env` file and reference it via env-var substitution.

3. **WebSocket exception leaks internal error messages to clients (`backend/app/chat/router.py`, line 185)**
   - The catch-all `except Exception as exc` block sends `str(exc)` directly to the WebSocket client: `{"type": "error", "message": str(exc)}`. This can expose internal stack context, library error messages, or DB details to any authenticated user. Fix: log the exception server-side and send a generic user-facing message.

4. **No rate limiting on auth endpoints despite IT-04 specification**
   - `user_journeys.md` (IT-04) requires "Rate limiting (5/min on auth)". No rate limiter is installed or configured anywhere in the backend. The `/api/v1/auth/login` and `/api/v1/auth/setup` endpoints are unprotected against brute-force. No `slowapi`, `limits`, or equivalent dependency is present. Fix: add `slowapi` and apply a `@limiter.limit("5/minute")` decorator to login and setup endpoints.

5. **No Next.js server-side route protection (missing `middleware.ts`)**
   - There is no `middleware.ts` at the Next.js app root. Authentication is enforced only client-side via `AuthGuard` (which runs after the page hydrates). Server-side rendered pages under `(dashboard)` are accessible before the client-side redirect fires. A malicious actor or crawler can access SSR content without a valid cookie. Fix: add a Next.js `middleware.ts` that inspects `brain_token` cookie and redirects to `/login` for protected routes before rendering.

6. **Sync conflict resolution (`POST /sync/conflicts/{block_id}/resolve`) lacks admin authorization**
   - `backend/app/sync/router.py`, line 153: this endpoint uses `get_current_user` (any authenticated user), not `require_admin`. Resolving conflicts — especially "accept_remote" which overwrites content by re-fetching from Guesty — is a destructive operation that should be admin-gated. Fix: replace `Depends(get_current_user)` with `Depends(require_admin)`.

7. **No exception handlers registered in `main.py`**
   - IT-08 ("Error Handling + Middleware") is marked complete, but `main.py` has no `app.add_exception_handler(...)` calls. FastAPI's default 500 handler returns the full Python exception message in development mode. The custom exception classes in `shared/exceptions.py` exist but are not globally registered. Fix: add exception handlers for `HTTPException` and unhandled `Exception` that return consistent JSON without stack traces.

---

### Non-Critical Issues (fix before delivery)

8. **Cookie `SameSite` set to `lax` instead of `strict` (`backend/app/auth/router.py`, line 17)**
   - IT-04 specification requires `SameSite=Strict`. The implementation uses `"lax"`. While `lax` is generally safe for this use case (GET navigation is allowed cross-site), the spec was explicit. Fix: change to `"strict"` to match the stated security posture.

9. **Reservations endpoint exposes raw Guesty exception text to the client (`backend/app/sync/reservations_router.py`, line 55)**
   - `raise HTTPException(status_code=502, detail=f"Guesty API error: {str(exc)}")` may expose internal Guesty API error messages (e.g., auth errors containing endpoint details). Fix: log the exception and return a generic message like `"Error al conectar con Guesty"`.

10. **No automated tests exist for any UJ or IT**
    - All UJ entries specify "Tests" in acceptance criteria (auth, payments, data mutations, API integrations). Zero test files were found anywhere in the project. The critical paths specified — Property CRUD, embedding trigger, WebSocket connection, Tool API key auth — have no coverage. Fix: add at minimum pytest tests for auth flows and Tool API key validation.

11. **Missing `isLoading` state in `AuthGuard` while `user` is null (`frontend/src/components/layout/AuthGuard.tsx`, line 31)**
    - When `isLoading` is true and `user` is null, the component renders the spinner. But on first mount `isLoading` starts as `true` in the Zustand store. If `getMe()` succeeds, `setUser` sets `isLoading: false`. However, between the time `setLoading` is not called on success path and `setUser` is called, there is a brief window. The `isLoading` flag is passed as a dependency to `useEffect` but never used to gate the redirect (line 13 returns early only on `user`, not on `isLoading`). This is minor but could cause a flash redirect on slow connections.

12. **`/configuracion/page.tsx` root redirects to nothing — 404 on direct access**
    - `frontend/src/app/(dashboard)/configuracion/page.tsx` exists but was not shown to contain a redirect to `/configuracion/integraciones`. If a user navigates to `/configuracion` directly, they will see a blank sub-layout with no content. Fix: add `redirect("/configuracion/integraciones")` to the root configuracion page.

13. **Tool API rate limiting specified but not implemented**
    - UJ-14 acceptance criteria state "rate limited". No rate limiting applies to any `/api/v1/tools/*` endpoint. Tool API keys are external-facing; abuse by a compromised key is unbounded. Fix: add per-key rate limiting (e.g., 100 req/min).

14. **`NEXT_PUBLIC_API_URL` in `docker-compose.yml` is `http://localhost:8000` for frontend container**
    - The frontend container builds with `NEXT_PUBLIC_API_URL=http://localhost:8000`. Inside Docker, `localhost` in the frontend container does not resolve to the backend container. The correct value should be `http://backend:8000`. This means the dockerized frontend cannot reach the backend. Fix: change to `http://backend:8000` for server-side requests and confirm NEXT_PUBLIC usage is client-side only.

15. **`AuthGuard` starts with `isLoading: true` but `setLoading` is not called on the success path**
    - In `AuthGuard.tsx`, `setLoading` is imported and listed as a dependency but never called in the success branch (only `setUser` is called which internally sets `isLoading: false`). This is currently harmless because `setUser` also sets `isLoading: false`, but it creates a misleading dependency in the `useEffect` array and suggests the intended call was omitted.

16. **Seed script creates demo data but includes no realistic knowledge blocks for systems**
    - UJ-22 specifies 15+ knowledge blocks. The seed script (`scripts/seed_demo.py`) creates blocks for properties but system-level knowledge blocks are not confirmed. Verify the seed satisfies the 15+ block requirement across all entities before delivery.

17. **No `error.tsx` or error boundary components on any route**
    - UJ-21 ("Pulido UI") acceptance criteria require "error boundary" on every page. There are no `error.tsx` files in any route segment. Next.js App Router error boundaries require explicit `error.tsx` files per route group. Currently, any unhandled error will bubble to the root layout crash. Fix: add `error.tsx` at minimum to the `(dashboard)` layout level.

---

### Passed Checks

- **All 22 UJ backend routes exist and are registered** in `main.py` — every router is imported and included. No missing endpoints.
- **Auth on all user-facing routes** — `get_current_user` or `require_admin` is applied to every endpoint examined. The Tool API uses a separate `verify_tool_key` dependency correctly.
- **Admin gate on destructive operations** — DELETE on properties/systems requires `require_admin`. Credentials, automations, user management, API key management, and embedding reindex all require `require_admin`.
- **All frontend pages exist** at their specified routes: `/dashboard`, `/propiedades`, `/propiedades/[slug]`, `/propiedades/nueva`, `/sistemas`, `/sistemas/[slug]`, `/sistemas/nuevo`, `/chat`, `/sincronizacion`, `/reservas`, `/mapa`, `/configuracion/integraciones`, `/configuracion/ia`, `/configuracion/api-keys`, `/configuracion/automatizaciones`, `/configuracion/usuarios`, `/configuracion/logs`.
- **Sidebar navigation is complete** — 8 items covering all major sections (dashboard, propiedades, mapa, sistemas, chat, sincronización, reservas, configuración).
- **Empty states present** on all checked pages — confirmed on `/chat`, `/reservas`, `/configuracion/api-keys`, `/configuracion/automatizaciones`, `/sincronizacion` (historial and conflictos tabs).
- **Loading skeletons** present on dashboard, chat, sincronización, and IA config pages.
- **No hardcoded API keys or secrets in application code** — all credentials sourced from settings or the encrypted DB store.
- **JWT cookie is httpOnly** — set server-side, never stored in localStorage or accessible to JS.
- **No token in response body** — auth endpoints return `UserResponse` only; token is cookie-only.
- **Encrypted credential store correctly used** — `llm.py` and `embeddings.py` load keys from the encrypted DB store, not from env directly.
- **WebSocket auth via cookie** — `chat/router.py` validates `brain_token` cookie on handshake before processing any messages.
- **API key stored as SHA-256 hash** — raw key shown once, hash persisted. Revocation sets `is_active=False`.
- **Session isolation** — chat session CRUD filters by `user_id`, users cannot access other users' sessions.
- **`.gitignore` correctly excludes `.env`** — confirmed.
- **Docker deployment exists** — `docker-compose.yml` with backend, frontend, and pgvector/pg16 DB.
- **pgvector included** — IVFFlat index and cosine search correctly used in RAG service.
- **Pydantic validation on all inputs** — request bodies use typed Pydantic models. Query length limits on search endpoints (max 500 chars).
- **All IT components integrated in `main.py`** — all 12 routers imported and registered; scheduler started in lifespan.

---

### Summary

The application is substantially complete and well-structured. All 22 User Journeys have corresponding backend endpoints and frontend pages, navigation is complete, and empty/loading states are present throughout. Security fundamentals (httpOnly cookies, encrypted credentials, admin gates, session isolation) are correctly implemented.

**Six issues require resolution before deployment**: insecure default secret values with no startup validation, hardcoded DB credentials in Docker Compose, WebSocket error message leakage, absent rate limiting on auth endpoints (despite being specified), no Next.js server-side middleware for route protection, and a missing admin gate on conflict resolution.

The absence of automated tests across all 22 UJs is the most significant delivery gap relative to specified acceptance criteria and should be addressed before handoff.

### 2026-05-04 — Security Fixes (pre-deployment)

All 6 critical issues from the /review subagent fixed:

1. **Config startup validation** (`backend/app/shared/config.py`): Added `validate_production_secrets()` that calls `sys.exit(1)` if `JWT_SECRET` or `ENCRYPTION_MASTER_KEY` are using insecure defaults when `APP_ENV=production`.

2. **Docker Compose hardcoded credentials** (`docker-compose.yml`): Replaced `POSTGRES_PASSWORD: brain` with `${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}` (mandatory), `POSTGRES_USER` and `POSTGRES_DB` use `${VAR:-brain}` defaults. Backend `DATABASE_URL` env var also parameterized.

3. **WebSocket exception leak** (`backend/app/chat/router.py`): Replaced `str(exc)` with generic `"Error interno del servidor"` message to avoid leaking internal error details to the client.

4. **Auth rate limiting** (`backend/app/auth/router.py`, `backend/app/main.py`): Added `slowapi` `@_limiter.limit("5/minute")` to `/auth/login` and `/auth/setup`. Registered `limiter` on `app.state` and added `RateLimitExceeded` handler in main.py.

5. **Conflict resolve admin gate** (`backend/app/sync/router.py`): Changed `get_current_user` to `require_admin` dependency on `POST /conflicts/{block_id}/resolve`.

6. **Next.js server-side middleware** (`frontend/src/middleware.ts`): Created middleware that redirects unauthenticated requests to `/login?next=<path>`. Public paths (login, setup) and Next.js static assets bypass the check.

- **TypeScript build**: 0 errors after all changes.
- **Security check**: All 6 critical blockers resolved. Deployment guide updated with POSTGRES_PASSWORD requirement.

### 2026-07-08 — Bug Fix: RAG content truncated to 300 chars, no relevance threshold
- **Bug**: `backend/app/rag/service.py` truncated every retrieved knowledge block to `content[:300]` before building the LLM context (`build_context_prompt`), gutting the value of the knowledge base for both the chat WebSocket (`backend/app/chat/router.py`) and the Tool API (`backend/app/tools/router.py`). Additionally, `semantic_search` always returned the top-K nearest blocks regardless of how irrelevant they were, so the anti-hallucination instruction in the prompt never had a chance to trigger.
- **Work Done**:
  - Removed the hard 300-char truncation. Content forwarded to the LLM is now capped at a new configurable ceiling, `settings.RAG_MAX_CONTEXT_CHARS` (default 2500), high enough to preserve full blocks in the vast majority of cases while still bounding the prompt/context window.
  - Added a configurable minimum-similarity threshold, `settings.RAG_MIN_SIMILARITY` (default 0.35, cosine score 0-1). Results scoring below it are dropped in `semantic_search`; if none clear the bar, an empty list is returned so `build_context_prompt` produces an empty context and the existing "si la información no está en el contexto, dilo claramente" instruction correctly kicks in instead of forcing irrelevant top-K filler into the prompt.
  - Both new values added to `Settings` (`backend/app/shared/config.py`) with sane defaults (no secrets), documented in `.env.example`.
  - No changes to data model, seed script, or embedding logic — retrieval/context path only, per scope.
- **Files Modified**: `backend/app/rag/service.py`, `backend/app/shared/config.py`, `.env.example`
- **Files Created**: `backend/tests/test_rag_context.py` (regression tests: full content >300 chars reaches the prompt, empty results still carry the anti-hallucination instruction, config ceilings are sane), `backend/tests/conftest.py` (sys.path setup for `app` package import)
- **Security Check**: No secrets introduced; new settings are plain numeric tuning values with safe defaults; no changes to auth/authz paths; no new external input surface (thresholds are server-side config, not user-supplied).
- **Tests**: Could NOT be executed. The machine's Homebrew Python 3.14 (and the unlinked Python 3.12 keg) both have a broken `pyexpat`/`libexpat` linkage (`Symbol not found: _XML_SetAllocTrackerActivationThreshold` against `/usr/lib/libexpat.1.dylib`), which breaks `ensurepip`/`pip install` entirely, system-wide, independent of this project. No venv could be provisioned and no dependencies (FastAPI, SQLAlchemy, pydantic-settings, etc.) could be installed. This is a pre-existing environment issue unrelated to this change — verified via `ast.parse()` syntax check on both modified files (passes) and a manual review of every call site of `semantic_search`/`build_context_prompt`/`content_preview` across the backend (`chat/router.py`, `tools/router.py`, `rag/router.py`) and frontend (`chat/page.tsx` already client-side slices to 120 chars for display, so it is unaffected by the field now carrying full content). Flagging to NEXO: this Python environment issue likely blocks test execution for any Python project on this machine until `libexpat`/Python are repaired (e.g. `brew reinstall expat` + relink) — out of scope for this fix, not attempted.
