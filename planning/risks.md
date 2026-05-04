# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|----|------|-----------|--------|------------|--------|
| R-01 | Guesty API rate limits block sync | Medium | Medium | Exponential backoff + batch requests (max 5 concurrent). Cache responses. | Open |
| R-02 | Guesty API changes or deprecated endpoints | Low | High | Provider abstraction layer. Pin to known API version. Monitor changelog. | Open |
| R-03 | pgvector IVFFlat index quality at low row count | Medium | Low | Start without index, add IVFFlat once >500 knowledge blocks. HNSW as fallback. | Open |
| R-04 | OpenAI embedding costs spike with frequent re-indexing | Low | Low | Batch embeddings, only re-embed on content change, track token usage in admin. | Open |
| R-05 | WebSocket connection drops (unreliable on some corporate networks) | Medium | Medium | Automatic reconnection with exponential backoff. Fallback to SSE if WS fails. | Open |
| R-06 | Credential encryption key rotation complexity | Low | High | Document key rotation procedure. V1: single master key, rotation deferred. | Open |
| R-07 | APScheduler 4.x instability (relatively new major version) | Low | Medium | Minimal scheduler usage (sync only). Can fallback to simple cron if issues arise. | Open |
| R-08 | Scope creep from "just add this one thing" | Medium | Medium | Strict scope.md boundaries. Defer to iteration. Ask before adding. | Open |
| R-09 | Large knowledge blocks exceeding context window for RAG | Medium | Medium | Chunk large blocks (>2000 tokens) into sub-blocks during embedding. Configurable chunk size. | Open |
| R-10 | EasyPanel deployment config incompatibilities | Low | Medium | Test Docker build early (IT-01). Document EasyPanel-specific settings. | Open |
