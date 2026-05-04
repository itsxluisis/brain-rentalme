# Stack Selection

Technology choices with rationale. Defined during planning, referenced thereafter.

## Selected Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Backend | [e.g., Node.js + Fastify] | | |
| Frontend | [e.g., React + Vite] | | |
| Database | [e.g., PostgreSQL] | | |
| ORM | [e.g., Prisma] | | |
| Auth | JWT + bcrypt | | Application-managed, no external auth SaaS |
| AI | OpenAI SDK | | Provider-abstracted, switchable |
| CSS | [e.g., Tailwind CSS] | | |
| State | [e.g., Zustand / React Query] | | |
| Testing | [e.g., Vitest + Supertest] | | |

(Populated during planning)

## Rejected Alternatives

| Technology | Rejected For | Reason |
|-----------|-------------|--------|
| | | |

## Stack Constraints

- Must be deployable via Docker
- Must work with EasyPanel from GitHub
- No external auth SaaS (Auth0, Clerk, etc.) unless explicitly requested
- No external state management SaaS unless explicitly requested
