# weekly
Version4.2.0. Role agents/keeper.md; template templates/weekly.md.
## Context/inputs
AGENTS.md, KNOWLEDGE_MAP.md; relevant domain/feature/idea/task; signals/signals.csv + signals/README.md when relevant. Goal, IDs/revisions/hashes, source ACL, applicability/risk, output format, tools/path boundaries, acceptance, budget.
## Steps
Outcomes/cost/owner time/errors/freshness/revisit/signals unresolved; proposals not automatic dismiss.

### Scheduled draft mode
Schedules and pilots are defined in [loop settings](../profile/loops.yaml) and [onboarding](../profile/loops.md). Read current canonical dossiers; use backlog/VIEW.md only as a derived view and flag stale/missing evidence. Exclude DEMO. Produce a concise English draft: outcomes, active focus, blockers, important unprocessed SIG IDs, deferred questions, and Owner proposals with reasons/uncertainties. Do not change priorities, status/stage, signals, or knowledge; do not send messages. Empty real scope means `blocked_no_real_context`, not a successful pilot. Use previous reports for comparison, never as new canon or proof of completed work.
## Postconditions/outputs
Applicable versioned artifact, source evidence, signal_refs IDs (not copied rows), explicit gaps, checkpoint, short summary. Independent reviewer for applicable risk. No double state or planned/current confusion.
## Side effects/idempotency
Local permitted draft/proposed patch. Coordinator alone mutates CSV through tools/signals.py CAS+lock; others submit candidates. Signals do not automatically create task/backlog/verified fact. External writes OFF. Read-only cannot be bypassed.
## Stop/failure
Missing evidence/access, invalid schema, conflict, budget/policy, unknown external result→stop+checkpoint+failure classification. Safe bounded retry only. Do not invent successful writes, model availability or evidence.
