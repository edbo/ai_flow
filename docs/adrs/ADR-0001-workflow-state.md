# ADR 0001: Durable Workflow State for AI Agent System

## Status

Accepted

## Date

2026-03-22

---

## Context

We are building an AI-assisted development workflow where an LLM (Claude) participates in:

- Planning work from Linear tickets
- Generating test-first pull requests
- Iteratively implementing features
- Responding to human feedback

The workflow spans multiple steps, approvals, and execution environments, including:

- GitHub Actions (ephemeral)
- External user input (GitHub, Slack)
- Long-running processes (multi-step implementation)

Key requirements:

- Workflow state must persist across executions
- The system must support long-running processes
- Human interaction must be possible at any step
- The system must be resumable after interruptions or failures
- State transitions must be deterministic and inspectable

Constraints:

- LLM APIs are stateless (no native conversation continuation)
- CI environments do not maintain state between runs
- Token limits prevent storing full conversation history

---

## Decision

We will introduce a **durable workflow state management layer** responsible for:

- Persisting workflow state across executions
- Coordinating multi-step processes
- Handling retries and failures
- Supporting external signals (e.g. approvals, revisions)
- Providing a single source of truth for workflow progression

This layer will sit between:

- External systems (GitHub, Slack, Linear)
- Execution logic (LLM calls, CI jobs)

---

## Architecture Overview

### Responsibilities of Workflow State Layer

- Maintain state per ticket / work item
- Track workflow phase and transitions
- Accept external input (signals/events)
- Resume execution after interruption
- Ensure deterministic progression

---

## Interaction Model

User interactions (via GitHub or Slack) will be translated into **state transitions**, rather than treated as a continuous chat.

Example:

```
@agent approve plan
@agent revise plan to exclude billing
@agent proceed with implementation
```

These commands trigger transitions in the workflow state.

---

## State Model

Each unit of work (e.g. Linear ticket) maintains structured state:

```ts
type Phase =
  | "backlog" # Do nothing
  | "planning" # AI Improve Task Definition and Plan
  | "plan_approval" # Human Approval of Task Definition and Implementation Plan
  | "test_planning" # AI Write verification/test plan
  | "test_plan_approval" # Human Approval of test plan
  | "test_implementation" # AI Test Implementation
  | "test_approval" # Human Approval of tests
  | "implementation" # AI Implement Code and Run Tests
  | "implementation_approval" # Human Approval of implementation
  | "completed"; # Done

interface AgentState {
  phase: Phase;
  plan: string;
  summary: string;
}
```

---

## Repository Context

Human-readable context is stored in the repository:

```
docs/features/<ticket-id>-<slug>/
  plan.md
  summary.md
  handoff.md
  state.json
```

This ensures:

- Local development is possible without external systems
- Context is visible during PR review
- Humans can take over at any time

---

## Design Principles

### 1. Deterministic Execution

Workflows must progress based on explicit state, not hidden model memory.

### 2. Separation of Concerns

- Workflow state layer = orchestration
- Repository = human-readable context
- LLM = stateless execution

### 3. Human Override

Humans must be able to intervene at any step.

### 4. Portability

All essential context must be accessible from the repository.

---

## Alternatives Considered

### Stateless CI-only approach

Rejected:

- No persistence across runs
- Cannot support approvals or long-running workflows

### Storing full chat history

Rejected:

- Token inefficiency
- Poor debuggability
- Non-deterministic behaviour

---

## Consequences

### Positive

- Enables complex multi-step workflows
- Supports human-in-the-loop interaction
- Improves reliability and resumability
- Decouples orchestration from execution

### Negative

- Introduces additional system complexity
- Requires careful state design

---

## Summary

We introduce a **durable workflow state layer** to manage AI-driven development workflows.

This enables:

- persistent, resumable processes
- structured state transitions
- reliable human interaction

The specific technology used to implement this layer is defined in a subsequent ADR.

---

**End of ADR**
