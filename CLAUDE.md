# CLAUDE.md

## Project overview

ai_flow is an opinionated AI agent workflow system built on Temporal for orchestration and Claude for LLM execution. Tasks are tracked in Linear, AI agents commit state to the repo, and plugins allow agents to check their work.

## Monorepo layout

```
clients/     # Frontend clients (TypeScript, managed by pnpm)
libs/        # Shared Python libraries (uv workspace members)
services/    # Python services (uv workspace members)
infra/       # Terraform stacks managed via Spacelift
docs/        # ADRs, architecture diagrams, feature context
```

- Python packages use `src/` layout (e.g. `libs/ai-flow/src/ai_flow/`)
- Each Python package has its own `pyproject.toml` and `tests/` directory
- The root `pyproject.toml` is the uv workspace root with shared dev dependencies and tool config

## Commands

- `uv sync` — install all dependencies
- `uv run pytest` — run all tests
- `uv run mypy libs/ services/` — type check all Python code
- `uv run ruff check libs/ services/` — lint all Python code
- `uv run ruff format libs/ services/` — format all Python code
- `pre-commit install` — install git hooks (run once after clone)

## Code style

- Python 3.13+, strict mypy (all functions must have type annotations)
- Use dataclass, TypedDict, or Pydantic models — no untyped dicts for structured data
- Line length: 120 characters
- Indent: 4 spaces (Python), 2 spaces (YAML, Terraform)
- Conventional commits required: `<type>(scope): <message>` (see .commitlintrc.json)
- Allowed commit types: feat, fix, docs, style, refactor, perf, test, build, chore, revert

## Architecture decisions

See `docs/adrs/` for accepted ADRs:
- ADR-0001: Durable workflow state with per-ticket phases
- ADR-0002: Temporal for workflow orchestration
- ADR-0003: Repository context structure under `docs/features/<ticket-id>/`
- ADR-0004: Python for backend, TypeScript for frontend, mypy strict mode
