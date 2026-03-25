# ADR 0003: Repository Context Structure for AI Agent Workflows

## Status
Accepted

## Date
2026-03-22

---

## Context

AI agent workflows require context that is:

- Human-readable
- Version-controlled
- Available locally when checking out a branch
- Usable as input for LLM prompts

Relying solely on external systems (e.g. workflow engines) makes it difficult for developers to:

- Understand current progress
- Take over work manually
- Review intent during pull requests

---

## Decision

We will store workflow context in the repository under the `docs/` directory.

Context will be organised by work type, with features as the primary unit.

---

## Structure

### Features

```
docs/features/<ticket-id>-<slug>/
  plan.md
  summary.md
  handoff.md
  state.json
```

Example:

```
docs/features/LIN-123-invoice-retry/
```

### Other Work Types

```
docs/
  bugs/
  chores/
  spikes/
```

Each follows the same internal structure.

---

## File Definitions

### plan.md

Defines the approved implementation plan:

- Goals
- Scope
- Constraints
- Non-goals

---

### summary.md

Tracks progress and decisions:

- Current status
- Key findings
- Next steps

---

### handoff.md

Provides guidance for human takeover:

- What has been completed
- What remains
- Known issues or risks

---

### state.json

Machine-readable snapshot of workflow state:

```json
{
  "ticket": "LIN-123",
  "phase": "tests_open",
  "plan_version": 2,
  "last_updated_by": "agent",
  "next_action": "awaiting_review"
}
```

---

## Responsibilities

### Repository

- Source of truth for human-readable context
- Enables local development and debugging
- Provides visibility during code review

---

### Workflow Engine (Temporal)

- Source of truth for execution state
- Drives transitions and orchestration

---

## Design Principles

### 1. Human-First Visibility

All important context must be readable in the repository without external tools.

---

### 2. Portability

Developers must be able to:

- Check out a branch
- Read `docs/features/...`
- Continue work immediately

---

### 3. Structured + Unstructured Hybrid

- Markdown files for humans
- JSON for machines

---

### 4. Incremental Updates

Files are updated as the workflow progresses:

- Planning → update `plan.md`
- Execution → update `summary.md`
- Handoff → update `handoff.md`
- State changes → update `state.json`

---

## Alternatives Considered

### External-only storage (e.g. database)

Rejected:
- Poor developer experience
- No visibility in PRs
- Difficult manual takeover

---

### Full chat transcript storage

Rejected:
- Noisy and hard to parse
- Inefficient for LLM context
- Not suitable for structured workflows

---

## Consequences

### Positive

- Improves developer experience
- Enables seamless human takeover
- Provides clear audit trail in version control
- Aligns with existing Git workflows

---

### Negative

- Requires discipline in maintaining files
- Potential duplication with workflow engine state

---

## Summary

We use the repository as the **human-facing context layer** for AI workflows.

Combined with a workflow engine, this enables:

- clarity
- portability
- collaboration

---

**End of ADR**
