# Complexity Firewall

Mandatory for large or legacy repositories. Treat repository size, coupling, and uncertainty as signals to narrow scope, not invitations to read more.

## Before deep exploration

1. **Map before opening files.** Use available AST/import/call-graph, symbol, impact-analysis, and code-search tools. If a tool is unavailable or incomplete, record that limitation and use directory shape, manifests, routes, schemas, tests, and git history as fallbacks.
2. **Partition by business boundary.** In a monorepo or tangled legacy system, identify deployables, bounded contexts, data ownership, queues, and external integrations. Work one context at a time. Do not merge subagent findings until each has compact evidence and uncertainty.
3. **Prioritize hotspots.** Rank files by domain vocabulary, fan-in, branching/decision density, test coverage, churn, and proximity to data or integration boundaries. Use impact analysis before following a dependency chain.
4. **Cap exploration.** Start with 10–20 candidates, 3–7 core modules, and 2–3 value flows. Read only enough to confirm or reject a hypothesis. After three consecutive files add no new concept or rule, stop that branch.
5. **Keep an evidence ledger.** Every finding records `observed | inferred | unknown`, `path:line`, confidence, and the next action. Never promote an inference to a rule merely because multiple layers repeat it.
6. **Escalate instead of guessing.** Stop and ask the user when context boundaries, business scope, or conflicting rules cannot be resolved cheaply. Otherwise isolate the ambiguity in open questions and continue without inventing rationale.
7. **Protect context and the repository.** Never read generated code, lockfiles, vendored code, snapshots, fixtures, or whole large files. Use targeted searches and bounded slices. Only write the scratch file and requested domain documents; never change product source.

## Coverage statement

When complexity is high, the deliverable must say what was covered, what was intentionally sampled or excluded, which tools were unavailable, and how a second pass should continue. A partial, traceable model is safer than a confident full-repo fiction.
