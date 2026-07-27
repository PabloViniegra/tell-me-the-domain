# [Product name] — Technical domain guide

> Reconstructed from the codebase at [commit / date]. This guide describes observed behavior only.
> References point to `path/to/file.ext:line` as of that revision. Do not infer expected behavior or propose corrections. Record inconsistencies, contradictions, and ambiguities as observations with their evidence.

## Orientation

[Two or three sentences: what the system does, what shape it is (single service, monorepo, modular monolith), and where the business logic actually lives versus where it merely passes through.]

**Discovery boundary:** [Contexts and deployables analyzed.] **Sampled or excluded:** [Areas intentionally not read and why.] **Confidence limits:** [Missing tools, unavailable contracts, conflicting evidence, or recommended next context.]

**Read these first:** `path/a.ext`, `path/b.ext`, `path/c.ext` — the three files that explain the most about the domain.

## Domain map

| Bounded context / module | Path | Owns | Depends on |
|---|---|---|---|
| [Name] | `src/...` | [Concepts it is authoritative for] | [Other contexts] |

```mermaid
graph TD
    A[Context A] --> B[Context B]
    B --> C[(Shared data)]
```

[Where the boundaries are clean and where they leak. Describe leaks as observed relationships or conflicting behavior, with evidence; do not infer which boundary is correct.]

## Model

```mermaid
erDiagram
    ENTITY_A ||--o{ ENTITY_B : "relationship"
```

| Entity | Defined at | Identity | Notes |
|---|---|---|---|
| [Name] | `path:line` | [Natural or surrogate key] | [Aggregate root, value object, lifecycle owner] |

## Lifecycles

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Active: [trigger]
    Active --> Closed: [trigger]
```

| Transition | Enforced at | Guard | On violation |
|---|---|---|---|
| Draft → Active | `path:line` | [Condition] | [Error raised / behaviour] |

Transitions that are deliberately absent: [list them — knowing what is impossible is as useful as knowing what is possible].

## Invariants and business rules

Grouped by concept. Each rule states what it enforces, where it is enforced, and what happens when it is violated. Note where the same rule is enforced in more than one layer, and where it is enforced in none.

### [Concept]

| Rule | Evidence | Failure mode | Rationale |
|---|---|---|---|
| [What must hold] | `path:line` | [Exception, HTTP status, silent fallback] | [Documented rationale / not stated in repository] |

## Policies, constants and calculations

| What | Value | Location | Configurable |
|---|---|---|---|
| [Threshold, rate, window] | [Value] | `path:line` | [Yes / hardcoded] |

[Calculation logic worth understanding before touching it: rounding, precision, ordering of operations, currency handling. Describe what is implemented, including divergent implementations, without selecting an intended one.]

## Permissions and visibility

| Actor | Can | Enforced at |
|---|---|---|
| [Role] | [Operations] | `path:line` |

[Tenant or organization scoping: how it is applied, and where it could be forgotten.]

## Time-driven behaviour

| Job / trigger | Schedule | Business effect | Location |
|---|---|---|---|
| [Name] | [Cron or event] | [What changes in the business] | `path:line` |

## External contracts

| System | Direction | Purpose | Adapter |
|---|---|---|---|
| [Name] | inbound / outbound | [Business role] | `path:line` |

[What breaks in business terms when each one is unavailable.]

## Where the value lives, technically

[The modules that carry the differentiating logic, and why. This is where reviews should be strictest and test coverage highest.]

## Risks and observations

Things a newcomer should know before their first change. Facts and their direct consequences, not opinions about style or guesses about intended behavior. Include duplicated rules, conflicting implementations, naming mismatches, dead branches, and behavior enforced only in one layer.

- **[Observation]** — `path:line`. [Why it is a risk: duplicated rule, rule enforced only in the interface, unbounded query, business logic in a migration, dead branch, etc.]

## Glossary (code ↔ business)

| Code term | Business term | Defined at | Note |
|---|---|---|---|
| `[Identifier]` | [Business word] | `path:line` | [Synonym, homonym, or legacy naming] |

## Information absent from the repository

List only facts that cannot be established from the repository, such as invisible external contracts or undocumented rationale. Do not ask a human to resolve an observed inconsistency; record the competing behaviors in the relevant sections above.

1. **[Missing fact]** — [Evidence showing that the repository does not establish it: `path:line`.]
