# doc-scan
Version4.2.0. Role agents/researcher.md; template templates/knowledge-candidate.md.
## Context/inputs
AGENTS.md, KNOWLEDGE_MAP.md; relevant domain/feature/idea/task; signals/signals.csv + signals/README.md when relevant. Goal, IDs/revisions/hashes, source ACL, applicability/risk, output format, tools/path boundaries, acceptance, budget.
## Steps
Inventory/hash delta→knowledge candidates; source contradictions; signal candidates to coordinator.
## Postconditions/outputs
Applicable versioned artifact, source evidence, signal_refs IDs (not copied rows), explicit gaps, checkpoint, short summary. Independent reviewer for applicable risk. No double state or planned/current confusion.
## Side effects/idempotency
Local permitted draft/proposed patch. Coordinator alone mutates CSV through tools/signals.py CAS+lock; others submit candidates. Signals do not automatically create task/backlog/verified fact. External writes OFF. Read-only cannot be bypassed.
## Stop/failure
Missing evidence/access, invalid schema, conflict, budget/policy, unknown external result→stop+checkpoint+failure classification. Safe bounded retry only. Do not invent successful writes, model availability or evidence.
