# API Contracts

All endpoints under `/api/v1`. Auth via httpOnly JWT cookie unless noted.

## Conventions
- Base URL: `/api/v1`
- Auth: JWT in httpOnly cookie (auto-sent with `withCredentials: true`)
- Tool API: `Authorization: Bearer <api-key>` header (separate from JWT)
- Error shape: `{ "detail": "message" }` (FastAPI default)
- Pagination: `{ "items": [], "total": int, "page": int, "limit": int }`
- Timestamps: ISO 8601 UTC

---

## Authentication (`/api/v1/auth`)

### POST /auth/setup
- **Auth**: Public (disabled after first user exists)
- **Request**: `{ email, password, full_name }`
- **Response 201**: `{ id, email, full_name, role: "admin" }` + sets httpOnly cookie
- **Response 409**: Setup already completed

### POST /auth/login
- **Auth**: Public
- **Request**: `{ email, password }`
- **Response 200**: `{ id, email, full_name, role }` + sets httpOnly cookie
- **Response 401**: Invalid credentials
- **Rate limit**: 5/min

### POST /auth/logout
- **Auth**: Required
- **Response 200**: `{}` + clears cookie

### POST /auth/refresh
- **Auth**: Required (valid cookie)
- **Response 200**: `{ id, email, full_name, role }` + new cookie

### GET /auth/me
- **Auth**: Required
- **Response 200**: `{ id, email, full_name, role, last_login_at }`

---

## Users (`/api/v1/users`) — Admin only

### GET /users
- **Response 200**: Paginated list `{ items: [User], total, page, limit }`

### POST /users
- **Request**: `{ email, password, full_name, role }`
- **Response 201**: `{ id, email, full_name, role, is_active }`

### PATCH /users/:id
- **Request**: `{ full_name?, role?, is_active? }`
- **Response 200**: Updated user

### DELETE /users/:id
- **Response 204**: Deactivated (soft)

---

## Properties (`/api/v1/properties`)

### GET /properties
- **Auth**: Required
- **Query**: `?page=1&limit=20&region=&type=&status=&search=`
- **Response 200**: Paginated `{ items: [PropertySummary], total, page, limit }`
- PropertySummary: `{ id, name, slug, type, region, status, capacity, knowledge_block_count, systems_count }`

### POST /properties
- **Auth**: Required
- **Request**: `{ name, type, region, address?, latitude?, longitude?, capacity?, bedrooms?, bathrooms?, status?, tags?, metadata_? }`
- **Response 201**: Full property object (slug auto-generated)

### GET /properties/:slug
- **Auth**: Required
- **Response 200**: Full property + `knowledge_blocks[]` + `linked_systems[]`

### PATCH /properties/:slug
- **Auth**: Required
- **Request**: Partial property fields
- **Response 200**: Updated property

### DELETE /properties/:slug
- **Auth**: Admin
- **Response 204**

### GET /properties/:slug/systems
- **Auth**: Required
- **Response 200**: `[{ system: SystemSummary, notes, config, relation_id }]`

---

## Systems (`/api/v1/systems`)

### GET /systems
- **Auth**: Required
- **Query**: `?page=1&limit=20&category=&status=&search=`
- **Response 200**: Paginated `{ items: [SystemSummary], total, page, limit }`

### POST /systems
- **Auth**: Required
- **Request**: `{ name, category, description?, website_url?, has_api?, api_docs_url?, status?, tags?, metadata_? }`
- **Response 201**: Full system (slug auto-generated)

### GET /systems/:slug
- **Auth**: Required
- **Response 200**: Full system + `knowledge_blocks[]` + `linked_properties[]`

### PATCH /systems/:slug
- **Auth**: Required
- **Request**: Partial system fields
- **Response 200**: Updated system

### DELETE /systems/:slug
- **Auth**: Admin
- **Response 204**

### GET /systems/:slug/properties
- **Auth**: Required
- **Response 200**: `[{ property: PropertySummary, notes, config, relation_id }]`

---

## Knowledge Blocks (`/api/v1/knowledge`)

### GET /knowledge
- **Auth**: Required
- **Query**: `?entity_type=&entity_id=&block_type=&search=&page=1&limit=20`
- **Response 200**: Paginated blocks

### POST /knowledge
- **Auth**: Required
- **Request**: `{ entity_type, entity_id, block_type, title, content, language?, metadata_? }`
- **Response 201**: Block (content_vector=null, embedding pending)

### GET /knowledge/:id
- **Auth**: Required
- **Response 200**: Full block

### PATCH /knowledge/:id
- **Auth**: Required
- **Request**: `{ title?, content?, block_type?, language?, is_active?, metadata_? }`
- **Response 200**: Updated block (re-embeds if content changed)

### DELETE /knowledge/:id
- **Auth**: Required
- **Response 204**

### POST /knowledge/:id/embed
- **Auth**: Admin
- **Response 202**: `{ status: "embedding_queued" }` — triggers re-embedding

---

## Relations (`/api/v1/relations`)

### POST /relations
- **Auth**: Required
- **Request**: `{ property_id, system_id, notes?, config? }`
- **Response 201**: Relation object

### PATCH /relations/:id
- **Auth**: Required
- **Request**: `{ notes?, config? }`
- **Response 200**: Updated relation

### DELETE /relations/:id
- **Auth**: Required
- **Response 204**

---

## Sync (`/api/v1/sync`)

