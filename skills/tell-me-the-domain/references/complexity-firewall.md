# Complexity Firewall

Mandatory for large or legacy repositories. Treat repository size, coupling, and uncertainty as signals to narrow scope, not invitations to read more.

## Before deep exploration

1. **Map before opening files.** Use available AST/import/call-graph, symbol, impact-analysis, and code-search tools. If a tool is unavailable or incomplete, record that limitation and use directory shape, manifests, routes, schemas, tests, and git history as fallbacks.
2. **Partition by business boundary.** In a monorepo or tangled legacy system, identify deployables, bounded contexts, data ownership, queues, and external integrations. Work one context at a time. Do not merge subagent findings until each has compact evidence and uncertainty.
3. **Prioritize hotspots.** Rank files by domain vocabulary, fan-in, branching/decision density, test coverage, churn, and proximity to data or integration boundaries. Use impact analysis before following a dependency chain.
4. **Cap exploration, expand coverage.** Start with 10–20 candidates and rank ALL modules with non-trivial business logic — typically 3–7 in a small service with one bounded context, but 15–25 or more in a monorepo with several. Read only enough to confirm or reject a hypothesis. After three consecutive files add no new concept or rule, stop that branch. Cap each branch to its evidence; cover the whole business, not a slice of it.
5. **Keep an evidence ledger.** Every finding records `observed | missing-evidence`, `path:line`, confidence, and the next documentation action. Never promote an inference to a rule merely because multiple layers repeat it.
6. **Do not escalate code inconsistencies.** If context boundaries, business scope, or rules conflict, record each observed behavior, its evidence, and the conflict in the documents. Ask the user only when the repository does not contain enough information to define the requested scope and proceeding would make the documents misleading.
7. **Protect context and the repository.** Never read generated code, lockfiles, vendored code, snapshots, fixtures, or whole large files. Use targeted searches and bounded slices. Only write the scratch file and requested domain documents; never change product source.

## Coverage statement

When complexity is high, the deliverable must say what was covered, what was intentionally sampled or excluded, which tools were unavailable, and how a second pass should continue. A partial, traceable model is safer than a confident full-repo fiction.

This firewall narrows scope during exploration. The depth and completeness of the deliverable are then checked at the coverage gate — see `workflow.md` § "Phase 3b — Coverage gate (mandatory before assembly)" for the pre-write checklist.
