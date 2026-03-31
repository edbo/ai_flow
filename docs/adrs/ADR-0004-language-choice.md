# ADR 0004: Language Choice for Workflow and Backend Code

## Status

Accepted

## Date

2026-03-31

---

## Context

ADR-0001 through ADR-0003 establish the need for a durable workflow system built on Temporal, with webhook ingestion via AWS Lambda, and repository-based context management.

We need to select a primary language for:

- Temporal workflows and activities
- Lambda webhook handlers
- CLI tooling and utilities
- Repository context manipulation (read/write `state.json`, markdown files)

TypeScript is already selected for frontend work. This ADR concerns the **backend and workflow code** specifically.

### Requirements

The language must support:

1. **Temporal SDK** — First-class workflow and activity authoring
2. **AWS Lambda** — Efficient cold starts and runtime support
3. **Anthropic Claude SDK** — Native client for LLM integration
4. **Testability** — Strong TDD support with fast test feedback loops
5. **Team familiarity** — Reasonable learning curve for the team
6. **Ecosystem maturity** — Stable libraries for GitHub, Linear, and Slack integrations

---

## Candidates

### 1. Go

#### Temporal Support

Go is a **first-class Temporal citizen**. The Go SDK was the first Temporal SDK and remains the reference implementation. It has the most complete feature coverage, the best documentation, and the largest body of production examples. Temporal's own server is written in Go.

- Deterministic workflow replay: fully supported
- Testing: `testsuite.WorkflowTestSuite` provides an in-memory test environment
- Signal and query handling: idiomatic and well-documented
- Worker performance: excellent — low memory footprint, high throughput

#### AWS Lambda

- Compiles to a single static binary — no runtime dependencies
- Cold start times: ~10-50ms (among the fastest of any Lambda runtime)
- Small deployment artifacts (~5-15MB zipped)
- Native `provided.al2023` runtime support

#### Claude SDK

- Official Anthropic Go SDK available (`github.com/anthropics/anthropic-sdk-go`)
- Actively maintained with full API coverage

#### Testability

- Built-in `testing` package, no framework needed
- Fast compilation and test execution
- Table-driven tests are idiomatic and reduce boilerplate
- Race detector (`-race`) catches concurrency issues at test time
- Mocking requires interfaces or code generation (e.g. `mockgen`)

#### Strengths

- Strongest Temporal integration of any language
- Best Lambda cold-start performance
- Static typing catches errors at compile time
- Single binary deployment simplifies operations
- Excellent concurrency primitives (goroutines, channels)
- Strong standard library reduces external dependencies

#### Weaknesses

- Verbose error handling (`if err != nil` pattern)
- No generics until recently — some patterns still feel clunky
- Steeper learning curve if team is unfamiliar
- Less expressive for rapid prototyping compared to dynamic languages
- Mocking is more ceremony than in dynamic languages

---

### 2. Python

#### Temporal Support

Python has an **official Temporal SDK** (`temporalio`). It uses a Rust-based core for deterministic replay, with a Python-native authoring experience. It is well-maintained but younger than the Go SDK.

- Deterministic workflow replay: supported via Rust core (sandbox mode)
- Testing: `WorkflowEnvironment` provides time-skipping test support
- Signal and query handling: supported via decorators
- Worker performance: adequate for moderate throughput; Rust core handles the heavy lifting

#### AWS Lambda

- Supported via `python3.12` managed runtime
- Cold start times: ~100-300ms (moderate)
- Larger deployment packages if dependencies are heavy (Temporal SDK pulls in Rust binaries)
- Lambda Layers or container images may be needed for complex dependencies

#### Claude SDK

- Official Anthropic Python SDK (`anthropic`) — the **most mature and feature-complete** client
- First SDK to receive new features; best documented
- Async support via `anthropic.AsyncAnthropic`

#### Testability

- `pytest` is excellent — fixtures, parametrize, and plugins make TDD ergonomic
- Fast feedback loops for unit tests
- Mocking is trivial (`unittest.mock`, `pytest-mock`)
- Type checking via `mypy` or `pyright` is optional but increasingly standard

#### Strengths

- Most mature Claude/Anthropic SDK — first to get new features
- Fastest prototyping speed — minimal boilerplate
- Rich ecosystem for data manipulation and scripting
- `pytest` is one of the best testing frameworks in any language
- Largest pool of developers familiar with the language
- Excellent for LLM prompt engineering and experimentation

#### Weaknesses

- Dynamic typing means more runtime errors (mitigated by type hints + mypy)
- Lambda cold starts are slower than Go
- Dependency management can be painful (though `uv` and `poetry` help)
- Temporal Python SDK is less battle-tested than Go
- GIL limits true parallelism (less relevant for I/O-bound workflow code)
- Packaging for Lambda with native dependencies requires extra tooling

---

### 3. Ruby

#### Temporal Support

Ruby has a **community-maintained Temporal SDK** (`temporalio-ruby`). It is the least mature of the three options. The Temporal team has signalled interest but Ruby is not a priority language.

- Deterministic workflow replay: supported but less battle-tested
- Testing: basic test support; less documented than Go or Python
- Signal and query handling: supported
- Worker performance: adequate for low-to-moderate throughput
- Community: smallest Temporal community of the three candidates

#### AWS Lambda

