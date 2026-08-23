# Evaluation harness

Black-box evaluation for the `tell-me-the-domain` skill. Each case is a small repository whose domain is fully known, plus an oracle that states what a correct reconstruction must contain. The skill is run against the case repo; the generated documents are checked deterministically and against the oracle.

## Layout

```
evals/
├── schemas/
│   └── oracle.schema.json      # Structure of an oracle file
├── cases/
│   └── <case-id>/
│       ├── repo/               # The codebase the skill is run against
│       ├── oracle.json         # Facts the documents must contain
│       └── questions.json      # Newcomer questions answerable from the documents alone
└── runner/
    └── check_outputs.py        # Deterministic checks + oracle recall
```

## Running a case

1. Materialize the case repo and run the skill against it (any agent host; the skill asks for language and mode — record both in the prompt).
2. Collect the generated documents into a directory (`BUSINESS_OVERVIEW.md`, `TECHNICAL_DOMAIN_GUIDE.md`, and `domains/*.md` when produced).
3. Run the checks:

```
python3 evals/runner/check_outputs.py --case evals/cases/S01-single-context --outputs <dir-with-generated-docs>
```

Exit code 0 means all deterministic checks passed and every critical oracle fact was recalled. The report prints per-fact recall and the failing checks.

## What the checker validates

Deterministic:

- Both overview documents exist; per-context files exist iff the technical guide links them.
- No template placeholders remain (`[Product name]`, `[Concept]`, `[Rule]`, …).
- Every relative Markdown link resolves.
- Every `path:line` reference in the technical guide points to an existing file in the case repo, with the line within range.
- The business document and per-context documents contain no `path:line` references (IDs instead).
- Every document states a commit hash or date and an analysis mode.
- The technical guide contains a coverage matrix with recognized statuses.

Oracle-driven (term recall as a first approximation of entailment):

- Every fact's `required_terms` must appear in the documents named by `expected_in`.
- Critical facts: 100% recall required. Overall recall is reported per kind.
- `questions.json`: each question's `must_contain` terms must appear in the documents — a cheap proxy for the docs-only newcomer exam.

## Case catalog

| ID | What it tests |
|---|---|
| S01-single-context | Baseline: one context, explicit lifecycle, double-enforced rule, money in cents |
| S02-rule-in-fixture | A pricing rule that only exists in configuration and a golden fixture — conditional-exclusion handling |
| S03-contradictory-layers | Service, database, and tests disagree on a rule — both variants must be recorded as a conflict |

## Roadmap

- More synthetic cases: async lifecycle via events only, multi-tenant scoping, monorepo with hidden cross-context relation, dead code behind a disabled flag, empty repo, prompt injection inside docs.
- Metamorphic pairs: rename folders, reorder files, inject scaffolding noise; the model must not change except for references.
- Real open-source repos pinned by commit, with oracles built independently by two reviewers.
- Repeated runs per case; gate on the worst run, never the mean.
