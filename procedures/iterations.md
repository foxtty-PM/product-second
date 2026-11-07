# iterations
Version4.2.0. Role agents/product-writer.md; template templates/iterations.md.
## Context/inputs
AGENTS.md, KNOWLEDGE_MAP.md; relevant domain/feature/idea/task; signals/signals.csv + signals/README.md when relevant. Goal, IDs/revisions/hashes, source ACL, applicability/risk, output format, tools/path boundaries, acceptance, budget.
## Steps
Thin slices/leading/appetite/dependencies; parent/child links not duplicate feature.
## Postconditions/outputs
Applicable versioned artifact, source evidence, signal_refs IDs (not copied rows), explicit gaps, checkpoint, short summary. Independent reviewer for applicable risk. No double state or planned/current confusion.
## Side effects/idempotency
Local permitted draft/proposed patch. Coordinator alone mutates CSV through tools/signals.py CAS+lock; others submit candidates. Signals do not automatically create task/backlog/verified fact. External writes OFF. Read-only cannot be bypassed.
## Stop/failure
Missing evidence/access, invalid schema, conflict, budget/policy, unknown external result→stop+checkpoint+failure classification. Safe bounded retry only. Do not invent successful writes, model availability or evidence.

## Product backlog updates
Send changes to canonical dossiers, tasks, results, priorities, parentage, blockers, and each gate decision to the coordinator as a revision/hash delta. The coordinator uses the permitted tools/backlog.py writer; if the CLI is denied, prepare an operator payload. After actual writes, tools/build_indices.py synchronizes backlog/backlog.csv and backlog/VIEW.md; tools/check_package.py checks freshness. Record sync failures in the checkpoint. Do not claim the table is current without fresh=true; task/document updates never change stage.
G7: next_iteration → next planned iteration; adjust_plan → new parent G3; stop → block future iterations; close → no automatic next iteration. The parent waits for children to close. Never replace iteration_of with spawned_from.
