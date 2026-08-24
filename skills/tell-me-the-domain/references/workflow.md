# Workflow

Phases in order. Each ends with a clear handoff to the next. The ledger format used throughout is defined in `references/evidence-ledger.md`.

## Phase 0 — Frame the search

Before reading anything, establish:

- **Output language.** Ask the user upfront which language they want the output documents written in. If the answer is empty, gibberish, or an unrecognizable language name, fall back to English. If the user picks anything other than English, surface this disclaimer and proceed — do not wait for a second confirmation:
  > Non-English output uses more tokens per word than English on most tokenizers (Latin-script languages ~1.5–2x; non-Latin scripts such as Chinese, Japanese, Korean, or Arabic 2–4x). The exploration phase is unchanged; only the document-writing phase pays the extra cost.
  Form-filling vocabulary (Mermaid labels, status enums, code identifiers, proper nouns) stays in the source language of the codebase regardless.
- **Analysis mode.** Two modes, stated in every deliverable:
  - **Complete context mode** — the default for a single service or a user-scoped area ("just the billing service"). Within the declared boundary, the coverage inventory must close fully before writing: every surface ends `complete`, `not-found-after-search`, or `not-applicable`.
  - **Repository atlas mode** — for whole-repo requests over large, legacy, or multi-context codebases. Produces a structural map of everything, full analysis of the prioritized contexts, and an explicit coverage matrix. It never claims the whole business is covered.
  Decide from the user's scope and the repo shape seen in Phase 1. When the scope cannot support complete mode, run atlas mode and say so.
- The repository root and whether this is a monorepo (several deployables) or a single service.
- Whether the user wants the whole repo or one bounded area.
- Anything they already know: the industry, the customer, the vocabulary. One sentence of context saves a lot of guessing.
- A discovery budget. In complete context mode the budget shapes reading order, never closure. In atlas mode it decides how many contexts get full analysis.

If the scope is ambiguous and the answer cannot be determined from the repository, ask one question only when proceeding would make the documents misleading. Do not ask about incoherencies, contradictions, naming mismatches, or behavior that appears unexpected: record the observed variants and their evidence, then continue.

Create the scratch ledger at `.tell-me-the-domain/notes.md` and begin.

## Phase 1 — Cheap recon

Build a map before opening any implementation file. All of this is high signal per token:

1. **Project map and dependency overview.** If structural-analysis tools are available (knowledge-graph builders, AST-based explorers), use them first. What calls what and what depends on what arrive as a compact graph instead of a flood of file reads. If absent, fall back to the items below.
2. **Directory shape**, two or three levels deep, excluding `node_modules`, `vendor`, `dist`, `target`, `.git`. Domain-oriented folder names (`orders/`, `underwriting/`, `payroll/`) are a gift; layer-oriented names (`controllers/`, `services/`) mean the domain hides one level down, inside file names.
3. **README, docs folder, ADRs, CHANGELOG.** Often the only place the *why* survives. Skim, do not read line by line. Record their claims as `documented`, never as `observed`.
4. **Manifests** (`package.json`, `go.mod`, `pyproject.toml`, `pom.xml`, `*.csproj`, `Gemfile`). Dependencies hint at the problem space — a payments SDK, a tax engine, a scheduling library. A hint promotes a hypothesis; it is not evidence of behavior.
5. **Data model.** Migrations, schema files, ORM entities, `.proto`, OpenAPI specs. Tables, columns and enums are the vocabulary of the business, and `NOT NULL`, `UNIQUE`, `CHECK` and foreign keys are business rules that someone bothered to enforce at the last line of defence.
6. **Entry points and routes.** The public API surface tells you which operations the outside world is allowed to perform. Also enumerate the non-HTTP entry points: CLI commands, admin panels, job registrations, queue consumers, webhook handlers.

Record in the ledger: candidate bounded contexts, the entity vocabulary, and the first draft of the coverage inventory. Rank the candidates; you will not read all of them in full.

**Empty or greenfield repos.** If reconnaissance surfaces no domain artifacts — no data models, no business-facing routes, no migrations, no test names that read as requirements — the repository does not establish a domain yet. Write the two overview documents as an absence report: state that the domain is not established, record the searched surfaces as `not-found-after-search`, and do not invent product behavior or source references. Surface the same finding in chat. `references/evidence-map.md` § 18 ("Signals that the domain is not here") lists what counts as an absence signal.

## Phase 1b — Coverage inventory (mandatory)

Before ranking or deep reading, enumerate every surface where business behavior can live, per candidate context, using the surface list and status values from `references/evidence-ledger.md`: deployables, routes, UI screens and actions, CLI/admin operations, jobs, producers and consumers, webhooks, tables and constraints, database-side logic, flags and configuration, reference data and seeds, outputs and communications, integrations, tests, docs.

This phase is cheap by design: directory listings, route-registration scans, schema scans, test-name listings, cron/queue configuration scans, i18n file listings. Headers and names only — no implementation reads.

The inventory is the **denominator of completeness**. Phase 3b can only close a category whose surfaces are accounted for. "Every term I found" is not coverage; "every surface in this matrix is closed" is.

