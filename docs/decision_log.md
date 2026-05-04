# Decision Log

## Decisions

### 2026-05-02 — Chat LLM: Anthropic Claude (not OpenAI)
- **Decision**: Use Anthropic Claude for RAG chat responses; OpenAI only for embeddings
- **Rationale**: User chose Claude for better reasoning and Spanish fluency. Keeps embedding provider separate from chat provider.
- **Alternatives Considered**: OpenAI GPT-4o (simpler, one provider), Both switchable (more complex)
- **Impact**: Need Anthropic SDK dependency + API key as Level 3 credential. Two AI providers to manage.
- **Reversibility**: Easy — provider-abstracted service layer

### 2026-05-02 — V1 includes map view and reservations
- **Decision**: Include properties map (Leaflet/OpenStreetMap) and Guesty reservations read-only view in V1
- **Rationale**: User wants full feature set from launch despite additional implementation time
- **Alternatives Considered**: Defer both to post-delivery
- **Impact**: +6 sessions. Need geocoding (or manual lat/lng), Leaflet dependency, Guesty reservations API integration with caching
- **Reversibility**: Easy — additive features, no architectural impact

### 2026-05-02 — Spanish UI, English code/API
- **Decision**: All user-facing UI text in Spanish. Code, API, variable names, comments in English
- **Rationale**: Team is Spanish-speaking, no i18n complexity needed for single language
- **Alternatives Considered**: English UI, Bilingual with i18n
- **Impact**: All labels, toasts, error messages, empty states written in Spanish. No i18n library needed.
- **Reversibility**: Medium — would need i18n extraction later if bilingual needed

### 2026-05-02 — pgvector IVFFlat index (not HNSW)
- **Decision**: Use IVFFlat with lists=10 for vector similarity search
- **Rationale**: 30-100 properties × ~5 blocks each = 150-500 vectors. IVFFlat is simpler and sufficient at this scale.
- **Alternatives Considered**: HNSW (better recall but heavier), no index (sequential scan OK at <1000 rows)
- **Impact**: May need to switch to HNSW if knowledge blocks exceed several thousand
- **Reversibility**: Easy — just recreate the index

### 2026-05-02 — WebSocket for chat streaming (not SSE)
- **Decision**: Native FastAPI WebSocket for real-time chat
- **Rationale**: Bidirectional communication, matches spec requirement, FastAPI native support
- **Alternatives Considered**: Server-Sent Events (simpler but unidirectional), HTTP polling
- **Impact**: Need WS connection management, reconnection logic, JWT auth on handshake
- **Reversibility**: Medium — would need to rewrite chat transport layer

### 2026-05-02 — Map library: react-leaflet + OpenStreetMap
- **Decision**: Use react-leaflet with free OpenStreetMap tiles
- **Rationale**: No API key needed, free, good enough for 30-100 pins, well-maintained React bindings
- **Alternatives Considered**: MapLibre GL (more performant but heavier), Google Maps (cost, API key complexity)
- **Impact**: Frontend dependency. Properties need lat/lng coordinates (can be entered manually or geocoded from address).
- **Reversibility**: Easy — swap map component
