# Open Questions & Assumptions

## Answered Questions

### Q1: Chat LLM Provider
- **Status**: Answered
- **Answer**: Anthropic Claude only. OpenAI for embeddings only.

### Q2: Optional Features — V1 Scope
- **Status**: Answered
- **Answer**: Include both (map view + reservations read-only view) in V1.

### Q3: Approximate Property Count
- **Status**: Answered
- **Answer**: 30-100 properties (medium portfolio)

### Q4: UI Language
- **Status**: Answered
- **Answer**: Spanish UI, English code/API

---

## Non-Blocking Assumptions (confirmed by proceeding)

| # | Assumption | Proceeding with |
|---|-----------|-----------------|
| A1 | Guesty API access | Team has/will obtain Guesty Pro Open API credentials |
| A2 | Deployment | Single VPS via EasyPanel, no multi-environment |
| A3 | Users | 1-5 team members, no public access, no multi-tenancy |
| A4 | Embedding model | text-embedding-3-small (1536 dims) |
| A5 | WebSocket | Native FastAPI WebSocket for chat streaming |
| A6 | Vikey | Single system entity with category "access", tag includes "checkin" |
