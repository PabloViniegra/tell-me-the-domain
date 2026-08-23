# Evidence Map

Where business meaning hides in a codebase, and how to find it cheaply. Language-agnostic; the patterns below are starting points, not an exhaustive list.

Everything in this file is a search heuristic: a signal promotes a hypothesis, never a fact. Record the behavior you find; label the interpretation as `hypothesis` or `synthesis` until evidence confirms it.

## Contents

1. Data model
2. Invariants and validation
3. Lifecycles and processes
4. Policies, money and calculations
5. Actors and permissions
6. Time, scheduling and deadlines
7. Integrations and external contracts
8. Human language: errors, copy, i18n
9. Tests as specification
10. History and social evidence
11. Interface and user journeys
12. Reference data, seeds and fixtures
13. Database-side logic
14. Outputs and communications
15. Imports, pipelines and reconciliation
16. Audit and compliance
17. Configuration and feature flags
18. Signals that the domain is *not* here

---

## 1. Data model

The highest signal-per-token artifact in almost any repository. Column names are the vocabulary; constraints are rules someone cared enough to enforce at the last possible layer.

Look for: `migrations/`, `schema.sql`, `*.prisma`, `models.py`, `entity/`, `*.proto`, `openapi.yaml`, `*.avsc`, ORM annotations.

Read for:
- Entity names and their relationships (cardinality tells you the shape of the business).
- `NOT NULL`, `UNIQUE`, `CHECK`, foreign keys with `ON DELETE` behaviour — each is a rule.
- Enums and status columns — the lifecycle vocabulary.
- Soft-delete, versioning, `valid_from`/`valid_to` columns — the business needs history, which usually means audit or regulatory pressure.
- Money columns: their type and scale reveal precision rules; a separate currency column means multi-currency is a real requirement.

```
rg -n "CREATE TABLE|ALTER TABLE .* ADD CONSTRAINT|CHECK \("
rg -n "enum |ENUM\(|IntegerChoices|@Enumerated"
```

## 2. Invariants and validation

What the system refuses to allow. Concentrated in constructors, factories, setters, validators and guard clauses at the top of use-case functions.

```
rg -n "if .*(throw|raise|panic|return .*[Ee]rr)" --max-count 3
rg -n "@Valid|@NotNull|@Min|@Max|zod|yup|joi|pydantic|validates?_|Assert\."
rg -n "class .*(Error|Exception)\b|errors\.New\(|fmt\.Errorf\("
```

Custom exception and error names are a compact list of everything the business considers illegal — read the error type declarations before reading the code that raises them.

## 3. Lifecycles and processes

```
rg -n "status|state|phase|stage" --type-add 'schema:*.{sql,prisma,proto}' -t schema
rg -n "transition|canTransition|allowedStates|StateMachine|workflow|saga"
rg -n "class .*(Created|Updated|Approved|Cancelled|Shipped|Completed)\b"
```

Past-tense event names are a narrative of the business process. Order them and you have the happy path; the events with no obvious trigger are usually the interesting edge cases.

Also check for outbox tables, queues, topic names and consumer registrations — asynchronous boundaries usually mark the seam between two parts of the business.

## 4. Policies, money and calculations

```
rg -n "calculate|compute|price|fee|rate|discount|tax|vat|commission|score|quota|limit|threshold"
rg -n "\b0\.[0-9]{2}\b|\b[0-9]{2,}\b" <core-domain-files>
```

Every magic number is a *candidate* business decision — a signal to investigate, not a fact. Record its value, its location, and whether it is configurable; then classify it (domain rule, application constraint, technical detail, unknown) before promoting it to the rules table. A hardcoded rate that turns out to be a domain rule is an operational risk and belongs in the technical document's risk section.

Rounding mode, precision, and whether money is stored as integer minor units are business rules with legal consequences in some industries. Note them.

## 5. Actors and permissions

```
rg -n "role|permission|scope|can[A-Z]|authorize|policy|tenant|organization_id"
```

The set of roles is the cast of characters. Tenant or organization scoping in queries tells you the product is multi-tenant, which changes almost every rule downstream. Row-level filters describe visibility rules that no one writes down elsewhere.

## 6. Time, scheduling and deadlines

```
rg -n "cron|schedule|@Scheduled|celery|sidekiq|rrule|business_day|holiday|timezone|SLA|expires?_at|due_date"
```

Scheduled jobs are recurring business obligations: invoicing cycles, reminder windows, retention purges, reconciliation runs. Business-day and holiday calendars indicate a regulated or contractual domain. Retention deletions may signal a legal requirement — record the behavior as observed and the legal reading as a hypothesis, never merged into one claim.

## 7. Integrations and external contracts

