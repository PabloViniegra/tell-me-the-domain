---
name: tell-me-the-domain
description: Explore an unfamiliar codebase to reconstruct its business domain — the core concepts, the rules that constrain them, why those rules exist, and where the product's value lives — then produce BUSINESS_OVERVIEW.md (for business-side readers) and TECHNICAL_DOMAIN_GUIDE.md (for consultants and developers). Use this whenever someone lands on a project whose business they don't understand, inherits legacy or third-party code, asks "what does this system actually do", "what are the business rules here", "help me onboard onto this repo", "document the domain", or needs to explain a codebase to non-technical stakeholders. Trigger it even when the request only mentions understanding, onboarding, or documenting business logic without naming these files.
---

# Domain Discovery

Most people join a project without knowing the business behind it. They learn it slowly, by colliding with the code. This skill compresses that process: read the codebase as the written record of the business, and turn it into two documents that a newcomer can actually use.

The code is the only source of truth that never lies about what the system *does* — but it is silent about *why*. Treat everything you extract as an observation, and be explicit about the difference between what the code proves and what you inferred.

## What you produce

Two files, written in the repository (default: `docs/`, or the repo root if there is no docs folder):

| File | Reader | Answers |
|---|---|---|
| `BUSINESS_OVERVIEW.md` | Product owner, analyst, new joiner from the business side | What does this product do, for whom, what are the rules of the game, where is the value |
| `TECHNICAL_DOMAIN_GUIDE.md` | Consultant or developer about to touch the code | Where the domain lives in the tree, which modules own which concepts, which invariants to not break, with `path:line` evidence |

Both are generated from the templates in `assets/`. Keep the structure of the templates — a predictable shape is what makes these docs skimmable across projects.

## Operating principles

**Evidence over assumption.** Every non-obvious claim in `TECHNICAL_DOMAIN_GUIDE.md` carries a `path/to/file.ext:42` reference. When you cannot back a claim, either drop it or move it to the open questions section.

**Separate observed from inferred.** "Orders cannot ship without payment" is observed if a guard clause enforces it. "Because chargebacks were a problem" is a guess — never write guesses as fact. Mark inference with a short hedge ("appears to", "suggests") and put the real uncertainty into the open questions.

**Spend tokens where the domain is.** Configuration, build tooling, generated code and vendored dependencies contain almost no business. Two hundred lines of a validator or a state machine are worth more than twenty files of scaffolding. See "Token discipline" below.

**Write as you go.** Keep a scratch file at `.tell-me-the-domain/notes.md` and append findings the moment you make them, with their file reference. This lets you move on without carrying source content in context, and it means an interrupted run still leaves something useful behind.

**Name things the way the business names them.** If the code says `Policy` and the UI copy says "contract", record both — the mismatch is itself a finding, and the glossary is where a newcomer gets unstuck fastest.

## Phase 0 — Frame the search

Before reading anything, establish:

- The repository root and whether this is a monorepo (several deployables) or a single service.
- Whether the user wants the whole repo or one bounded area ("just the billing service").
- Anything they already know: the industry, the customer, the vocabulary. A single sentence of context from them saves a lot of guessing.
- A discovery budget: target one bounded context, 10–20 candidate files, and a small set of evidence-backed rules before expanding. In a large repository, "whole repo" means a structural map plus prioritized contexts, not exhaustive reading.

If the scope is ambiguous and cheap to clarify, ask one question. Otherwise proceed and state your assumption in the output.

Create the scratch file and begin.

## Complexity firewall — mandatory for large or legacy repositories

Treat repository size, coupling, and uncertainty as signals to narrow scope, not invitations to read more. Before deep exploration:

1. **Map before opening files.** Use available AST/import/call-graph, symbol, impact-analysis, and code-search tools. If a tool is unavailable or incomplete, record that limitation and use directory shape, manifests, routes, schemas, tests, and git history as fallbacks.
2. **Partition by business boundary.** In a monorepo or tangled legacy system, identify deployables, bounded contexts, data ownership, queues, and external integrations. Work one context at a time. Do not merge subagent findings until each has compact evidence and uncertainty.
3. **Prioritize hotspots.** Rank files by domain vocabulary, fan-in, branching/decision density, test coverage, churn, and proximity to data or integration boundaries. Use impact analysis before following a dependency chain.
4. **Cap exploration.** Start with 10–20 candidates, 3–7 core modules, and 2–3 value flows. Read only enough to confirm or reject a hypothesis. After three consecutive files add no new concept or rule, stop that branch.
5. **Keep an evidence ledger.** Every finding records `observed | inferred | unknown`, `path:line`, confidence, and the next action. Never promote an inference to a rule merely because multiple layers repeat it.
6. **Escalate instead of guessing.** Stop and ask the user when context boundaries, business scope, or conflicting rules cannot be resolved cheaply. Otherwise isolate the ambiguity in open questions and continue without inventing rationale.
7. **Protect context and the repository.** Never read generated code, lockfiles, vendored code, snapshots, fixtures, or whole large files. Use targeted searches and bounded slices. Only write the scratch file and requested domain documents; never change product source.

When complexity is high, the deliverable must say what was covered, what was intentionally sampled or excluded, which tools were unavailable, and how a second pass should continue. A partial, traceable model is safer than a confident full-repo fiction.

## Phase 1 — Cheap recon

Build a map before opening any implementation file. All of this is high signal per token:

