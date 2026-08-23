---
name: tell-me-the-domain
description: "Reconstruct a codebase's business domain into newcomer-facing docs. Use for onboarding, inherited or legacy code, clarifying business rules, or 'document the domain' requests."
license: MIT
metadata:
  author: "PabloViniegra"
  version: "1.1.0"
---

# Domain Discovery

A skill for newcomers who join a project without knowing the business behind it. Read the codebase as the written record of the business. Treat every extraction as an observation grounded in the repository; do not infer intent or propose corrections.

## Decision gate: output language

Before doing anything else, ask the user which language they want `BUSINESS_OVERVIEW.md` and `TECHNICAL_DOMAIN_GUIDE.md` written in. If the answer is empty, gibberish, or an unrecognizable language name, fall back to English. If they pick anything other than English, surface the token-cost disclaimer in `references/workflow.md` Phase 0 before proceeding.

## Decision gate: analysis mode

Choose one of two modes and state it in every deliverable:

- **Complete context mode** — the default for a single service or a user-scoped area (e.g., "just the billing service"). Within the declared boundary, the coverage inventory must close fully before writing: every surface ends `complete`, `not-found-after-search`, or `not-applicable`. A partial result is a failure, not a deliverable.
- **Repository atlas mode** — for whole-repo requests over large, legacy, or multi-context codebases. Produces a structural map of everything, full analysis of the prioritized contexts, and an explicit coverage matrix. It never claims the whole business is covered.

Decide from the user's scope and the repo shape observed in Phase 1. If the scope cannot support complete mode, run atlas mode and say so.

## Activation Contract

- A project whose business you do not understand.
- Inherited legacy or third-party code.
- Explaining a product's business to a non-technical stakeholder — consultant, analyst, or new account manager stepping into a product they did not build.
- Requests like "what does this system actually do", "what are the business rules here", "help me onboard", "document the domain".
- Triggers where the request mentions only onboarding, understanding, or documenting the domain (the output filenames may not appear in the prompt).

## What you produce

The two files below are written to `docs/` (or repo root if no `docs/`). When the domain spans several bounded contexts, additional `docs/domains/<context>.md` files are produced — one per bounded context — each linked from both overview files so the document structure screams the domain.

| File | Reader | Answers |
|---|---|---|
| `BUSINESS_OVERVIEW.md` | Product owner, analyst, business-side newcomer | What the product does, for whom, the rules of the game, where the value lives |
| `TECHNICAL_DOMAIN_GUIDE.md` | Consultant or developer about to touch the code | Where the domain lives, which modules own what, which invariants not to break, with `path:line` evidence |
| `docs/domains/<context>.md` *(when the domain spans several bounded contexts)* | Same audiences, scoped to one bounded context | Same questions, narrowed to one context, with cross-context relationships stated in the overview files |

Both documents end with a section for facts the repository cannot establish, such as missing external contracts or undocumented rationale. Inconsistencies and ambiguities found in the code are recorded as observations in the documents, not turned into questions for the user. Both state the commit or date they were generated from. Templates live in `assets/templates/`.

## Hard rules

These are non-negotiable. They govern extraction discipline, the depth expectation of the deliverable, and the gate the agent must pass before writing.

- **Evidence over assumption.** Every non-obvious claim in the technical guide carries `path/to/file.ext:line`. Drop or hedge what you cannot back. Every claim is typed — `observed`, `documented`, `synthesis`, `hypothesis`, `missing-evidence` — per `references/evidence-ledger.md`.
- **Observed behavior only.** Document guards, constraints, transitions, calculations, permissions, naming mismatches, duplicated rules, unreachable branches, and conflicting evidence exactly as found. Code present is not code running: distinguish active behavior from config-dependent, inactive, test-only, and unreachable code. Do not mark expected behavior as fact and do not ask the user to resolve an inconsistency during discovery.
- **Spend tokens where the domain is.** Configuration, generated code, vendored deps, scaffolding carry almost no business — but inspect them when the coverage inventory marks them as contract, reference data, or the only statement of a rule. Depth lives in validators, transitions, and policies — not in glue code, scaffolding, or generated files.
- **Write as you go.** Append findings to `.tell-me-the-domain/notes.md` immediately, using the full finding schema in `references/evidence-ledger.md`. An interrupted run still leaves a trail.
- **Name things the way the business names them.** A code/UI mismatch is itself a finding. The glossary is where a newcomer gets unstuck.
- **Complete means accounted for.** A surface is covered when it is modelled, confirmed absent after searching, declared `not-applicable`, or explicitly declared `partial` / `blocked` / `out-of-scope` — never when it was simply never searched. The coverage inventory is the denominator; both gates check closure against it.
- **Depth beats brevity — in the deliverable.** Each main concept is developed in depth — definition, attributes, relationships, processes, and why a newcomer must understand it (see `assets/templates/BUSINESS_OVERVIEW.template.md` § The main concepts). Every concept the business uses is included in the model; none reduced to a one-liner. File length matches what the domain requires, not a target. The two overview files are floor, not ceiling; when the domain spans several bounded contexts, additional `docs/domains/<context>.md` files are produced from `assets/templates/BOUNDED_CONTEXT.template.md`, one per bounded context, and every overview file links to them clearly so the document structure screams the domain. **Exploration depth is governed by `references/token-discipline.md` — this rule does not lift that budget.**
- **Pass the coverage gate before writing.** Before assembly, every checklist line in `references/workflow.md` § "Phase 3b — Coverage gate" must be closed against the coverage inventory. A partial model passed off as complete is the failure mode this gate exists to prevent.
- **Pass the output verification after writing.** After `Phase 6`, every check in `references/workflow.md` § "Phase 6b — Output verification" must pass. The verification gate is non-negotiable even when writing was clean.

