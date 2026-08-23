# tell-me-the-domain

[![skills.sh](https://skills.sh/b/PabloViniegra/tell-me-the-domain)](https://skills.sh/PabloViniegra/tell-me-the-domain)


> **Day one: You land on a new project.** Nobody explains what it’s actually about or what it does. That onboarding meeting with your Tech Lead never happens, yet tasks are already being assigned to you before you even grasp the basics of the business you're coding for.
>
> **This skill helps you understand the project’s business logic directly from the codebase** — the record of what the system actually *does*, in contradiction to what outdated documentation can claim.
>
> The code is evidence, not an oracle: it shows what is implemented, not why it exists, how the product is sold, or which processes still happen outside it. The skill documents the implemented domain with evidence, labels interpretive claims as synthesis, and declares honestly what the repository cannot establish.

A reusable agent skill for reconstructing the business domain of an unfamiliar codebase. It reads the repository as the only source of truth that never lies about what the system *does*, and turns it into documents a newcomer can actually use. Output depth matches what the domain requires; per-context files extend the model when the domain spans several bounded contexts.

## Install

```
npx skills add PabloViniegra/tell-me-the-domain
```

## What it does

Given a codebase, the skill produces structured documents alongside the project source. Two overview files are always produced; per-context files are added when the domain spans several bounded contexts.

| Document | Audience | Purpose |
|---|---|---|
| `BUSINESS_OVERVIEW.md` | Product owners, analysts, new joiners from the business side | What the product does, for whom, what rules govern it, and where the value lives. Free of file paths, class names, and framework jargon. |
| `TECHNICAL_DOMAIN_GUIDE.md` | Consultants and developers about to touch the code | Where the domain lives in the tree, which modules own which concepts, which invariants must not be broken, with `path:line` evidence for every claim. |
| `docs/domains/<context>.md` *(when the domain spans several bounded contexts)* | Same audiences, scoped to one bounded context | Same questions, narrowed to one context. Cross-linked from both overview files so the document structure screams the domain. |

All documents describe only behavior observed in the repository. Inconsistencies, contradictory rules, naming mismatches, and unexpected behavior are recorded directly as findings with evidence; the skill does not ask a newcomer to decide what the system should do. The final section is reserved for information the repository genuinely does not establish, such as an unavailable external contract or undocumented rationale.

## Two analysis modes

The skill always runs in one of two modes, stated in every deliverable:

- **Complete context mode** — the default for a single service or a scoped area. Within the declared boundary, a coverage inventory of every business surface (routes, jobs, tables, screens, events, integrations, outputs…) must close fully before anything is written. A partial result is a failure, not a deliverable.
- **Repository atlas mode** — for whole-repo requests over large, legacy, or multi-context codebases. Produces a structural map of everything, full analysis of the prioritized contexts, and an explicit coverage matrix showing what is complete, partial, blocked, or out of scope. It never claims the whole business is covered.

The difference between the modes is the difference between "no known gaps inside this boundary" and "an honest map of what is known and what is not" — the skill never blurs the two.

## How it works

The skill follows a phased workflow (0 through 6, with the coverage inventory at Phase 1b, the coverage gate at Phase 3b, and output verification at Phase 6b).

0. **Frame the search** — scope, analysis mode, repo shape, prior context, discovery budget.
1. **Cheap recon** — directory shape, READMEs, manifests, data model, entry points. High signal per token.
1b. **Coverage inventory** — enumerate every surface where business behavior can live, per context, with a status per surface. This is the denominator of completeness.
2. **Locate the domain core** — rank candidate modules by vocabulary match, import centrality, branching density, test coverage, and churn. All inventoried modules with non-trivial business logic are ranked, not a fixed slice.
3. **Harvest the rules** — invariants, lifecycles, policies and calculations, permissions and visibility, and every inventoried operation traced end to end. Ends with the coverage gate (Phase 3b) before assembly.
3b. **Coverage gate** — fourteen categories (concepts, actors, processes, lifecycles, invariants, calculations, time, integrations, configuration, outputs, audit, ownership, terminology, missing information) closed against the inventory.
4. **Assemble the model** — concept map, lifecycles, full process catalog plus highlighted value journeys, glossary, cross-context reconciliation.
5. **Value and gaps** — where the observable value lives, with typed claims; surface what the code cannot answer.
6. **Write the documents** — fill the templates, calibrate register per audience, cross-link per-context files when the domain has several bounded contexts.
6b. **Output verification** — every ledger finding consumed, every reference valid, no placeholders, registers clean, coverage matrix consistent.

## Operating principles

- **Observed behavior only.** The skill documents what the code does, not what it appears intended to do. Inconsistencies and competing implementations are findings, not questions for the newcomer. Code present is not code running: config-dependent, inactive, test-only, and unreachable behavior is labelled as such.
- **Evidence over assumption.** Every non-obvious claim in the technical guide carries a `path/to/file.ext:line` reference, and every claim is typed (observed, documented, synthesis, hypothesis, missing-evidence). Unsupported claims are omitted; genuinely missing information is recorded as absent from the repository.
- **Complete means accounted for.** A surface is covered when it is modelled, confirmed absent after searching, or explicitly declared partial/blocked/out-of-scope — never when it was simply never searched. The coverage inventory is the denominator; both gates check closure against it.
- **Write as you go.** Findings are appended to a scratch ledger (`.tell-me-the-domain/notes.md`) as they are made, so an interrupted run still leaves a trail. The ledger is deleted only after a closed complete-context run; in atlas mode it is kept so the next pass can continue.
- **Depth beats brevity — in the deliverable.** Each main concept is developed in depth — definition, attributes, relationships, processes, and why a newcomer must understand it — not reduced to a one-liner. File length matches what the domain requires, not a target. Exploration depth is governed separately by `references/token-discipline.md` and stays bounded.
- **Coverage gate before writing, output verification after.** Before assembly, fourteen coverage categories must close against the inventory. After writing, references, registers, links, and the coverage matrix are verified before delivery.
- **Complexity firewalls.** Large or legacy repositories are mapped before deep reading, partitioned by business boundary, explored under an explicit budget, and reported with a coverage matrix instead of confident guesses.
- **Name things the way the business names them.** A mismatch between code naming and business naming is itself a finding, and the glossary is where a newcomer gets unstuck fastest.

## Repository contents

```
tell-me-the-domain/
├── AGENTS.md                                    # Project-level agent instructions (registers the skill)
├── README.md                                    # This file
├── evals/                                       # Evaluation harness: oracle schemas, synthetic cases, deterministic checks
└── skills/tell-me-the-domain/
    ├── SKILL.md                                 # The skill definition (frontmatter + workflow)
    ├── assets/
    │   └── templates/
    │       ├── BUSINESS_OVERVIEW.template.md    # Output template for the business-side document
    │       ├── TECHNICAL_DOMAIN_GUIDE.template.md # Output template for the developer-side document
    │       └── BOUNDED_CONTEXT.template.md      # Output template for one bounded context (when the domain spans several)
    └── references/
        ├── workflow.md                          # Phases 0–6b in detail (includes coverage inventory, gate, and output verification)
        ├── evidence-ledger.md                   # Claim types, finding schema, and coverage inventory format
        ├── complexity-firewall.md               # Budget and partitioning for large repos (atlas mode)
        ├── token-discipline.md                  # Exploration cost control
        └── evidence-map.md                      # Where domain signals hide, by artifact type
```

## Usage

This skill is intended to be loaded by an agent that supports the opencode skill format. Once loaded, invoke it on any codebase where the business is unclear — inherited code, legacy systems, third-party repositories, or a monorepo whose bounded contexts you do not yet know. The skill will:

1. Explore the codebase following the phases above, in the analysis mode that matches the scope.
2. Build the coverage inventory (Phase 1b) before any deep reading, and persist findings to `.tell-me-the-domain/notes.md` as it goes.
3. Pass the coverage gate (Phase 3b) against the inventory before any writing.
4. Write `BUSINESS_OVERVIEW.md` and `TECHNICAL_DOMAIN_GUIDE.md` into `docs/` (or the repository root if no `docs/` folder exists).
5. When the domain spans several bounded contexts, also write `docs/domains/<context>.md` — one per context — and link them from both overview files.
6. Verify the output (Phase 6b): references valid, registers clean, coverage matrix consistent.
7. Report up to three observed findings that would most surprise a newcomer (hard cap). Mention missing information only when the repository genuinely cannot establish it; never ask the newcomer to reconcile code inconsistencies.

## When to use it

The activation conditions that decide whether this skill fires live in `SKILL.md` § Activation Contract — single source of truth, not duplicated here.

## Conventions

- Document register is split by audience. The business document and per-context documents use business language; the technical document uses code-adjacent language with references.
- All documents state, near the top, the commit or date they were generated from. Domain docs rot, and a reader deserves to know how much to trust them.
- Per-context files share the business document's depth expectation and link to the overview files in both directions.
- The scratch ledger is deleted only after a closed complete-context run, unless the user asks to keep it; in atlas mode it is kept so the next pass can continue from the coverage matrix.
- Discoverability is bounded by the rules in `references/complexity-firewall.md`; output depth is bounded by what the domain requires, not by a target.

## References

- `skills/tell-me-the-domain/SKILL.md` — full skill definition (frontmatter + workflow).
- `skills/tell-me-the-domain/references/workflow.md` — phases 0–6b in detail (coverage inventory, coverage gate, output verification).
- `skills/tell-me-the-domain/references/evidence-ledger.md` — claim types, finding schema, and coverage inventory format.
- `skills/tell-me-the-domain/references/complexity-firewall.md` — budget and partitioning for large repos (atlas mode).
- `skills/tell-me-the-domain/references/token-discipline.md` — exploration cost control (governs exploration depth; "depth beats brevity" applies to deliverables only).
- `skills/tell-me-the-domain/references/evidence-map.md` — search patterns per artifact type and ecosystem.
- `skills/tell-me-the-domain/assets/templates/BUSINESS_OVERVIEW.template.md` — structure for the business-side output.
- `skills/tell-me-the-domain/assets/templates/TECHNICAL_DOMAIN_GUIDE.template.md` — structure for the developer-side output.
- `skills/tell-me-the-domain/assets/templates/BOUNDED_CONTEXT.template.md` — structure for one bounded context (when the domain spans several).
