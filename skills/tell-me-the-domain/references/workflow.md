# Workflow

Seven phases, in order. Each ends with a clear handoff to the next.

## Phase 0 — Frame the search

Before reading anything, establish:

- **Output language.** Ask the user upfront which language they want the two output documents written in. If the answer is empty, gibberish, or an unrecognizable language name, fall back to English. If the user picks anything other than English, surface this disclaimer before proceeding and let them confirm:
  > Non-English output uses more tokens per word than English on most tokenizers (Latin-script languages ~1.5–2x; non-Latin scripts such as Chinese, Japanese, Korean, or Arabic 2–4x). The exploration phase is unchanged; only the document-writing phase pays the extra cost.
  Form-filling vocabulary (Mermaid labels, status enums, code identifiers, proper nouns) stays in the source language of the codebase regardless.
- The repository root and whether this is a monorepo (several deployables) or a single service.
- Whether the user wants the whole repo or one bounded area (e.g., "just the billing service").
- Anything they already know: the industry, the customer, the vocabulary. One sentence of context saves a lot of guessing.
- A discovery budget: target one bounded context, 10–20 candidate files, and a small set of evidence-backed rules before expanding. In a large repository, "whole repo" means a structural map plus prioritized contexts, not exhaustive reading.

If the scope is ambiguous and the answer cannot be determined from the repository, ask one question only when proceeding would make the documents misleading. Do not ask about incoherencies, contradictions, naming mismatches, or behavior that appears unexpected: record the observed variants and their evidence, then continue.

Create the scratch file at `.tell-me-the-domain/notes.md` and begin.

## Phase 1 — Cheap recon

Build a map before opening any implementation file. All of this is high signal per token:

1. **Project map and dependency overview.** If structural-analysis tools are available (Graphify, knowledge-graph builders, AST-based explorers), use them first to produce the structural map and the call/import graph. What calls what and what depends on what arrive as a compact graph instead of a flood of file reads. If absent, fall back to the items below.
2. **Directory shape**, two or three levels deep, excluding `node_modules`, `vendor`, `dist`, `target`, `.git`. Domain-oriented folder names (`orders/`, `underwriting/`, `payroll/`) are a gift; layer-oriented names (`controllers/`, `services/`) mean the domain hides one level down, inside file names.
3. **README, docs folder, ADRs, CHANGELOG.** Often the only place the *why* survives. Skim, do not read line by line.
4. **Manifests** (`package.json`, `go.mod`, `pyproject.toml`, `pom.xml`, `*.csproj`, `Gemfile`). Dependencies name the business: a payments SDK, a tax engine, an EDI parser, a scheduling library each imply a whole problem space.
5. **Data model.** Migrations, schema files, ORM entities, `.proto`, OpenAPI specs. Tables, columns and enums are the vocabulary of the business, and `NOT NULL`, `UNIQUE`, `CHECK` and foreign keys are business rules that someone bothered to enforce at the last line of defence.
6. **Entry points and routes.** The public API surface tells you which operations the outside world is allowed to perform — that list is close to the list of use cases.

Record in the notes: candidate bounded contexts, the entity vocabulary, and 10–20 files that look like they hold domain logic. Rank them; you will not read all of them.

## Phase 2 — Locate the domain core

The core is where the rules concentrate. Rank candidates by these signals, cheapest first:

- Files whose names match the business vocabulary rather than a technical layer.
- Modules that many other modules import but that import little themselves — the stable centre.
- Files with high branching density and few framework imports: pure decision logic.
- Directories with the densest test coverage. Teams test what they are afraid of breaking, and what they are afraid of breaking is the business.
- Churn, if git history is available: `git log --format= --name-only -n 400 | sort | uniq -c | sort -rn | head -40`. Frequently changed domain files mean rules that are still evolving.

Pick the three to seven modules that survive this ranking. That is the core. Everything else is delivery mechanism, and you can describe it in a sentence.

## Phase 3 — Harvest the rules

Now read with intent, targeting the ranked files. You are looking for four things:

