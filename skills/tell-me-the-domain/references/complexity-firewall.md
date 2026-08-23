# Complexity Firewall

Mandatory in repository atlas mode (large, legacy, or multi-context repos requested whole). Treat size, coupling, and uncertainty as signals to partition and prioritize — never as permission to skip the inventory.

## Before deep exploration

1. **Map before opening files.** Use available AST/import/call-graph, symbol, impact-analysis, and code-search tools. If a tool is unavailable or incomplete, record that limitation and use directory shape, manifests, routes, schemas, tests, and git history as fallbacks.
2. **Partition by business boundary.** Identify deployables, bounded contexts, data ownership, queues, and external integrations. A bounded context is a semantic boundary — its own vocabulary, its own authority over its data, translation at its edges — not a folder or a deployable. Work one context at a time. Do not merge subagent findings until each has compact evidence and uncertainty.
3. **Prioritize hotspots.** Rank files by domain vocabulary, fan-in, branching/decision density, test coverage, churn, and proximity to data or integration boundaries. Use impact analysis before following a dependency chain.
4. **Budget shapes reading order, never closure.** Start with 10–20 deep-read candidates per context, ranked from the coverage inventory. A branch closes when its inventory rows close, not when reading feels unproductive. Three consecutive files adding no new concept or rule demote a branch's priority; they do not close it — adapters and glue can hide the policy file behind them.
5. **Keep the evidence ledger.** Every finding follows the schema in `references/evidence-ledger.md`: claim type, evidence, confidence, enforcement, consistency, runtime status, next search. Never promote an inference to a rule merely because multiple layers repeat it.
6. **Do not escalate code inconsistencies.** Record each observed behavior, its evidence, and the conflict in the documents. Ask the user only when the repository does not contain enough information to define the requested scope and proceeding would make the documents misleading.
7. **Protect context and the repository.** Do not read generated code, lockfiles, vendored code, snapshots, or fixtures by default — inspect them when the inventory marks them as contract, reference data, or the only statement of a rule. Use targeted searches and bounded slices. Only write the scratch ledger and the requested domain documents; never change product source.

## Coverage statement

Atlas mode delivers a structural map of everything and full analysis of the prioritized contexts. The deliverable must show the coverage matrix — which contexts and surfaces are `complete`, `partial`, `blocked`, or `out-of-scope`, which tools were unavailable, and how a second pass should continue from the kept ledger. An atlas is honest by construction; it must never describe the whole business as covered.