- Supported via `ruby3.3` managed runtime
- Cold start times: ~150-400ms (moderate to slow)
- Deployment packaging is straightforward with Bundler
- Smaller ecosystem of Lambda-specific tooling compared to Python or Go

#### Claude SDK

- Official Anthropic Ruby SDK (`anthropic-sdk-ruby`) available
- Maintained but receives updates after Python and TypeScript SDKs
- Adequate API coverage

#### Testability

- `rspec` is an excellent, expressive testing framework
- Very fast feedback loops for unit tests
- Mocking and stubbing are first-class in RSpec
- Strong TDD culture in the Ruby community

#### Strengths

- Highly expressive and readable syntax
- Strong TDD culture — RSpec is arguably the gold standard for BDD
- Excellent for DSL creation (relevant for workflow definitions)
- Rails ecosystem if web components are ever needed
- Pleasant developer experience for small-to-medium codebases

#### Weaknesses

- **Least mature Temporal SDK** — community-maintained, not official
- Smallest Temporal community and fewest production references
- Slower Lambda cold starts than Go
- Smaller ecosystem for cloud-native tooling compared to Go or Python
- Performance is the weakest of the three for compute-bound work
- Fewer developers with combined Ruby + Temporal experience

---

## Comparison Matrix

| Criterion                  | Go         | Python     | Ruby       |
|----------------------------|------------|------------|------------|
| Temporal SDK maturity      | Excellent  | Good       | Fair       |
| Lambda cold-start          | Excellent  | Moderate   | Moderate   |
| Claude SDK maturity        | Good       | Excellent  | Good       |
| TDD ergonomics             | Good       | Excellent  | Excellent  |
| Prototyping speed          | Moderate   | Excellent  | Excellent  |
| Type safety                | Excellent  | Good (with strict mypy) | Weak  |
| Operational simplicity     | Excellent  | Moderate   | Moderate   |
| Ecosystem (cloud-native)   | Excellent  | Excellent  | Moderate   |
| Team learning curve        | Moderate   | Low        | Low        |
| Concurrency model          | Excellent  | Moderate   | Moderate   |

---

## Analysis

### If Temporal integration is the top priority → Go

Go is the reference language for Temporal. Choosing Go minimises risk around workflow correctness, SDK coverage, and production debugging. The operational story (single binary, fast cold starts) is also the cleanest. The trade-off is slower iteration speed during early development and more verbose code.

### If rapid prototyping and LLM integration are the top priority → Python

Python offers the fastest path to a working prototype. The Claude SDK is the most mature, `pytest` makes TDD ergonomic, and the language excels at the kind of string manipulation and data wrangling that LLM integration involves. The trade-off is weaker operational characteristics (cold starts, packaging complexity) and a younger Temporal SDK.

### If developer happiness and TDD culture are the top priority → Ruby

Ruby's expressiveness and RSpec make for a pleasant TDD workflow. However, the immature Temporal SDK is a significant risk for a system where Temporal is the central orchestration layer (per ADR-0002). This risk outweighs the developer experience benefits.

---

## Decision

We will use **Python** as the primary language for workflow and backend code, with **TypeScript** for frontend work.

The deciding factors are:

1. **Prototyping speed** — Python enables the fastest path to a working system, which is critical in the early phase where we are iterating on workflow design and LLM integration patterns.
2. **Claude SDK maturity** — The Anthropic Python SDK is the most feature-complete and first to receive new capabilities. Given that Claude integration is central to the system, this reduces friction and risk.
3. **TDD ergonomics** — `pytest` provides an excellent test-first development experience with minimal boilerplate.

### Mitigating Python's weaknesses

#### Type safety

We will enforce **strict type hinting** from the outset to mitigate Python's dynamic typing risks:

- All function signatures must include full type annotations (parameters and return types)
- All data structures must use `dataclass`, `TypedDict`, or Pydantic models — no untyped dicts for domain objects
- `mypy` (or `pyright`) in strict mode will run as part of CI and pre-commit checks
- `--strict` flag equivalent settings: `disallow_untyped_defs`, `disallow_any_generics`, `warn_return_any`, `no_implicit_optional`
- New code that fails type checking must not be merged

This gives us compile-time-like safety while retaining Python's prototyping speed.

#### Lambda cold starts

- Use `uv` for fast, reproducible dependency management and packaging
- Keep Lambda deployment packages lean by separating heavy dependencies (Temporal SDK) from lightweight webhook handlers
- Consider Lambda SnapStart or provisioned concurrency if cold starts become problematic

#### Temporal SDK maturity

- The Python SDK is official and actively maintained, with a Rust core for deterministic replay
- Pin SDK versions and monitor the Temporal Python SDK changelog for breaking changes
- Keep workflow logic simple and well-tested to reduce exposure to SDK edge cases

---

## Consequences

### Positive

- Fastest iteration speed during early development
- Best-in-class Claude/Anthropic SDK integration
- Strong TDD workflow with `pytest`
- Strict type hinting provides guardrails without sacrificing expressiveness
- Large talent pool and ecosystem for future contributors

### Negative

- Lambda cold starts are slower than Go (~100-300ms vs ~10-50ms) — acceptable for webhook handlers that are not latency-critical
- Dependency packaging for Lambda requires more tooling than Go's single-binary model
- Temporal Python SDK is less battle-tested than Go — mitigated by keeping workflow logic simple and well-tested
- Strict type hinting adds some overhead to development — accepted as a worthwhile trade-off for correctness

---

**End of ADR**
