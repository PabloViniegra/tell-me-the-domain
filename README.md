# tell-me-the-domain

[![skills.sh](https://skills.sh/b/PabloViniegra/tell-me-the-domain)](https://skills.sh/PabloViniegra/tell-me-the-domain)

A reusable agent skill for reconstructing the business domain of an unfamiliar codebase. It reads the repository as the only source of truth that never lies about what the system *does*, and turns it into two documents a newcomer can actually use.

## Install

```
npx skills add PabloViniegra/tell-me-the-domain
```

## What it does

Given a codebase, the skill produces two structured documents alongside the project source:

| Document | Audience | Purpose |
|---|---|---|
| `BUSINESS_OVERVIEW.md` | Product owners, analysts, new joiners from the business side | What the product does, for whom, what rules govern it, and where the value lives. Free of file paths, class names, and framework jargon. |
| `TECHNICAL_DOMAIN_GUIDE.md` | Consultants and developers about to touch the code | Where the domain lives in the tree, which modules own which concepts, which invariants must not be broken, with `path:line` evidence for every claim. |

Both documents end with an *open questions* section addressed to a person who would know — the newcomer's agenda for their first week.

## How it works

The skill follows a seven-phase workflow:

1. **Frame the search** — establish scope, repo shape, and any prior context.
2. **Cheap recon** — directory shape, READMEs, manifests, data model, entry points. High signal per token.
3. **Locate the domain core** — rank candidate modules by vocabulary match, import centrality, branching density, test coverage, and churn.
4. **Harvest the rules** — invariants, lifecycles, policies and calculations, permissions and visibility.
5. **Assemble the model** — concept map, lifecycles, primary flows, glossary.
6. **Value and gaps** — state where the value lives; surface what the code cannot answer.
7. **Write the documents** — fill the templates, calibrate register per audience, mark evidence.

## Operating principles

- **Evidence over assumption.** Every non-obvious claim in the technical guide carries a `path/to/file.ext:line` reference. Claims without backing go to the open questions.
- **Observed versus inferred.** Assertions drawn from code are stated as fact. Reasonable guesses are hedged with "appears to" or "suggests" and rerouted to the open questions.
- **Write as you go.** Findings are appended to a scratch file (`.tell-me-the-domain/notes.md`) as they are made, so an interrupted run still leaves a trail.
- **Complexity firewalls.** Large or legacy repositories are mapped before deep reading, partitioned by business boundary, explored under an explicit budget, and reported with coverage limits instead of confident guesses.
- **Name things the way the business names them.** A mismatch between code naming and business naming is itself a finding, and the glossary is where a newcomer gets unstuck fastest.

## Repository contents

```
tell-me-the-domain/
├── AGENTS.md                                    # Project-level agent instructions (registers the skill)
├── README.md                                    # This file
└── skills/tell-me-the-domain/
    ├── SKILL.md                                 # The skill definition (frontmatter + workflow)
    ├── assets/
    │   └── templates/
    │       ├── BUSINESS_OVERVIEW.template.md    # Output template for the business-side document
    │       └── TECHNICAL_DOMAIN_GUIDE.template.md # Output template for the developer-side document
    └── references/
        ├── workflow.md                          # Phases 0–6 in detail
        ├── complexity-firewall.md               # Budget and stop conditions for large repos
        ├── token-discipline.md                  # Exploration cost control
        └── evidence-map.md                      # Where domain signals hide, by artifact type
```

## Usage

This skill is intended to be loaded by an agent that supports the opencode skill format. Once loaded, invoke it on any codebase where the business is unclear — inherited code, legacy systems, third-party repositories, or a monorepo whose bounded contexts you do not yet know. The skill will:

1. Explore the codebase following the phases above.
2. Persist findings to `.tell-me-the-domain/notes.md` as it goes.
3. Write `BUSINESS_OVERVIEW.md` and `TECHNICAL_DOMAIN_GUIDE.md` into `docs/` (or the repository root if no `docs/` folder exists).
4. Report the two or three findings that would most surprise a newcomer, plus the open questions that most need a human answer.

## When to use it

Use this skill whenever someone:

- Joins a project whose business they do not understand.
- Inherits legacy or third-party code.
- Asks "what does this system actually do", "what are the business rules here", "help me onboard onto this repo", "document the domain".
- Needs to explain a codebase to non-technical stakeholders.

Trigger it even when the request only mentions understanding, onboarding, or documenting business logic without naming the output files.

## Conventions

- Document register is split by audience. The business document uses business language; the technical document uses code-adjacent language with references.
- Both documents state, near the top, the commit or date they were generated from. Domain docs rot, and a reader deserves to know how much to trust them.
- The scratch file is deleted at the end of a successful run unless the user asks to keep it.

## References

- `skills/tell-me-the-domain/SKILL.md` — full skill definition (frontmatter + workflow).
- `skills/tell-me-the-domain/references/workflow.md` — phases 0–6 in detail.
- `skills/tell-me-the-domain/references/complexity-firewall.md` — budget and stop conditions for large repos.
- `skills/tell-me-the-domain/references/token-discipline.md` — exploration cost control.
- `skills/tell-me-the-domain/references/evidence-map.md` — search patterns per artifact type and ecosystem.
- `skills/tell-me-the-domain/assets/templates/BUSINESS_OVERVIEW.template.md` — structure for the business-side output.
- `skills/tell-me-the-domain/assets/templates/TECHNICAL_DOMAIN_GUIDE.template.md` — structure for the developer-side output.
