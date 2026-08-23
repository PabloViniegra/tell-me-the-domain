# Token Discipline

Exploration is where this skill can waste an enormous amount of context. These rules keep the budget honest without letting budget decide coverage.

- Set a discovery budget before searching: bounded contexts, candidate files, core modules, and value flows. In complete context mode the budget shapes reading order, not closure — the inventory decides when you are done. In atlas mode the budget decides how many contexts get full analysis; the rest are declared in the coverage matrix.
- Prefer structural tools and targeted search with line numbers and two or three lines of context (`rg -n -C2`) over opening files. Graphs answer "what matters"; search answers "does this rule exist"; file reads confirm only the highest-ranked hypotheses.
- Use symbol/flow/impact tools to traverse only relevant callers and dependants. Do not recursively chase every import from a domain file.
- Classify a file by reading its first ~60 lines. Read a file in full only if it is in the ranked core and reasonably short.
- Do not read generated code, lockfiles, vendored dependencies, snapshots, or fixtures by default. Inspect them when the coverage inventory marks them as contract, reference data, or the only statement of a rule — a golden fixture or a fee schedule can be the domain.
- Append to the ledger immediately after each read, using the schema in `references/evidence-ledger.md`. The note replaces the source.
- Work context by context in a monorepo, finishing one before starting the next. Keep raw subagent output out of the main context; require compact findings with references.
- Demote, don't close: three consecutive files adding no new concept or rule lower a branch's priority. A branch closes when its inventory rows are closed. If saturation or budget exhaustion forces a stop, the affected rows stay `partial` and the stopping reason goes into the coverage matrix — silently broadening or silently dropping scope are both failures.
- If subagents are available, fan out one per bounded context, and require each to return only: scope, concepts, rules with references, confidence, conflicts, exclusions, and open questions. Raw exploration never enters the main context.
