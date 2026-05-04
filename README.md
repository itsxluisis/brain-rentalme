# FactorIA-APP-TEMPLATE

Reusable engineering base for AI-assisted software development. Duplicate this repository for each new project.

## How to Use

1. Duplicate this repository as a new private repository
2. Edit `START_PROJECT_PROMPT.md` with your project description
3. Open the repository in Claude Code
4. Run `/init-project` to begin Planning Mode

## What This Template Provides

- Governance file (`CLAUDE.md`) loaded automatically by Claude Code
- Planning, design, and implementation folder structure
- Five enforcement commands: `init-project`, `start-execution`, `session-start`, `review`, `iterate`
- Persistent project memory via markdown files
- Docker and EasyPanel deployment structure

## Commands

| Command | Purpose |
|---------|---------|
| `/init-project` | Start Planning Mode for a new project |
| `/start-execution` | Begin Autonomous Execution after plan approval |
| `/session-start` | Resume work at the start of each session |
| `/review` | Run independent review after each milestone |
| `/iterate` | Apply changes after delivery |

## Repository Structure

```
planning/       — requirements, scope, questions, risks
design/         — architecture, data model, API contracts, wireframes
implementation/ — task tracker, user journeys
docs/           — project memory, work log, decisions, NFR
deployment/     — Docker, EasyPanel, deployment guide
skills/         — skill registry
mcps/           — MCP and API registry
backend/        — backend application (populated per project)
frontend/       — frontend application (populated per project)
tests/          — automated tests (populated per project)
.claude/        — commands and settings
```
