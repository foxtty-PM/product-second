# Context map for all agents
Bootstrap: AGENTS.md → agents/<role>.md → this map → profile/INDEX.md → the relevant index/node. Do not read the entire SPEC, reference archive, or CSV without a need.
- Domain/process/rules: knowledge/domains/INDEX.md.
- Current features: knowledge/product/features/INDEX.md; overall map: knowledge/product/INDEX.md.
- UX/technical context: product/interfaces/, systems/, integrations/.
- Metrics/events: knowledge/metrics/INDEX.md, knowledge/event-schema.md.
- Decisions: knowledge/decisions/INDEX.md. Evidence: knowledge/sources/INDEX.md.
- Initiatives/children: ideas/INDEX.md. Tasks: tasks/INDEX.md. Product backlog: backlog/VIEW.md, backlog/backlog.csv; contract: backlog/README.md. Deferred references: backlog/INDEX.md.
- Workflow rules: workflows/routes.json, gates.json, task-transitions.json, applicability.json; budgets/models: policy/budgets.json, policy/model-registry.json. Read before changing status, selecting modules, or choosing a budget/model_profile; check_package validates consistency with schemas.
- Task execution: tasks/README.md — selective planning, completion evidence and nearest-gate readiness.
- Signals: signals/signals.csv; contract: signals/README.md. For a feature/idea, filter related_ids by exact ID first, then load summary/context/source_ref for relevant rows. For incoming signals, use status=new. Resolve SIG through the generated registry to a CSV row, never a Markdown path.

## Search
Exact ID/metadata → full text → graph neighbors → primary source. Related signals are evidence candidates, not automatically knowledge. Query logs record scope/method/hits/gaps/stop reason. not_found_within_budget does not mean absent. Check the source for consequential, stale, or disputed claims. DEMO and reference are excluded by default.

## Writes
Executors propose signal candidates; only the coordinator writes CSV through tools/signals.py with expected_hash. No parallel manual/Excel edits. The keeper does not write signals: save only evidence-backed knowledge after permission. Other roles, including the coordinator for decisions and researcher for sources, write candidates under knowledge/_drafts/; drafts are not nodes and do not enter the registry or search. Card.signal_refs does not duplicate rows.
Indexes, graph, and ID registry are generated, not a second state. build_indices includes SIG IDs and typed signal links. Source links do not expand data access rights.