## Phase 2 — Locate the domain core

The core is where the rules concentrate. Rank candidates from the inventory, cheapest signals first:

- Files whose names match the business vocabulary rather than a technical layer.
- Modules that many other modules import but that import little themselves — the stable centre.
- Files with high branching density and few framework imports: pure decision logic.
- Directories with the densest test coverage. Tests are a signal that someone feared breaking this — a hypothesis about importance, to be confirmed by reading.
- Churn, if git history is available: `git log --format= --name-only -n 400 | sort | uniq -c | sort -rn | head -40`.

Rank every module in the inventory that shows non-trivial business logic; the inventory is what makes "every module" a closed set rather than an aspiration. The core is whatever survives the ranking — typically 3–7 modules in a small service with one bounded context, 15–25 or more in a monorepo. Modules ranked below the core are not excluded: any module that owns a distinct concept, lifecycle, calculation, or permission stays in the model. Describe the core in depth and reference the rest in one paragraph each.

## Phase 3 — Harvest the rules

Read with intent, targeting the ranked files. Record each finding with the ledger schema — claim type, evidence, confidence, enforcement, consistency, runtime status. You are looking for:

- **Invariants** — conditions the system refuses to violate: guard clauses, assertions, custom exceptions, validators, database constraints.
- **Lifecycles** — status enums, state columns, transition tables, event names in the past tense (`OrderShipped`). Reconstruct the transitions the system permits and the ones it explicitly rejects (a guard or constraint that fires). A transition with no code behind it is an *absence*, not a prohibition — record it as unobserved, not as "deliberately impossible".
- **Policies and calculations** — pricing, fees, tax, eligibility, scoring, limits, prorating. Magic numbers are candidate business decisions: record the value, the location, and whether it is configurable, and classify it (domain rule / application constraint / technical detail / unknown) instead of assuming every number is a business rule.
- **Permissions and visibility** — who is allowed to do what. Role checks and tenant scoping describe the actors in the business as reliably as any org chart.
- **Processes** — for every operation inventoried in Phase 1b (route, command, job, consumer, webhook, screen action), trace it end to end: trigger → decisions → state changes → side effects (persistence, events, integrations) → visible outcome → failure and recovery paths. Every operation ends in one of four states: `traced`, `passthrough` (confirmed to carry no decision logic), `out-of-scope`, or `blocked`. An untraced operation is a coverage gap, not an omission you get to make silently.

`references/evidence-map.md` lists where each of these hides across ecosystems, with search patterns. Read it when the codebase is unfamiliar or the obvious places come up empty.

Two shortcuts that repeatedly pay off:

- **Tests are the specification the business actually agreed to.** Test names in a domain test file often read as a requirements list. Read those names before reading the implementation.
- **Error messages and validation copy are business rules in plain language.** Grep the message catalogue or i18n files.

For every rule or discrepancy, note what the code enforces, where (`path:line`), and what happens when it is violated. Record undocumented rationale as `missing-evidence`, not as a question about what the system should do. If multiple locations disagree, record each behavior with `consistency: divergent` and document the conflict directly.

### Phase 3b — Coverage gate (mandatory before assembly)

The business cannot be learned partially. Before moving to assembly, verify against the ledger that each line below is closed. A line is closed when every inventory row that feeds it is `complete`, `not-found-after-search`, or `not-applicable` (complete context mode), or explicitly declared with its status (atlas mode):

1. **Concepts and relationships** — every entity, value object, and aggregate in the inventory is in the model, with its relationships named specifically.
2. **Actors, permissions and visibility** — every role, tenant-scoping rule, and row-level filter is recorded with the operations it enables and where it is enforced.
3. **Operations and processes** — every inventoried operation is `traced`, `passthrough`, `out-of-scope`, or `blocked`. No untraced operation.
4. **Lifecycles** — every entity with a status field, transition code, or past-tense event has its permitted and explicitly rejected transitions recorded.
5. **Invariants and failure modes** — every guard, validator, custom exception, and DB constraint is in the invariant table with evidence, enforcement layer, and failure mode.
6. **Calculations, money and thresholds** — every pricing formula, rounding rule, and hardcoded threshold is in the policy table with location, config status, and classification.
7. **Time, scheduling and retention** — every cron, scheduled job, deadline, expiry, and retention rule has its business effect recorded.
8. **Integrations, events and messages** — every adapter, webhook, queue topic, and outbox entry names the external party, the direction, and the business consequence of failure.
9. **Configuration and variants** — every feature flag, plan/region/tenant branch, and environment-dependent rule is recorded with `runtime_status: config-dependent` where applicable.
10. **Outputs and communications** — every report, export, email, PDF, and notification template is tied to the process that produces it.
11. **Audit and compliance signals** — audit-log writers, consent records, retention deletions, and legal holds are recorded where they exist.
12. **Data ownership and cross-context edges** — every concept has an authoritative owner context; every cross-context event has a producer and a consumer (or the absence recorded).
13. **Terminology** — every domain term encountered appears in the glossary with its synonyms, homonyms, and where it is defined.
14. **Missing information** — every fact the repository cannot establish is listed, with the evidence of its absence.

