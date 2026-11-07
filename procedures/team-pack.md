# team-pack
Version4.2.0. Role agents/product-writer.md; template templates/dev-context.md.
## Context/inputs
AGENTS.md, KNOWLEDGE_MAP.md; relevant domain/feature/idea/task; signals/signals.csv + signals/README.md when relevant. Goal, IDs/revisions/hashes, source ACL, applicability/risk, output format, tools/path boundaries, acceptance, budget.
## Steps
Return existing ClickUp and development knowledge document links as {title, url} for clickup_docs/dev_knowledge_docs on the own dossier; the coordinator updates the card and regenerates backlog. Never invent an address when the document does not exist or its URL is unknown.
Sanitized self-contained pack with source hashes and signal_refs as needed; no sender.
## Postconditions/outputs
Applicable versioned artifact, source evidence, signal_refs IDs (not copied rows), explicit gaps, checkpoint, short summary. Independent reviewer for applicable risk. No double state or planned/current confusion.
## Side effects/idempotency
Local permitted draft/proposed patch. Coordinator alone mutates CSV through tools/signals.py CAS+lock; others submit candidates. Signals do not automatically create task/backlog/verified fact. External writes OFF. Read-only cannot be bypassed.
## Stop/failure
Missing evidence/access, invalid schema, conflict, budget/policy, unknown external result→stop+checkpoint+failure classification. Safe bounded retry only. Do not invent successful writes, model availability or evidence.
