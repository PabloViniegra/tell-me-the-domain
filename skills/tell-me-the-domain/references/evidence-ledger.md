# Evidence Ledger

`.tell-me-the-domain/notes.md` is the run's working memory. It has two parts: a **coverage inventory** created in Phase 1b, and a **findings log** appended from Phase 2 onward. Both use the schemas below so two runs produce comparable artifacts and the coverage gate has something concrete to check.

## Claim types

Every finding is exactly one of these. Claim type travels with the finding into the deliverables.

| Type | Meaning |
|---|---|
| `observed` | Behavior the code executes or rejects, backed by `path:line`. |
| `documented` | A claim made by repo docs, comments, ADRs, or commit history, not confirmed in executable code. |
| `synthesis` | Your composition of several observations into a model element (e.g., "this module owns pricing"). Always labelled; never presented as observed. |
| `hypothesis` | A plausible reading that still needs confirmation. Cannot appear in deliverables as fact. |
| `missing-evidence` | A fact the repository does not establish. |

Search heuristics (directory names, dependency lists, churn, test density) promote hypotheses. Only evidence confirms observations.

## Finding schema

One entry per finding:

| Field | Values |
|---|---|
| `id` | Stable ID from the prefix table below. The deliverables reference these IDs. |
| `context` | Bounded context or module it belongs to. |
| `kind` | One value from the kind table below. |
| `claim` | The statement, in one sentence. |
| `claim_type` | One of the five types above. |
| `evidence` | `path:line` list; empty only for `missing-evidence`. |
| `actor` / `trigger` / `outcome` | For processes and rules: who, what starts it, what results. |
| `failure_mode` | What happens when violated: exception, HTTP status, silent fallback, nothing observed. |
| `evidence_confidence` | `direct` (the code or docs say it) / `corroborated` (two independent artifacts agree) / `indirect` (inferred from naming or shape). |
| `enforcement` | `db` / `domain` / `application` / `edge` / `docs-only` / `none`. Where the rule is enforced, not how much you trust it. |
| `consistency` | `consistent` / `divergent` / `unknown` across layers. |
| `runtime_status` | `active` / `config-dependent` / `inactive` / `test-only` / `unreachable` / `unknown`. Code present is not code running. |
| `coverage_status` | Same six values as the inventory: `complete` / `partial` / `blocked` / `not-found-after-search` / `not-applicable` / `out-of-scope`. |
| `next_search` | The next thing this finding tells you to look at, if any. |

Confidence, enforcement, and consistency are separate axes on purpose: a rule enforced in one layer can be certain; three layers can repeat the same historical error.

### Kinds and ID prefixes

| Prefix | Kind | Use |
|---|---|---|
| `C` | `concept` | Entity, value object, aggregate |
| `P` | `process` | End-to-end operation or journey |
| `R` | `rule`, `calculation`, `permission`, `conflict`, `time`, `output`, `configuration`, `audit`, `ownership` | Invariant, formula, who-may, competing variants, deadline, outward artifact, flag/plan, audit trail, or authoritative owner |
| `A` | `actor` | Human role, job, or external system that acts |
| `T` | `terminology` | Domain term, synonym, or homonym |
| `L` | `lifecycle` | Status set and transitions |
| `E` | `integration` | Event, adapter, webhook, or bus contract |
| `F` | `absent` | Fact the repository does not establish |

Set `kind` to the specific value (`calculation`, `conflict`, `configuration`, …). The prefix stays `R` for every rule-shaped finding. Do not invent prefixes outside this table. Existing oracles that already use `R-` for calculations and conflicts stay valid.

## Coverage inventory

Created in Phase 1b, before any deep read. One row per surface per context:

| Context | Surface | Artifacts found | Reviewed | Excluded | Status | Note |
|---|---|---|---|---|---|---|

Surfaces to enumerate: deployables/modules, HTTP routes, GraphQL/CLI/admin operations, UI screens and actions, jobs and schedulers, event producers and consumers, webhook handlers, tables/enums/constraints, database-side logic (triggers, procedures, views, RLS), feature flags and configuration, reference data and seeds, outputs (reports, exports, emails, documents), integrations and adapters, tests and BDD specs, docs.

Status values:

| Status | Meaning |
|---|---|
| `complete` | Fully read and modelled. |
| `partial` | Sampled; the note says what remains. |
| `blocked` | Evidence unavailable (missing tool, unreadable artifact). |
| `not-found-after-search` | Searched with the patterns in `evidence-map.md`; nothing found. |
| `not-applicable` | This surface cannot exist here (e.g., no UI in a library). |
| `out-of-scope` | Excluded by the user's declared scope. |

Closure rule: in **complete context mode**, every row must end `complete`, `not-found-after-search`, or `not-applicable` before writing. In **repository atlas mode**, `partial`, `blocked`, and `out-of-scope` rows are legal deliverables — but they must appear verbatim in the coverage matrix of the technical guide and in the discovery boundary of both overview documents.
