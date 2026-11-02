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
│       ├── questions.json      # Newcomer questions answerable from the documents alone
│       └── prompt.txt          # Optional per-case agent prompt (must not hint at the answer)
├── ci/
│   ├── run_agent.py            # Default OpenCode wrapper for the case agent
│   └── run_judge.py            # Default OpenCode wrapper for the entailment judge
└── runner/
    ├── check_outputs.py        # Structural checks + oracle scoring
    ├── run_case.py              # Materialize, invoke an agent, then check one case
    ├── run_all.py               # Run every case and gate on the worst result
    └── process_utils.py        # Timeout cleanup for agent and judge processes
```

## Running a case

1. Materialize the case repo and run the skill against it (any agent host; the skill asks for language and mode — record both in the prompt).
2. Collect the generated documents into a directory (`BUSINESS_OVERVIEW.md`, `TECHNICAL_DOMAIN_GUIDE.md`, and `domains/*.md` when produced).
3. Run the checks:

```
python3 evals/runner/check_outputs.py --case evals/cases/S01-single-context --outputs <dir-with-generated-docs>
```

Without `--judge-cmd`, the standalone checker uses required-term recall as a local fallback. `run_all.py` requires the entailment judge so the CI gate never silently falls back to term recall:

```
python3 evals/runner/run_all.py \
  --output-root /tmp/tmtd-evals \
  --agent-cmd 'python3 evals/ci/run_agent.py' \
  --judge-cmd 'python3 evals/ci/run_judge.py'
```

`evals/ci/run_agent.py` and `evals/ci/run_judge.py` are the default wrappers. They call `opencode run --auto` with `opencode/deepseek-v4.1-flash-free` unless `TMTD_AGENT_MODEL` / `TMTD_JUDGE_MODEL` override it; free model names change often, so check `opencode models` when a run fails to start. The agent wrapper copies `skills/tell-me-the-domain` from the candidate checkout to a temporary directory and points the agent at it, because installed copies of the skill may be stale. Set `TMTD_SKILL_DIR` to evaluate a skill from another checkout; the PR workflow sets it to the candidate, since the wrapper itself comes from the base revision. It answers the language question (English) and adds nothing else: no output-format coaching. The agent runs inside the case repository and cannot see the oracles. The judge runs in an empty temporary directory. The agent command receives `$TMTD_PROMPT`, `$TMTD_REPO`, and `$TMTD_OUTPUT_DIR`. The judge command receives one JSON request on stdin and must return one JSON object with one result per oracle fact:

```
{"facts":[{"id":"R-001","entailed":true,"score":0.93,"reason":"The document states the rule and cites its source span."}]}
```

The default acceptance threshold is `0.80`; use `--judge-threshold` to change it. Critical facts must be entailed. `run_all.py` runs every case, continues after failures, enforces per-agent, judge, and case timeouts, and exits with the worst exit code rather than averaging runs.

If a case contains `prompt.txt`, `run_case.py` uses it instead of the default wording, substituting `{repo}` and `{output}`; the generated prompt is saved in the run directory. Prompts and case READMEs must read like a real user request: never name the trap under test or the expected answer.

`run_case.py` materializes each case in a neutrally named temporary sandbox (the case ID names the trap, so it never appears in the agent's paths), then copies the documents and any kept ledger into the run directory. If the analyzed repository changed in any way other than the scratch ledger — edited files, generated caches from executing code, documents written into the repo — the case fails, and the repository's final state is kept in `analyzed-repo/` inside the run directory.

The GitHub workflow always runs the runner contract tests. The black-box job defaults to the wrappers above, one repeat, and 480s agent timeout. It still needs a provider credential as a repository secret (`OPENCODE_API_KEY` or `ANTHROPIC_API_KEY`) if the default free model is unavailable on the runner. It uploads generated overview documents only for manual runs, not pull requests.

On pull requests, the black-box runner and its oracle cases come from the base revision while the candidate checkout is the agent's working directory. This keeps a change from rewriting the evaluator and its release gate; new cases begin gating after they land on the base branch.

The workflow has a one-time bootstrap fallback for the PR that first introduces the evaluator; later PRs always use the base-revision runner.

The configured agent and judge commands are trusted executables, not a sandbox boundary. Run them on an isolated evaluator job; the runner removes GitHub and runner metadata from their environment but cannot safely hide provider credentials that the configured commands require.

## What the checker validates

Deterministic:

- Both overview documents exist; per-context files exist iff the technical guide links them.
- No template placeholders remain (`[Product name]`, `[Concept]`, `[Rule]`, …).
- Every relative Markdown link resolves.
- Every `path:line` reference in the technical guide points to an existing file in the case repo, with the line within range.
- The business document and per-context documents contain no `path:line` references (IDs instead).
- Every document states a commit hash or date and an analysis mode.
- The technical guide contains a coverage matrix with recognized statuses.

Oracle-driven:

- With a judge, every fact is scored for entailment against its source spans and the generated documents. Critical facts must meet the threshold.
- Without a judge, every fact's `required_terms` must appear in the documents named by `expected_in`; this is a compatibility fallback, not the release gate.
- `questions.json`: each question's `must_contain` terms must appear in the documents — a cheap proxy for the docs-only newcomer exam.
- `forbidden_output_terms`, when present in an oracle, must not appear in any generated document.

## Case catalog

| ID | What it tests |
|---|---|
| S01-single-context | Baseline: one context, explicit lifecycle, double-enforced rule, money in cents |
| S02-rule-in-fixture | A pricing rule that only exists in configuration and a golden fixture — conditional-exclusion handling |
| S03-contradictory-layers | Service, database, and tests disagree on a rule — both variants must be recorded as a conflict |
| S04-async-events-only | Lifecycle encoded only in past-tense events with no status column |
| S05-multi-tenant-scoping | Tenant isolation implicit in the `WHERE` clause; an `unsafe` variant must be flagged |
| S06-cross-context-bus | Two services share events without an explicit contract |
| S07-disabled-feature-flag | Code exists behind a feature flag disabled in shipped configuration |
| S08-empty-repo | No domain artifacts are present; write both overview documents as an absence report and do not invent a product |
| S09-prompt-injection | Repository documentation contains instructions that must be treated as untrusted content |

## Roadmap

- More synthetic cases: monorepo with hidden cross-context relation, metamorphic repository noise, and real open-source repos pinned by commit.
- Metamorphic pairs: rename folders, reorder files, inject scaffolding noise; the model must not change except for references.
- Real open-source repos pinned by commit, with oracles built independently by two reviewers.
- Repeated runs per case; gate on the worst run, never the mean.
