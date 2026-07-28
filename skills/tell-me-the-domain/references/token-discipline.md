# Token Discipline

Exploration is where this skill can waste an enormous amount of context. These rules keep the budget honest.

- Set a discovery budget before searching: bounded contexts, candidate files, core modules, and value flows. Expand it only when a new high-confidence finding justifies the cost.
- Prefer structural tools and targeted search with line numbers and two or three lines of context (`rg -n -C2`) over opening files. Graphs answer "what matters"; search answers "does this rule exist"; file reads confirm only the highest-ranked hypotheses.
- Use symbol/flow/impact tools to traverse only relevant callers and dependants. Do not recursively chase every import from a domain file.
- Classify a file by reading its first ~60 lines. Read a file in full only if it is in the ranked core and reasonably short.
- Never read generated code, lockfiles, vendored dependencies, snapshots, or fixtures. Sample large test suites by name only.
- Append to the notes file immediately after each read, including evidence type, confidence, and the next search. The note replaces the source.
- Work context by context in a monorepo, finishing one before starting the next. Keep raw subagent output out of the main context; require compact findings with references.
- Stop at saturation, budget exhaustion, or unresolved boundary ambiguity. Report the stopping reason instead of silently broadening scope.
- If three consecutive files add no new concept or rule, stop that branch. A newcomer needs both the complete map and enough terrain on each module to act — partial coverage leaves the mental model wrong. Match depth to the domain: skim nothing the business requires, saturate on the concepts that drive the value, and pass the coverage gate from `references/workflow.md` before writing.
- If subagents are available, fan out one per bounded context, and require each to return only: scope, concepts, rules with references, confidence, conflicts, exclusions, and open questions. Raw exploration never enters the main context.
