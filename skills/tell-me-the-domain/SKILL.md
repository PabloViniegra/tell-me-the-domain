---
name: tell-me-the-domain
description: "Reconstruct a codebase's business domain into newcomer-facing docs. Use for onboarding, inherited or legacy code, clarifying business rules, or 'document the domain' requests."
license: MIT
metadata:
  author: "PabloViniegra"
  version: "1.0"
---

# Domain Discovery

> Skill name in the registry: `tell-me-the-domain`.

A skill for newcomers who join a project without knowing the business behind it. Read the codebase as the written record of the business. Treat every extraction as an observation grounded in the repository; do not infer intent or propose corrections. Two hundred lines of a validator beat twenty files of glue — depth where the domain is, terseness everywhere else.

## Decision gate: output language

Before doing anything else, ask the user which language they want `BUSINESS_OVERVIEW.md` and `TECHNICAL_DOMAIN_GUIDE.md` written in. If the answer is empty, gibberish, or an unrecognizable language name, fall back to English. If they pick anything other than English, surface the token-cost disclaimer in `references/workflow.md` Phase 0 before proceeding.

## Activation Contract

- A project whose business you do not understand.
- Inherited legacy or third-party code.
- Explaining a product's business to a non-technical stakeholder — consultant, analyst, or new account manager stepping into a product they did not build.
- Requests like "what does this system actually do", "what are the business rules here", "help me onboard", "document the domain".
- Even when only onboarding, understanding, or documenting business logic is mentioned — the output files need not be named.

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

- **Evidence over assumption.** Every non-obvious claim in the technical guide carries `path/to/file.ext:line`. Drop or hedge what you cannot back.
- **Observed behavior only.** Document guards, constraints, transitions, calculations, permissions, naming mismatches, duplicated rules, unreachable branches, and conflicting evidence exactly as found. Do not mark expected behavior as fact and do not ask the user to resolve an inconsistency during discovery.
- **Spend tokens where the domain is.** Configuration, generated code, vendored deps, scaffolding carry almost no business. Depth lives in validators, transitions, and policies — not in glue code, scaffolding, or generated files.
- **Write as you go.** Append findings to `.tell-me-the-domain/notes.md` immediately, with `path:line` and confidence. An interrupted run still leaves a trail.
- **Name things the way the business names them.** A code/UI mismatch is itself a finding. The glossary is where a newcomer gets unstuck.
- **Depth beats brevity — in the deliverable.** Each main concept is developed in depth — definition, attributes, relationships, processes, and why a newcomer must understand it (see `assets/templates/BUSINESS_OVERVIEW.template.md` § The main concepts). Every concept the business uses is included in the model; none reduced to a one-liner. File length matches what the domain requires, not a target. The two overview files are floor, not ceiling; when the domain spans several bounded contexts, additional `docs/domains/<context>.md` files are produced from `assets/templates/BOUNDED_CONTEXT.template.md`, one per bounded context, and every overview file links to them clearly so the document structure screams the domain. **Exploration depth is governed by `references/token-discipline.md` — this rule does not lift that budget.**
- **Pass the coverage gate before writing.** Before moving from Phase 3 to Phase 4 in `references/workflow.md`, every checklist line in § "Phase 3b — Coverage gate (mandatory before assembly)" — Glossary, Lifecycles, Invariants, Calculations, Permissions — must be complete. A partial model is the failure mode this rule exists to prevent; cover the whole business, then write.

## Execution Steps

| Phase | Output | See |
|---|---|---|
| 0. Frame the search | scope, repo shape, user context, discovery budget | `references/workflow.md` |
| 1. Cheap recon | project map, manifests, data model, entry points | `references/workflow.md` |
| 2. Locate the domain core | every module with non-trivial business logic, ranked | `references/workflow.md` |
| 3. Harvest the rules | invariants, lifecycles, policies, permissions | `references/workflow.md`, `references/evidence-map.md` |
| 3b. Coverage gate | glossary, lifecycles, invariants, calculations, permissions all complete | `references/workflow.md` |
| 4. Assemble the model | concept map, lifecycles, primary flows, glossary | `references/workflow.md` |
| 5. Value and gaps | where value lives; open questions | `references/workflow.md` |
| 6. Write the documents | overview files + per-context files (one per bounded context), calibrated to depth of domain | `references/workflow.md`, `assets/templates/` |

For large or legacy repos, apply `references/complexity-firewall.md` before deep exploration, and follow `references/token-discipline.md` throughout.

## Output contract

- Write `BUSINESS_OVERVIEW.md` and `TECHNICAL_DOMAIN_GUIDE.md` to `docs/` (or repo root if no `docs/`). When the domain spans several bounded contexts, also write the corresponding `docs/domains/<context>.md` files; each one is referenced from both overview files.
- Write all documents in the language the user chose upfront. See `references/workflow.md` Phase 0 for the ask script and the token-cost disclaimer shown to non-English users.
- Delete `.tell-me-the-domain/notes.md` unless the user asks to keep it.
- Hard cap of three observed findings: tell the user in chat up to three findings that would surprise a newcomer most, and surface the same findings in both documents under "Three things that would surprise a newcomer". Mention only open questions caused by genuinely absent evidence; do not ask the newcomer to explain or resolve code inconsistencies.
- For large or legacy repos, the deliverable must state what was covered, what was sampled or excluded, which tools were unavailable, and how a second pass should continue.

## References

- `references/workflow.md` — phases 0–6 in detail.
- `references/complexity-firewall.md` — mandatory budget, partitioning, and stop conditions for large or legacy repos.
- `references/token-discipline.md` — exploration cost control.
- `references/evidence-map.md` — where domain signals hide, by artifact and ecosystem, with search patterns.
- `assets/templates/BUSINESS_OVERVIEW.template.md` — output structure for the business-side document.
- `assets/templates/TECHNICAL_DOMAIN_GUIDE.template.md` — output structure for the developer-side document.
- `assets/templates/BOUNDED_CONTEXT.template.md` — output structure for one bounded context (when the domain spans several).
