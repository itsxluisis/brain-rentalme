# Scope

## In Scope (V1 Delivery)

- Full property + system + knowledge block CRUD
- Property-system many-to-many relations with per-relation config
- Guesty read-only sync (listings → properties + knowledge blocks)
- Sync scheduling via APScheduler, conflict detection/resolution
- RAG pipeline: OpenAI embeddings + pgvector search + Anthropic Claude chat
- Streaming chat via WebSocket with source attribution
- AI Agent Tool API (6 endpoints, API key auth, logging)
- Dashboard with stats, activity feed, quick actions
- Properties map view (Leaflet + OpenStreetMap)
- Reservations read-only view (live from Guesty API)
- Admin panel: credentials, users, integrations, AI config
- JWT auth (httpOnly cookies), role-based access (admin/user)
- Docker + docker-compose deployment (EasyPanel ready)
- Seed script with realistic demo data
- Spanish UI, English code/API

## Out of Scope

- Multi-tenancy (single company: RentalMe.es)
- Write operations to Guesty (read-only sync only)
- Cloudbeds sync implementation (schema prepared, stub only)
- INTO / UpMarket API integrations (no open API — manual entry only)
- Mobile native apps
- Email notifications or alerts
- File/image uploads (knowledge is text-only)
- Versioning/history of knowledge block edits
- Public-facing pages (fully private, auth-gated)
- i18n infrastructure (Spanish only, no language switcher)
- Real-time collaborative editing

## Assumptions

- Team has/will obtain Guesty Pro Open API credentials
- Single VPS deployment via EasyPanel
- 1-5 concurrent users maximum
- 30-100 properties, scaling to a few hundred knowledge blocks
- Modern browsers only (Chrome, Firefox, Safari latest 2 versions)
- OpenAI API access for embeddings (text-embedding-3-small)
- Anthropic API access for chat completions (Claude)

## Deferred (Post-Delivery Iteration)

- Cloudbeds sync implementation
- Knowledge block edit history/versioning
- Webhook notifications on sync events
- Multi-language knowledge blocks (auto-translate)
- Advanced analytics (chat usage patterns, popular topics)
- Custom embedding models / fine-tuning
- Bulk import/export of knowledge blocks (CSV/JSON)