0. **Project map and dependency overview.** If structural-analysis tools are available (Graphify, knowledge-graph builders, AST-based explorers), use them first to produce the structural map and the call/import graph. What calls what and what depends on what arrive as a compact graph instead of a flood of file reads. If absent, fall back to the items below.
1. **Directory shape**, two or three levels deep, excluding `node_modules`, `vendor`, `dist`, `target`, `.git`. Domain-oriented folder names (`orders/`, `underwriting/`, `payroll/`) are a gift; layer-oriented names (`controllers/`, `services/`) mean the domain hides one level down, inside file names.
2. **README, docs folder, ADRs, CHANGELOG.** Often the only place the *why* survives. Skim, do not read line by line.
3. **Manifests** (`package.json`, `go.mod`, `pyproject.toml`, `pom.xml`, `*.csproj`, `Gemfile`). Dependencies name the business: a payments SDK, a tax engine, an EDI parser, a scheduling library each imply a whole problem space.
4. **Data model.** Migrations, schema files, ORM entities, `.proto`, OpenAPI specs. Tables, columns and enums are the vocabulary of the business, and `NOT NULL`, `UNIQUE`, `CHECK` and foreign keys are business rules that someone bothered to enforce at the last line of defence.
5. **Entry points and routes.** The public API surface tells you which operations the outside world is allowed to perform — that list is close to the list of use cases.

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

**Invariants** — conditions the system refuses to violate: guard clauses, assertions, custom exceptions, validators, database constraints.

**Lifecycles** — status enums, state columns, transition tables, event names in the past tense (`OrderShipped`). A state machine is a business process written down; reconstruct the legal transitions and, more importantly, the illegal ones.

**Policies and calculations** — pricing, fees, tax, eligibility, scoring, limits, prorating. Magic numbers and thresholds are business decisions someone made in a meeting. Record the number *and* where it lives, because a hardcoded threshold is an operational risk worth flagging.

**Permissions and visibility** — who is allowed to do what. Role checks and tenant scoping describe the actors in the business as reliably as any org chart.

`references/evidence-map.md` lists where each of these hides across ecosystems, with search patterns. Read it when the codebase is unfamiliar or the obvious places come up empty.

Two shortcuts that repeatedly pay off:

- **Tests are the specification the business actually agreed to.** Test names in a domain test file often read as a requirements list. Read those names before reading the implementation.
- **Error messages and validation copy are business rules in plain language.** Grep the message catalogue or i18n files; they translate `ERR_LIMIT_4092` into something a human wrote for a human.

For every rule you record, note: what it enforces, where (`path:line`), what happens when it is violated, and whether the *why* is documented anywhere or unknown. The unknowns become your open questions.

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

Fill `assets/BUSINESS_OVERVIEW.template.md` and `assets/TECHNICAL_DOMAIN_GUIDE.template.md`, then write both files to the target directory.

Calibrate the register:

- `BUSINESS_OVERVIEW.md` must be readable by someone who has never seen the code. No file paths, no class names, no framework names. If a rule cannot be stated in business language, state its effect instead: not "`validateSlaWindow` throws after 48h" but "a claim not reviewed within two days is escalated automatically".
- `TECHNICAL_DOMAIN_GUIDE.md` is for someone about to change something. Lead with where the domain lives and what will break if they touch it. Every rule gets its evidence reference.

Both documents end with the open questions. Both state, near the top, the commit or date they were generated from — domain docs rot, and a reader deserves to know how much to trust them. For large or legacy repositories, also state the analyzed scope, excluded or sampled areas, discovery budget reached, confidence limits, and recommended next context.

Finally, tell the user in the chat: the two or three findings that would surprise a newcomer most, and the open questions that most need a human answer. Delete the scratch file unless they want to keep it.

## Token discipline

Exploration is where this skill can waste an enormous amount of context, so:

- Set a discovery budget before searching: bounded contexts, candidate files, core modules, and value flows. Expand it only when a new high-confidence finding justifies the cost.
- Prefer structural tools and targeted search with line numbers and two or three lines of context (`rg -n -C2`) over opening files. Graphs answer "what matters"; search answers "does this rule exist"; file reads confirm only the highest-ranked hypotheses.
- Use symbol/flow/impact tools to traverse only relevant callers and dependants. Do not recursively chase every import from a domain file.
- Classify a file by reading its first ~60 lines. Read a file in full only if it is in the ranked core and reasonably short.
- Never read generated code, lockfiles, vendored dependencies, snapshots, or fixtures. Sample large test suites by name only.
- Append to the notes file immediately after each read, including evidence type, confidence, and the next search. The note replaces the source.
- Work context by context in a monorepo, finishing one before starting the next. Keep raw subagent output out of the main context; require compact findings with references.
- Stop at saturation, budget exhaustion, or unresolved boundary ambiguity. Report the stopping reason instead of silently broadening scope.
- If three consecutive files add no new concept or rule, stop that branch. Breadth of concepts beats depth on any single module — a newcomer needs the map, not the terrain.
- If subagents are available, fan out one per bounded context, and require each to return only: scope, concepts, rules with references, confidence, conflicts, exclusions, and open questions. The point is that raw exploration never enters the main context.

## Reference material

- `references/evidence-map.md` — where domain signals hide, by artifact type and ecosystem, with search patterns. Read during Phase 1 or 3 when the codebase is unfamiliar.
- `assets/BUSINESS_OVERVIEW.template.md`, `assets/TECHNICAL_DOMAIN_GUIDE.template.md` — output structures. Read before Phase 6.