- **Invariants** — conditions the system refuses to violate: guard clauses, assertions, custom exceptions, validators, database constraints.
- **Lifecycles** — status enums, state columns, transition tables, event names in the past tense (`OrderShipped`). A state machine is a business process written down; reconstruct the legal transitions and, more importantly, the illegal ones.
- **Policies and calculations** — pricing, fees, tax, eligibility, scoring, limits, prorating. Magic numbers and thresholds are business decisions someone made in a meeting. Record the number *and* where it lives, because a hardcoded threshold is an operational risk worth flagging.
- **Permissions and visibility** — who is allowed to do what. Role checks and tenant scoping describe the actors in the business as reliably as any org chart.

`references/evidence-map.md` lists where each of these hides across ecosystems, with search patterns. Read it when the codebase is unfamiliar or the obvious places come up empty.

Two shortcuts that repeatedly pay off:

- **Tests are the specification the business actually agreed to.** Test names in a domain test file often read as a requirements list. Read those names before reading the implementation.
- **Error messages and validation copy are business rules in plain language.** Grep the message catalogue or i18n files; they translate `ERR_LIMIT_4092` into something a human wrote for a human.

For every rule or discrepancy you record, note what the code enforces, where (`path:line`), and what happens when it is violated. Assign an initial confidence (`high` / `medium` / `low`) using the criterion in the technical template — this is what the deliverable will surface to the reader, so get it right during extraction. Record undocumented rationale as an observation of missing evidence, not as a question about what the system should do. If multiple locations disagree, document each behavior and the conflict directly.

## Phase 4 — Assemble the model

From the notes, build:

- **Concept map**: the main entities, their relationships, and which module owns each. Express as a Mermaid `erDiagram` or `graph`.
- **Lifecycles**: one Mermaid `stateDiagram-v2` per entity that has a meaningful state, showing transitions and their triggers.
- **Primary flows**: the two or three journeys that carry the product's value, end to end, in business terms — "a customer places an order and the warehouse gets picked".
- **Glossary**: every domain term, in the code's words and the business's words, with a one-line definition and where it is defined. Flag synonyms and, especially, homonyms — the same word meaning two different things in two contexts is a classic source of newcomer pain.

Sanity-check the model against the data schema. If your model has a concept the database has never heard of, you probably invented it.

## Phase 5 — Value and gaps

Answer, explicitly, "where does the value live". Usually one of: a calculation nobody else does well, an integration that is hard to obtain, accumulated data, or a workflow that removes manual work. The rest of the system exists to support it, and saying so out loud reorients a newcomer faster than any diagram.

Then close honestly. List what you could not determine: rules with no discoverable rationale, dead or ambiguous code, external systems whose contract is invisible from here. Phrase each as a question addressed to a person who would know. These questions are one of the most valuable parts of the output — they are the newcomer's agenda for their first week.

## Phase 6 — Write the documents

Fill `assets/templates/BUSINESS_OVERVIEW.template.md` and `assets/templates/TECHNICAL_DOMAIN_GUIDE.template.md`, then write both files to the target directory.

Calibrate the register:

- `BUSINESS_OVERVIEW.md` must be readable by someone who has never seen the code. No file paths, no class names, no framework names. If a rule cannot be stated in business language, state its effect instead: not "`validateSlaWindow` throws after 48h" but "a claim not reviewed within two days is escalated automatically".
- `TECHNICAL_DOMAIN_GUIDE.md` is for someone about to change something. Lead with where the domain lives and what will break if they touch it. Every rule gets its evidence reference.

Both documents state the commit or date they were generated from and end with a section limited to information absent from the repository. Inconsistencies, contradictions, and ambiguous code belong in the relevant rules, risks, observations, or glossary sections, with evidence and no proposed correction. For large or legacy repositories, also state the analyzed scope, excluded or sampled areas, discovery budget reached, confidence limits, and recommended next context.

Finally, tell the user in the chat the two or three observed findings that would surprise a newcomer most. Mention open questions only when the repository lacks the necessary evidence; never ask the user to resolve an inconsistency found in the code. Delete the scratch file unless they want to keep it.
