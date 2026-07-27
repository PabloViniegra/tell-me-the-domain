---
name: tell-me-the-domain
description: "Trigger: onboarding, business rules, document domain, legacy code, third-party code. Reconstruct a codebase's business domain into BUSINESS_OVERVIEW.md and TECHNICAL_DOMAIN_GUIDE.md."
license: MIT
metadata:
  author: "PabloViniegra"
  version: "1.0"
---

# Domain Discovery

A skill for newcomers who join a project without knowing the business behind it. Read the codebase as the written record of the business and turn it into two documents a newcomer can actually use.

The code is the only source of truth for what the system does. Treat every extraction as an observation grounded in the repository. Do not infer business intent, expected behavior, or a correction to an inconsistency.

## When to use

- A project whose business you do not understand.
- Inherited legacy or third-party code.
- Requests like "what does this system actually do", "what are the business rules here", "help me onboard", "document the domain", or explaining a codebase to non-technical stakeholders.
- Even when only onboarding, understanding, or documenting business logic is mentioned — the output files need not be named.

## What you produce

Two files, written to `docs/` (or repo root if no `docs/`):

| File | Reader | Answers |
|---|---|---|
| `BUSINESS_OVERVIEW.md` | Product owner, analyst, business-side newcomer | What the product does, for whom, the rules of the game, where the value lives |
| `TECHNICAL_DOMAIN_GUIDE.md` | Consultant or developer about to touch the code | Where the domain lives, which modules own what, which invariants not to break, with `path:line` evidence |

Both documents end with a section for facts the repository cannot establish, such as missing external contracts or undocumented rationale. Inconsistencies and ambiguities found in the code are recorded as observations in the documents, not turned into questions for the user. Both state the commit or date they were generated from. Templates live in `assets/templates/`.

## Hard rules

- **Evidence over assumption.** Every non-obvious claim in the technical guide carries `path/to/file.ext:line`. Drop or hedge what you cannot back.
- **Observed behavior only.** Document guards, constraints, transitions, calculations, permissions, naming mismatches, duplicated rules, unreachable branches, and conflicting evidence exactly as found. Do not mark expected behavior as fact and do not ask the user to resolve an inconsistency during discovery.
- **Spend tokens where the domain is.** Configuration, generated code, vendored deps, scaffolding carry almost no business. Two hundred lines of a validator beat twenty files of glue.
- **Write as you go.** Append findings to `.tell-me-the-domain/notes.md` immediately, with `path:line` and confidence. An interrupted run still leaves a trail.
- **Name things the way the business names them.** A code/UI mismatch is itself a finding. The glossary is where a newcomer gets unstuck.

## Workflow

| Phase | Output | See |
|---|---|---|
| 0. Frame the search | scope, repo shape, user context, discovery budget | `references/workflow.md` |
| 1. Cheap recon | project map, manifests, data model, entry points | `references/workflow.md` |
| 2. Locate the domain core | 3–7 ranked modules | `references/workflow.md` |
| 3. Harvest the rules | invariants, lifecycles, policies, permissions | `references/workflow.md`, `references/evidence-map.md` |
| 4. Assemble the model | concept map, lifecycles, primary flows, glossary | `references/workflow.md` |
| 5. Value and gaps | where value lives; open questions | `references/workflow.md` |
| 6. Write the documents | both output files, calibrated per audience | `references/workflow.md`, `assets/templates/` |

For large or legacy repos, apply `references/complexity-firewall.md` before deep exploration, and follow `references/token-discipline.md` throughout.

## Output contract

- Write `BUSINESS_OVERVIEW.md` and `TECHNICAL_DOMAIN_GUIDE.md` to `docs/` (or repo root if no `docs/`).
- Delete `.tell-me-the-domain/notes.md` unless the user asks to keep it.
- Tell the user in chat the two or three observed findings that would surprise a newcomer most. Mention only open questions caused by genuinely absent evidence; do not ask the newcomer to explain or resolve code inconsistencies.
- For large or legacy repos, the deliverable must state what was covered, what was sampled or excluded, which tools were unavailable, and how a second pass should continue.

## References

- `references/workflow.md` — phases 0–6 in detail.
- `references/complexity-firewall.md` — mandatory budget, partitioning, and stop conditions for large or legacy repos.
- `references/token-discipline.md` — exploration cost control.
- `references/evidence-map.md` — where domain signals hide, by artifact and ecosystem, with search patterns.
- `assets/templates/BUSINESS_OVERVIEW.template.md` — output structure for the business-side document.
- `assets/templates/TECHNICAL_DOMAIN_GUIDE.template.md` — output structure for the developer-side document.
