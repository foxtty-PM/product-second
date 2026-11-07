# inbox-sweep
Version4.2.0. Role agents/coordinator.md; template templates/inbox-digest.md.
## Context/inputs
AGENTS.md, KNOWLEDGE_MAP.md; relevant domain/feature/idea/task; signals/signals.csv + signals/README.md when relevant. Goal, IDs/revisions/hashes, source ACL, applicability/risk, output format, tools/path boundaries, acceptance, budget.
## Steps
Allowlist/pagination/cursor/dedup; meaningful signals→CSV via lock/CAS; capture before cursor commit.

### Scheduled draft mode
Schedules in [loop settings](../profile/loops.yaml) require the first pilot described in [onboarding](../profile/loops.md). Access allowlisted sources only within current rights. Initial automation returns candidates with source refs, gaps, and coverage; it does not capture/update CSV or advance source cursors. Reference existing signals by SIG ID without copying rows. A new scheduled report is not capture success. The coordinator can separately apply reviewed candidates through tools/signals.py CAS/lock. Missing access or allowlist means blocked, not no new signals.
## Postconditions/outputs
Applicable versioned artifact, source evidence, signal_refs IDs (not copied rows), explicit gaps, checkpoint, short summary. Independent reviewer for applicable risk. No double state or planned/current confusion.
## Side effects/idempotency
Local permitted draft/proposed patch. Coordinator alone mutates CSV through tools/signals.py CAS+lock; others submit candidates. Signals do not automatically create task/backlog/verified fact. External writes OFF. Read-only cannot be bypassed.
## Stop/failure
Missing evidence/access, invalid schema, conflict, budget/policy, unknown external result→stop+checkpoint+failure classification. Safe bounded retry only. Do not invent successful writes, model availability or evidence.
