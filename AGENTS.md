# Agent instructions

## Conventions

- **No length limits.** When a file needs depth, write deeply — even if it gets long. Brevity is not a goal; depth is, when the project requires it.
- For markdown deliverables (notably `BUSINESS_OVERVIEW.md`), each business concept must be developed in depth: definition grounded in observed behavior, attributes and shape using the code's terminology, relationships with other concepts named specifically, the business processes it participates in end-to-end, and why a newcomer must understand it. A glossary of one-liners belongs at the end of the document; the "main concepts" section is where the model gets built.

## Skills

This project ships a reusable skill in `skills/tell-me-the-domain/`. Load it via the Skill tool when the task involves understanding, documenting, or onboarding to a codebase's business domain.

- `tell-me-the-domain` — reconstructs a codebase's business domain into `BUSINESS_OVERVIEW.md` and `TECHNICAL_DOMAIN_GUIDE.md`. Triggers: onboarding, business rules, document domain, legacy code, third-party code.