### POST /sync/trigger
- **Auth**: Admin
- **Request**: `{ provider: "guesty" }`
- **Response 202**: `{ sync_log_id, status: "running" }`

### GET /sync/status
- **Auth**: Required
- **Response 200**: `{ last_sync: SyncLog, next_scheduled: datetime?, is_running: bool }`

### GET /sync/logs
- **Auth**: Required
- **Query**: `?page=1&limit=20`
- **Response 200**: Paginated sync logs

### GET /sync/conflicts
- **Auth**: Required
- **Response 200**: `[{ block_id, title, local_content, remote_content, last_synced_at }]`

### POST /sync/conflicts/:block_id/resolve
- **Auth**: Required
- **Request**: `{ resolution: "keep_local" | "accept_remote" }`
- **Response 200**: Resolved block

---

## RAG (`/api/v1/rag`)

### POST /rag/search
- **Auth**: Required
- **Request**: `{ query: string, scope?: "all"|"properties"|"systems", entity_id?: uuid, limit?: int (default 5) }`
- **Response 200**: `{ results: [{ block_id, title, content_preview, entity_type, entity_id, entity_name, score }] }`

---

## Chat (`/api/v1/chat`)

### GET /chat/sessions
- **Auth**: Required
- **Response 200**: `[{ id, title, scope, updated_at, last_message_preview }]`

### POST /chat/sessions
- **Auth**: Required
- **Request**: `{ scope?, scope_entity_id? }`
- **Response 201**: New session

### GET /chat/sessions/:id
- **Auth**: Required (owner only)
- **Response 200**: Session + messages

### PATCH /chat/sessions/:id
- **Auth**: Required (owner only)
- **Request**: `{ title? }`
- **Response 200**: Updated session

### DELETE /chat/sessions/:id
- **Auth**: Required (owner only)
- **Response 204**

### WebSocket /chat/ws/:session_id
- **Auth**: JWT validated on handshake
- **Client sends**: `{ type: "message", content: string }`
- **Server sends**: `{ type: "token", content: string }` (streaming) → `{ type: "done", sources: [...] }` (completion)

---

## Tool API (`/api/v1/tools`) — API Key Auth

### GET /tools/search
- **Auth**: API Key (Bearer)
- **Query**: `?q=string&entity_type=property|system&limit=5`
- **Response 200**: `{ results: [{ entity_type, slug, name, relevance_score, preview }] }`

### GET /tools/property/:slug
- **Auth**: API Key
- **Response 200**: `{ name, slug, type, region, capacity, status, knowledge_blocks: [{title, content, block_type}] }`

### GET /tools/system/:slug
- **Auth**: API Key
- **Response 200**: `{ name, slug, category, description, knowledge_blocks: [{title, content, block_type}] }`

### GET /tools/property/:slug/systems
- **Auth**: API Key
- **Response 200**: `{ systems: [{ name, slug, category, notes, config }] }`

### GET /tools/system/:slug/properties
- **Auth**: API Key
- **Response 200**: `{ properties: [{ name, slug, type, region, notes, config }] }`

### POST /tools/rag
- **Auth**: API Key
- **Request**: `{ query, scope?: "all"|"properties"|"systems", limit?: 5 }`
- **Response 200**: `{ answer: string, sources: [{ entity_type, entity_name, block_title, relevance_score }] }`

---

## Automations (`/api/v1/automations`)

### GET /automations
- **Auth**: Admin
- **Response 200**: `[AutomationTask]`

### POST /automations
- **Auth**: Admin
- **Request**: `{ name, action_type, schedule_type, schedule_config, is_active? }`
- **Response 201**: Task

### PATCH /automations/:id
- **Auth**: Admin
- **Request**: Partial fields
- **Response 200**: Updated task

### DELETE /automations/:id
- **Auth**: Admin
- **Response 204**

### POST /automations/:id/trigger
- **Auth**: Admin
- **Response 202**: `{ status: "triggered" }`

---

## Admin (`/api/v1/admin`)

### GET /admin/stats
- **Auth**: Admin
- **Response 200**: `{ properties_count, systems_count, knowledge_blocks_count, blocks_with_embeddings, last_sync, active_users }`

### GET /admin/activity
- **Auth**: Admin
- **Query**: `?page=1&limit=20&type=`
- **Response 200**: Paginated activity events

---

## Credentials (`/api/v1/credentials`)

### GET /credentials
- **Auth**: Admin
- **Response 200**: `[{ id, service_name, updated_at, has_value: bool }]` (never returns actual values)

### PUT /credentials/:service_name
- **Auth**: Admin
- **Request**: `{ value: string }`
- **Response 200**: `{ service_name, updated_at }`

### DELETE /credentials/:service_name
- **Auth**: Admin
- **Response 204**

### POST /credentials/:service_name/test
- **Auth**: Admin
- **Response 200**: `{ status: "ok"|"error", message?: string }`

---

## Reservations (`/api/v1/reservations`)

### GET /reservations
- **Auth**: Required
- **Query**: `?property_slug=&status=&from_date=&to_date=&page=1&limit=20`
- **Response 200**: `{ items: [Reservation], total, page, limit }`
- Reservation: `{ id, guest_name, property_name, property_slug, check_in, check_out, status, channel, guests_count }`
- **Notes**: Fetched live from Guesty, cached 5min

---

## Health

### GET /health
- **Auth**: Public
- **Response 200**: `{ status: "ok", version: string, db: "connected"|"error" }`
