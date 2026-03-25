# ADR 0002: Selection of Temporal for Workflow State Management

## Status
Accepted

## Date
2026-03-22

---

## Context

ADR-0001 defines the need for a **durable workflow state management layer** to support:

- Long-running workflows
- Human-in-the-loop approvals
- Deterministic state transitions
- Resumability across failures and restarts

We evaluated several approaches to implementing this layer.

---

## Decision

We will use Temporal as the workflow orchestration engine and source of truth for workflow state.

---

## Why Temporal

Temporal provides:

### 1. Durable Execution

- Workflows persist state automatically
- Execution resumes seamlessly after failures
- No need to manually manage checkpoints

---

### 2. Native Support for Long-Running Workflows

- Workflows can run for days or weeks
- No reliance on external schedulers or polling systems

---

### 3. Signals for External Input

- External systems (GitHub, Linear, Slack) can send signals
- Signals map cleanly to user commands and approvals
- Webhooks from external services are received via AWS Lambda functions behind an API Gateway, which forward them as Temporal signals

**Webhook Ingestion Architecture:**

```
GitHub/Linear webhook → API Gateway → Lambda → Temporal Signal
```

- AWS API Gateway provides the HTTP endpoints for receiving webhooks
- Individual Lambda functions parse and validate incoming payloads per source (e.g. GitHub, Linear)
- Lambdas forward validated events as signals to the appropriate Temporal workflow
- This decouples external event ingestion from workflow execution
- Lambdas are stateless and scale independently of the Temporal worker fleet

Example signal handler:

```ts
workflow.setHandler("user_command", (cmd) => {
  if (cmd.type === "approve_plan") {
    state.phase = "tests";
  }
});
```

---

### 4. Deterministic State Transitions

- Workflow logic is defined in code
- Replay guarantees deterministic behaviour
- Eliminates hidden or implicit state

---

### 5. Built-in Retries and Fault Tolerance

- Automatic retry policies
- Resilient to infrastructure failures
- Simplifies error handling

---

### 6. Event History

- Full history of workflow execution is retained
- Enables debugging and observability

---

## Alternatives Considered

### 1. Database (e.g. Supabase/Postgres)

Pros:
- Simple to set up
- Easy to query

Cons:
- Requires manual state management
- No built-in orchestration
- Complex retry and failure handling
- Hard to model long-running workflows

---

### 2. Queue + Workers (e.g. SQS + Lambdas)

Pros:
- Scalable
- Familiar pattern

Cons:
- Requires custom orchestration logic
- No built-in state model
- Difficult to handle multi-step workflows

---

### 3. GitHub Actions Only

Pros:
- Already integrated with code

Cons:
- Ephemeral execution
- No persistence between runs
- Not suitable for long-running workflows

---

## Consequences

### Positive

- Strong guarantees around execution and state
- Clean mapping between user actions and workflow signals
- Reduced need for custom orchestration code
- Improved reliability and debuggability
- API Gateway + Lambda provides a scalable, low-maintenance ingestion layer for external webhooks
- Webhook processing is decoupled from workflow execution — failures in ingestion do not affect running workflows

---

### Negative

- Additional infrastructure and operational overhead
- Learning curve for workflow design and determinism constraints
- Limited ad-hoc querying compared to traditional databases
- API Gateway + Lambda adds AWS infrastructure that must be provisioned and monitored

---

## Mitigations

- Use repository `docs/` files for human-readable state
- Optionally introduce a read-model database later for querying
- Keep workflows simple and well-scoped per ticket
- Use Infrastructure as Code (Terraform) to manage API Gateway and Lambda resources
- Implement dead-letter queues on Lambdas for failed webhook deliveries

---

## Summary

Temporal provides a robust, deterministic, and scalable foundation for managing AI-driven development workflows.

It replaces the need for custom orchestration logic and enables:

- durable execution
- clean state transitions
- reliable human interaction

---

**End of ADR**
