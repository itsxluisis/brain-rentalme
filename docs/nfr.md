# Non-Functional Requirements

## Performance
- API response: <500ms for CRUD, <2s for RAG search, <5s for sync trigger response
- Page load (FCP): <1.5s on standard connection
- Chat streaming: first token <1s after query
- Concurrent users: up to 5 simultaneous (internal team only)
- Embedding generation: <3s per block (background, non-blocking)

## Accessibility
- Keyboard navigation for all interactive elements
- Sufficient color contrast in both themes (WCAG AA)
- Focus indicators on interactive elements
- Screen reader: semantic HTML, aria-labels on icon-only buttons

## Security
- JWT: 24h expiry, httpOnly, Secure, SameSite=Strict
- Rate limiting: 5 attempts/min on auth, 60 req/min general, 30 req/min on AI endpoints
- Credential handling: 3-level model (env / deployment / admin panel AES-256-GCM)
- Input validation: Pydantic on all endpoints, Zod on all frontend forms
- No sensitive data in logs or error responses
- Tool API keys: SHA-256 hashed, revocable, usage logged

## Observability
- Structured JSON logging (request ID, user ID, endpoint, duration)
- Sync events logged with full stats
- Tool API calls logged (endpoint, params, response time, results count)
- AI token usage tracked per request (embeddings + chat)
- Health check endpoint: GET /api/v1/health

## Scalability
- Properties: 30-100 now, design for up to 500
- Knowledge blocks: 150-500 now, design for up to 5000
- Chat sessions: unlimited per user, paginated
- Vector index: IVFFlat (lists=10), switch to HNSW if >5000 vectors

## Browser / Device Support
- Chrome, Firefox, Safari: latest 2 versions
- Mobile-responsive: usable on tablet, functional on phone (not optimized)
- Dark mode default, light mode available

## Compliance
- No guest PII stored locally (reservations fetched on-demand from Guesty, not persisted)
- Credentials encrypted at rest (AES-256-GCM)
- No analytics or tracking on the internal tool
- Data residency: same VPS as existing RentalMe.es stack (Spain/EU)
