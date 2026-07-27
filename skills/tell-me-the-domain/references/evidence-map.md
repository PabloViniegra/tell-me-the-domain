# Evidence Map

Where business meaning hides in a codebase, and how to find it cheaply. Language-agnostic; the patterns below are starting points, not an exhaustive list.

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
11. Signals that the domain is *not* here

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

Every magic number is a business decision. Record its value, its location, and whether it is configurable — a hardcoded rate is an operational risk and belongs in the technical document's risk section.

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

Scheduled jobs are recurring business obligations: invoicing cycles, reminder windows, retention purges, reconciliation runs. Business-day and holiday calendars indicate a regulated or contractual domain. Retention deletions usually imply a legal requirement — flag them.

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

Read the *names* first — `it("rejects a refund after 30 days")` is a requirement. Fixtures and factories reveal what a realistic entity looks like, including which fields are truly mandatory in practice. BDD feature files, when present, are business documentation that happens to execute.

## 10. History and social evidence

- `git log -S"<term>"` to find when a rule was introduced.
- Commit messages and PR references often carry the ticket ID and the rationale.
- ADRs (`docs/adr/`, `docs/decisions/`) are the only artifact designed to record *why*.
- Long-lived TODO/FIXME comments near domain rules usually mark known business debt.

## 11. Signals that the domain is *not* here

Do not spend tokens on: dependency lockfiles, generated clients and stubs, migrations that only add indexes, CI configuration, linter and formatter config, boilerplate CRUD controllers that just forward to a service, DTO mappers, snapshot files, vendored code.

If a whole repository looks like this, the domain may live elsewhere — in a sibling service, a stored-procedure layer, a BPM engine, a rules engine configuration, or a spreadsheet someone maintains. Say so in the open questions rather than inventing a domain that is not there.
