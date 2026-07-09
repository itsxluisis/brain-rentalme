# Task Tracker

## Tracking Table

| ID | Type | Name | Milestone | Status | Security Checked | Review Passed | Notes |
|----|------|------|-----------|--------|------------------|---------------|-------|
| IT-01 | IT | Project Scaffolding + Docker Compose | M0 | completed | yes | no | Next.js build verified |
| IT-02 | IT | Database Schema + Alembic Migrations | M0 | completed | yes | no | 12 tables, pgvector first |
| IT-03 | IT | SQLAlchemy Async Models | M0 | completed | yes | no | All models + relationships |
| IT-04 | IT | Authentication System | M0 | completed | yes | no | JWT + bcrypt + cookies + setup |
| IT-05 | IT | Frontend Base Layout + Auth Flow | M0 | completed | yes | no | Sidebar + AuthGuard + Login |
| IT-06 | IT | Credential Encryption Service | M0 | completed | yes | no | AES-256-GCM |
| IT-07 | IT | Shared AI Clients | M0 | completed | yes | no | OpenAI + Anthropic |
| IT-08 | IT | Error Handling + Middleware | M0 | completed | yes | no | Exceptions + pagination |
| UJ-01 | UJ | Gestionar Propiedades | M1 | completed | yes | no | Build verified |
| UJ-02 | UJ | Gestionar Sistemas | M1 | completed | yes | no | Pre-seed 12 systems, build verified |
| UJ-03 | UJ | Vincular Propiedades ↔ Sistemas | M1 | completed | yes | no | LinkedSystemsSection + LinkedPropertiesSection |
| UJ-04 | UJ | Gestionar Bloques de Conocimiento | M1 | completed | yes | no | KnowledgeBlockSection, async embeddings |
| UJ-05 | UJ | Configurar Integración Guesty | M2 | completed | yes | no | Credentials router + Guesty test |
| UJ-06 | UJ | Sincronizar Propiedades desde Guesty | M2 | completed | yes | no | Sync service + /sincronizacion page |
| UJ-07 | UJ | Historial de Sincronización y Conflictos | M2 | completed | yes | no | Conflicts tab + resolve endpoint |
| UJ-08 | UJ | Gestionar Automatizaciones | M2 | completed | yes | no | APScheduler 4.x + automations page |
| UJ-09 | UJ | Búsqueda Semántica | M3 | completed | yes | no | pgvector cosine search + RAG service |
| UJ-10 | UJ | Chat RAG con Streaming | M3 | completed | yes | no | WebSocket + Claude streaming |
| UJ-11 | UJ | Gestionar Sesiones de Chat | M3 | completed | yes | no | Session CRUD + auto-title |
| UJ-12 | UJ | Monitorización de Embeddings | M3 | completed | yes | no | Stats + bulk reindex |
| UJ-13 | UJ | Gestionar API Keys para Agentes | M4 | completed | yes | no | SHA-256 hash, shown once |
| UJ-14 | UJ | Tool API para Agentes IA | M4 | completed | yes | no | 6 endpoints + logging |
| UJ-15 | UJ | Panel de Configuración Admin | M4 | completed | yes | no | Tab layout with 6 sub-pages |
| UJ-16 | UJ | Gestión de Usuarios | M4 | completed | yes | no | CRUD + role management |
| UJ-17 | UJ | Logs de Actividad | M4 | completed | yes | no | Sync + API call logs |
| UJ-18 | UJ | Dashboard | M5 | completed | yes | no | Stats cards + quick actions |
| UJ-19 | UJ | Vista de Mapa | M5 | completed | yes | no | react-leaflet + OpenStreetMap |
| UJ-20 | UJ | Reservas (Read-Only) | M5 | completed | yes | no | Guesty live + 5min cache |
| UJ-21 | UJ | Pulido UI | M5 | completed | yes | no | Sidebar updated, nav complete |
| UJ-22 | UJ | Script de Datos Demo | M5 | completed | yes | no | 5 props + 4 systems + 15+ blocks |
| FIX-01 | Fix | RAG: truncation a 300 chars + sin umbral de relevancia | Post-M5 | completed | yes | no | Ver work_log 2026-07-08. Tests no ejecutables (entorno Python roto, no relacionado) |

## Milestones

- **M0: Foundation** — All Infrastructure Tasks (IT-01 through IT-08). Review after completion.
- **M1: Core CRUD** — Properties, Systems, Knowledge Blocks, Relations (UJ-01 through UJ-04). Review after completion.
- **M2: Sync + Automations** — Guesty integration and scheduled sync (UJ-05 through UJ-08). Review after completion.
- **M3: Intelligence** — RAG search, chat, embeddings (UJ-09 through UJ-12). Review after completion.
- **M4: Agent API + Admin** — Tool API, config, users, logs (UJ-13 through UJ-17). Review after completion.
- **M5: Polish** — Dashboard, map, reservations, UI polish, seed data (UJ-18 through UJ-22). Final review before delivery.

## Status Values
- `pending` — not started
- `in_progress` — actively being implemented
- `completed` — finished and verified
- `blocked` — waiting on a dependency or decision