If any line is incomplete in complete context mode, expand the ledger before assembly — do not write. In atlas mode, incomplete lines must appear in the coverage matrix and the discovery boundary of both overview documents.

## Phase 4 — Assemble the model

From the ledger, build:

- **Concept map**: the entities, their relationships, and which module owns each. Mermaid `erDiagram` or `graph`.
- **Lifecycles**: one Mermaid `stateDiagram-v2` per entity that has a meaningful state — plural, not one representative diagram.
- **Process catalog**: every material process from Phase 3, as a table — name, actor, trigger, outcome, where it is told in depth. Then narrate the two or three journeys that carry the product's value as highlighted flows. The catalog is the completeness artifact; the highlighted flows are the orientation artifact. Do not confuse them.
- **Glossary**: every domain term, in the code's words and the business's words. Flag synonyms and homonyms — the same word meaning two things in two contexts is a classic source of newcomer pain.

**Cross-context reconciliation.** When subagents or sequential passes produced per-context findings, run a merge pass before writing: events with producers but no consumers (or the reverse), terms shared across contexts with different meanings, ownership conflicts, rules duplicated across boundaries with divergent content. The seams are where end-to-end processes break; the merge pass is where you catch it.

Sanity-check the model against the data schema — and against routes, tests, and UI labels. The schema is one reconciliation source, not the arbiter: event-sourced, stateless, or externally-persisted concepts are real even when no table knows their name. A concept with no evidence anywhere is probably invented; a concept with code evidence but no table is a finding, not an error.

## Phase 5 — Value and gaps

Answer "where does the value live" with typed claims, because the repository can prove mechanisms but rarely proves commercial value:

- **Observed value mechanism** — "the pricing engine concentrates all rounding rules" is observable; say it with evidence.
- **Synthesis** — "everything else exists to feed this engine" is your analysis; label it as such.
- **Not established** — "this is why customers buy" is usually invisible from code; record it under missing information instead of inventing it.

Then close honestly. List what you could not determine: rules with no discoverable rationale, dead or ambiguous code, external systems whose contract is invisible from here. Phrase each as a question addressed to a person who would know — these are the newcomer's agenda for their first week.

## Phase 6 — Write the documents

Fill the relevant templates and write to `docs/` (or repo root if no `docs/`):

- `assets/templates/BUSINESS_OVERVIEW.template.md` → `BUSINESS_OVERVIEW.md` (always)
- `assets/templates/TECHNICAL_DOMAIN_GUIDE.template.md` → `TECHNICAL_DOMAIN_GUIDE.md` (always)
- `assets/templates/BOUNDED_CONTEXT.template.md` → `domains/<context>.md` (one per bounded context, only when the domain spans several)

Every overview file links to every per-context file, and every per-context file's "Related contexts" links back.

Calibrate the register:

- `BUSINESS_OVERVIEW.md` must be readable by someone who has never seen the code. No file paths, no class names, no framework names. Rules and concepts reference the technical guide by ID (`R-003`, `C-002`) — never by `path:line`. If a rule cannot be stated in business language, state its effect instead: not "`validateSlaWindow` throws after 48h" but "a claim not reviewed within two days is escalated automatically".
- `TECHNICAL_DOMAIN_GUIDE.md` is for someone about to change something. Lead with where the domain lives and what breaks if they touch it. Every rule gets its ID, its evidence references, and its confidence/enforcement/consistency axes.
- Per-context `domains/<context>.md` files use the business register with ID references; the `path:line` evidence lives in the technical guide.

All documents state the commit or date they were generated from, the analysis mode, and the discovery boundary. In atlas mode they also state the analyzed scope, excluded or sampled areas, and the recommended next context. Inconsistencies, contradictions, and ambiguous code belong in the relevant sections with evidence and no proposed correction.

### Phase 6b — Output verification (mandatory before delivering)

After writing, verify against the ledger and the templates. Do not deliver until every line passes; fix and re-check.

1. Every ledger finding is consumed by a deliverable or explicitly marked excluded with its reason.
2. Every `path:line` reference exists at the stated commit, and the line number is within the file's range.
3. No template placeholder remains in any document.
4. Overview and per-context files link to each other in both directions; no broken relative links.
5. Business documents contain no `path:line` references and no framework names; IDs are used instead.
6. Diagrams and their companion tables describe the same states, transitions, and relationships.
7. Every contradiction found during harvest appears with both variants, in both overviews where relevant.
8. The coverage matrix in the technical guide matches the discovery-boundary statements in all documents.
9. The analysis mode is stated, and an atlas-mode document nowhere claims the whole business is covered.
10. The three-newcomer-surprises cap is respected.

Finally, report up to three observed findings in the chat, and surface the same findings in both overview documents under "Three things that would surprise a newcomer". Mention open questions only when the repository lacks the necessary evidence; never ask the user to resolve an inconsistency found in the code. Delete the scratch ledger only after a closed complete-context run, unless the user asks to keep it; in atlas mode or after a partial run, keep the ledger so the next pass can continue from the coverage matrix instead of re-exploring.
