# Changelog

All notable changes to this skill are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- A per-PR evaluation workflow and `run_all.py`, which gates on the worst case result.
- Entailment-judge support with source spans, generated documents, scores, and reasons.
- Synthetic evaluation cases for disabled feature flags, empty repositories, and prompt injection.
- Optional per-case `prompt.txt` files and forbidden-output checks for evaluation oracles.

### Changed
- Repository instructions are explicitly treated as untrusted evidence, never agent commands.

## [1.1.0] — 2026-08-24

### Changed
- Completeness is now a closure contract rather than an aspiration. The skill
  declares one of two analysis modes (complete context / repository atlas) and
  requires the coverage inventory to close before writing.
- The pre-write gate expanded from five categories to fourteen, covering
  concepts, processes, lifecycles, invariants, calculations, time, integrations,
  configuration, outputs, audit, ownership, terminology, and missing
  information.
- A new Phase 6b output verification gates placeholder removal, reference
  validity, register split, surprise parity, and bidirectional linking between
  overviews and per-context files.
- Findings now follow a typed-claim schema with independent axes for
  confidence, enforcement, consistency, runtime status, and coverage.
- Documents cross-reference rules and concepts by stable IDs; business
  documents contain no `path:line` references.
- Contradictions recorded with both variants as a `conflict` finding; findings
  never invented to fit a desired rule.
- Heuristic search signals (magic numbers, retention, hardcoded thresholds)
  labelled as hypotheses rather than facts.
- README and SKILL.md describe the code as evidence with limits, not an
  oracle that "never lies".

### Added
- `references/evidence-ledger.md` describes claim types, the finding schema,
  and the coverage inventory format.
- `evals/runner/check_outputs.py` is a deterministic checker implementing
  the structural half of Phase 6b plus oracle-driven recall.
- `evals/runner/run_case.py` materializes a case, invokes an agent through
  a pluggable command, and pipes the output into the checker.
- `evals/schemas/oracle.schema.json` declares the oracle fact schema,
  including the `audit`, `configuration`, and `conflict` kinds.
- `evals/cases/S01-single-context` — baseline claim service with double
  enforcement and money in cents.
- `evals/cases/S02-rule-in-fixture` — fee percentage lives in configuration
  and a golden fixture, exercising the conditional fixture policy.
- `evals/cases/S03-contradictory-layers` — service, DB, and tests disagree
  on a refund window; the skill must record both variants as a conflict.
- `evals/cases/S04-async-events-only` — lifecycle encoded only in past-tense
  events with no status column.
- `evals/cases/S05-multi-tenant-scoping` — tenant isolation implicit in the
  WHERE clause; an `unsafe` variant must be flagged.
- `evals/cases/S06-cross-context-bus` — two services share events without an
  explicit contract.

## [1.0.0] — 2026-07-27

First tagged release. Coverage gate, per-context files, depth-scoped output.
