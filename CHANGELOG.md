# Changelog

All notable changes to this skill are documented here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.1] — 2026-11-10

### Fixed
- The S03 oracle no longer expects the refund concept to mention a "previously
  processed payment", which the case repository never establishes.
- Template and reference examples no longer reuse the vocabulary, file paths,
  and rules of eval cases S01–S04 (claims, insurer fee files, refund windows,
  `OrderShipped`); they use a fictional marina domain instead, so copying an
  example can no longer satisfy an oracle.
- The S01 oracle no longer claims that claims are identified by
  `(hospital_id, insurer_ref)`; the repository only makes both fields mandatory.
- Output verification allows the requested documents in the analyzed repository,
  matching the default `docs/` output location.
- Phase 5 no longer turns dead or ambiguous code into questions for the reader.
- A complete-context run that cannot close its inventory switches to atlas mode
  and says so, instead of having no defined outcome.
- Surprise sections may list fewer than three findings, and the technical guide's
  permission table uses `R-` IDs for permissions and `A-` IDs for actors.
- The output checker reads placeholders from the skill templates and matches
  them outside inline code (so `[...]` in a JSON snippet is not a placeholder),
  accepts `path:line:col` and validates `path:start-end`, ignores nested bullets
  in the surprise cap, enforces surprise order, requires every ID referenced by
  the business overview or per-context files to appear in the technical guide
  (even when the guide defines none; the header's ID legend counts on neither
  side), accepts written-out dates such as "10 November 2026", checks date and
  mode in per-context files, and resolves their relative links from `domains/`.
- The S02 oracle no longer claims pricing applies the configured `half_up` rule;
  the engine never reads that key and uses Python's `round` (ties to even).
- Divergent rules must name every layer involved, including which value the
  tests assert.
- The S06 oracle no longer claims billing publishes `InvoicePaid`; the bus is
  declared but never used, and only the test hands the event to the handler.
- The S05 oracle no longer expects the guide to say `list_tickets_unsafe` "must
  not be used"; the skill records behavior and never prescribes corrections.
- Instruction-like repository content is named plainly as untrusted content and a
  prompt-injection attempt, not only described.

## [1.2.0] — 2026-11-02

### Fixed
- Black-box evals no longer leak answers to the agent: case READMEs stop announcing
  the fixture and its expected answer, per-case focus hints and leaking `prompt.txt`
  files are gone, and the agent wrapper no longer injects output-format coaching.
- The agent runs inside a neutrally named sandbox of the case repository instead of
  the skill repository, so it can neither read the oracles nor see the case ID.
- The OpenCode wrappers work with current OpenCode (no `--dir` flag) and default to a
  model that exists; the agent loads the candidate skill instead of a stale installed copy.

### Changed
- Discovery is static: the skill never executes, builds, tests, or installs anything
  from the analyzed repository. Blind runs showed agents running untrusted repository
  code, including in the prompt-injection case.
- The language question is skipped when the request already names the language.
- Both overviews must list the same three surprises with identical headlines; the
  templates' examples now model that instead of contradicting it.
- Every ID used in any document, including `F-` missing facts, is defined in the
  technical guide.
- The frontmatter description names the deliverables and more trigger phrases.
- Repository instructions are explicitly treated as untrusted evidence, never agent commands.
- Language disclaimer is shown once; the run proceeds without a second confirmation.
- Empty repositories produce an absence report instead of stopping.
- The evidence ledger now names the same kinds and ID prefixes as the templates and eval oracles.

### Added
- `run_case.py` fails a case when the analyzed repository was modified (anything other
  than the scratch ledger), and keeps the ledger in the run directory for inspection.
- A per-PR evaluation workflow and `run_all.py`, which gates on the worst case result.
- Entailment-judge support with source spans, generated documents, scores, and reasons.
- Synthetic evaluation cases for disabled feature flags, empty repositories, and prompt injection.
- Optional per-case `prompt.txt` files and forbidden-output checks for evaluation oracles.
- `evals/ci/run_agent.py` and `evals/ci/run_judge.py` wrap `opencode run` for local and CI black-box evaluations.


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
