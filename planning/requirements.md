# Requirements

## Functional Requirements

### Core Features

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-01 | Property CRUD with structured metadata | High | Name, type, region, capacity, status, tags, JSONB metadata |
| FR-02 | System CRUD (integrated tools registry) | High | Category enum, API docs URL, status |
| FR-03 | Knowledge Blocks (polymorphic, attached to property or system) | High | Block types: description, rules, access, faq, sop, integration_guide, pricing_notes, checkin_notes, custom |
| FR-04 | Property-System relations (many-to-many with config) | High | Notes + JSONB config per relation |
| FR-05 | Guesty API sync (read-only, manual + scheduled) | High | Create/update properties + seed knowledge blocks from listings |
| FR-06 | Conflict resolution (Guesty sync vs manual edits) | Medium | Manual edits never overwritten, flag conflicts for user resolution |
| FR-07 | RAG semantic search (pgvector cosine similarity) | High | Embed query → top-K retrieval → filter by scope |
| FR-08 | RAG Chat with Claude (streaming via WebSocket) | High | Source attribution, session management, scope selector |
| FR-09 | AI Agent Tool API (HTTP, API key auth) | High | search, property, system, relations, rag endpoints |
| FR-10 | Setup wizard (first admin creation) | High | Disabled after first user created |
| FR-11 | Credential management (AES-256-GCM encrypted) | High | Guesty key, OpenAI key, Anthropic key stored in DB |
| FR-12 | User management (admin: invite, roles, deactivate) | Medium | Admin + User roles |
| FR-13 | Automation tasks (scheduled sync via APScheduler) | Medium | Cron/interval config, pause/resume |
| FR-14 | Dashboard with stats and activity feed | Medium | Property count, system count, KB count, sync status |
| FR-15 | Properties map view (geocoded pins) | Medium | Interactive map with clustering, status color-coding |
| FR-16 | Reservations read-only view (from Guesty API) | Medium | On-demand fetch, short-term cache, filter by property/date/status |
| FR-17 | Sync history logs and monitoring | Medium | Per-sync: items processed, created, updated, errors |
| FR-18 | Tool API key management | Medium | Create (show once), list (masked), revoke |
| FR-19 | Tool API call logging | Low | Endpoint, params, response_ms, results_count |
| FR-20 | Embedding health monitoring and re-indexing | Low | Coverage stats, bulk re-embed trigger |

### Admin Panel (Mandatory)
- Sync logs and execution history
- AI token usage tracking (OpenAI embeddings + Anthropic chat)
- API key and credential management (Level 3)
- System configuration (AI models, RAG params)
- User management

## Non-Functional Requirements
See `docs/nfr.md` for performance, accessibility, security, and observability requirements.

## Out of Scope
See `planning/scope.md` for explicit exclusions.