Look at dependencies, HTTP clients, SDK usage, webhook handlers, and adapter or gateway folders. Each external system is a business relationship: a payment processor, a carrier, a credit bureau, a government filing endpoint.

Webhook handlers are particularly informative — they list the events the outside world can impose on this business, which no internal code reveals.

## 8. Human language: errors, copy, i18n

```
rg -n "" locales/ i18n/ translations/ --files
rg -n "message|error_message|description" <catalog files>
```

Someone already translated the rules into plain language for end users. This is the cheapest bridge between code and `USER_BUSINESS.md`, and often the only place the *why* is stated.

## 9. Tests as specification

Domain test files under names like `*_test.*`, `*.spec.*`, `test_*.py`, `features/*.feature`.

Read the *names* first — `it("rejects a refund after 30 days")` is a requirement. BDD feature files, when present, are business documentation that happens to execute. Fixtures and factories reveal what a realistic entity looks like, including which fields are truly mandatory in practice — see § 12 before deciding whether to read them.

## 10. History and social evidence

- `git log -S"<term>"` to find when a rule was introduced.
- Commit messages and PR references often carry the ticket ID and the rationale.
- ADRs (`docs/adr/`, `docs/decisions/`) are the only artifact designed to record *why*.
- Long-lived TODO/FIXME comments near domain rules usually mark known business debt.

## 11. Interface and user journeys

Screens, forms, and navigation reveal operations that have no dedicated endpoint: bulk actions, wizards, draft states, UI-only validations, field visibility rules.

Look for: route/page components, form schemas, menu definitions, permission-gated buttons, frontend validation schemas that duplicate backend rules.

A rule enforced only in the UI is a finding: it describes intent, not protection. Record where each rule is enforced (edge / application / domain / db) — that axis is what the technical guide's invariant table uses.

## 12. Reference data, seeds and fixtures

Do not bulk-read these, but never skip them blindly either. When the coverage inventory marks them as contract, reference data, or the only statement of a rule, inspect them:

- `seeds/`, `fixtures/`, `data/`, `*.csv`, tariff tables, country/currency lists, reason-code catalogues.
- Golden files under `tests/fixtures/` often encode the expected output of a calculation more precisely than the code that produces it.
- A fee schedule or eligibility matrix that only exists as a JSON fixture *is* the domain rule; its location does not make it less real.

## 13. Database-side logic

In legacy systems the domain often lives inside the database itself.

```
rg -n "CREATE (OR REPLACE )?(TRIGGER|FUNCTION|PROCEDURE)|CREATE VIEW" -i
rg -n "ROW LEVEL SECURITY|POLICY ON|GENERATED ALWAYS" -i
```

Triggers, stored procedures, views, row-level security, and generated columns are business rules with the worst discoverability of any layer. If they exist, they are core — not an implementation detail.

## 14. Outputs and communications

The artifacts the business produces for the outside world: report generators, PDF/Excel exports, email and notification templates, invoice renderers, document templates.

```
rg -n "render|template|pdf|xlsx|csv|mail|notification" --files-with-matches
```

These answer "what does the actor actually receive" — often the only place the business outcome is stated in full sentences.

## 15. Imports, pipelines and reconciliation

Business data that enters outside the APIs: ETL jobs, bulk loaders, file imports (CSV/SFTP/EDI), synchronization with external systems, reconciliation reports.

```
rg -n "import|etl|sync|reconcil|bulk|load" -i --files-with-matches
```

Reconciliation code is especially valuable: it exists where two systems can disagree, which tells you exactly which facts the business does not fully control.

## 16. Audit and compliance

Audit-log writers, consent records, legal holds, retention policies, access logs, soft-delete with history. In regulated domains these are not cross-cutting infrastructure — they are the product. Record what is captured, when, and what query surface exposes it.

## 17. Configuration and feature flags

```
rg -n "feature.?flag|isEnabled|variant|rollout|plan|tier|region" -i
```

Flags, plans, regions, and tenant overrides are behavioral branches the runtime takes. Code guarded by a disabled flag is present but not active — record it with `runtime_status: config-dependent` or `inactive`, never as observed current behavior. The same binary can run several different businesses.

## 18. Signals that the domain is *not* here

Do not spend tokens on: dependency lockfiles, generated clients and stubs, migrations that only add indexes, CI configuration, linter and formatter config, boilerplate CRUD controllers that just forward to a service, DTO mappers, snapshot files, vendored code.

If a whole repository looks like this, the domain may live elsewhere — in a sibling service, a stored-procedure layer, a BPM engine, a rules engine configuration, or a spreadsheet someone maintains. State that the repository does not establish the domain and record the evidence; do not invent a domain or ask the user to reconcile code inconsistencies.
