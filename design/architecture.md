# Architecture

## System Overview
(High-level description of the system — populated during planning)

## Module Structure

### Backend
(Module list, responsibilities, and communication patterns — populated during planning)

### Frontend
(Page/component structure, routing, state management approach — populated during planning)

## Infrastructure
(Deployment topology, service boundaries, container layout — populated during planning)

## Credential Level Mapping

| Credential | Level | Storage |
|-----------|-------|---------|
| DATABASE_URL | 1 | .env |
| JWT_SECRET | 1 | .env |
| ENCRYPTION_MASTER_KEY | 1 | .env |
| Service URLs | 2 | EasyPanel env vars |
| Feature flags | 2 | EasyPanel env vars |
| Third-party API keys | 3 | Admin panel (AES-256 encrypted) |

(Add project-specific credentials during planning)

## Key Architecture Decisions
See `docs/decision_log.md` for rationale behind major choices.