## Execution Steps

| Phase | Output | See |
|---|---|---|
| 0. Frame the search | scope, mode, repo shape, user context, discovery budget | `references/workflow.md` |
| 1. Cheap recon | project map, manifests, data model, entry points | `references/workflow.md` |
| 1b. Coverage inventory | every business surface enumerated, with status — the denominator of completeness | `references/workflow.md`, `references/evidence-ledger.md` |
| 2. Locate the domain core | every module with non-trivial business logic, ranked | `references/workflow.md` |
| 3. Harvest the rules | invariants, lifecycles, policies, permissions, processes traced end to end | `references/workflow.md`, `references/evidence-map.md` |
| 3b. Coverage gate | fourteen categories closed against the inventory | `references/workflow.md` |
| 4. Assemble the model | concept map, lifecycles, process catalog, glossary, cross-context reconciliation | `references/workflow.md` |
| 5. Value and gaps | typed value claims; open questions | `references/workflow.md` |
| 6. Write the documents | overview files + per-context files, calibrated to depth of domain | `references/workflow.md`, `assets/templates/` |
| 6b. Output verification | ledger consumed, references valid, registers clean, matrix consistent | `references/workflow.md` |

For large or legacy repos, apply `references/complexity-firewall.md` before deep exploration, and follow `references/token-discipline.md` throughout.

## Output contract

- Write `BUSINESS_OVERVIEW.md` and `TECHNICAL_DOMAIN_GUIDE.md` to `docs/` (or repo root if no `docs/`). When the domain spans several bounded contexts, also write the corresponding `docs/domains/<context>.md` files; each one is referenced from both overview files.
- Write all documents in the language the user chose upfront. See `references/workflow.md` Phase 0 for the ask script and the token-cost disclaimer shown to non-English users.
- State the analysis mode (complete context or repository atlas) and the commit or date in every document.
- Delete `.tell-me-the-domain/notes.md` only after a closed complete-context run, unless the user asks to keep it. In atlas mode or after a partial run, keep the ledger so the next pass continues from the coverage matrix instead of re-exploring.
- Hard cap of three observed findings: tell the user in chat up to three findings that would surprise a newcomer most, and surface the same findings in both documents under "Three things that would surprise a newcomer". Mention only open questions caused by genuinely absent evidence; do not ask the newcomer to explain or resolve code inconsistencies.
- In atlas mode, the deliverable must include the coverage matrix: what was covered, what was sampled or excluded, which tools were unavailable, and how a second pass should continue.

## References

- `references/workflow.md` — phases 0–6b in detail.
- `references/evidence-ledger.md` — claim types, finding schema, and coverage inventory format.
- `references/complexity-firewall.md` — mandatory budget, partitioning, and stop conditions for large or legacy repos.
- `references/token-discipline.md` — exploration cost control.
- `references/evidence-map.md` — where domain signals hide, by artifact and ecosystem, with search patterns.
- `assets/templates/BUSINESS_OVERVIEW.template.md` — output structure for the business-side document.
- `assets/templates/TECHNICAL_DOMAIN_GUIDE.template.md` — output structure for the developer-side document.
- `assets/templates/BOUNDED_CONTEXT.template.md` — output structure for one bounded context (when the domain spans several).
