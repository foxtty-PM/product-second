---
schema_version: 4.2.0
artifact_id: TO_FILL
artifact_type: gate
revision: 1
status: draft
approved_revision: null
input_manifest: []
signal_refs: []
---

# gate
## Required content
Gate/idea/revision/route; task/artifact/reviewer/input checks/no blockers/budget; options/consequences; Owner exact quote/date/conditions; real external action separate exact-payload approval. Each decided gate goes to idea gate_log through tools/backlog.py apply: approved/changes_requested/rejected need quote and decided_by, not_applicable a reason, inherited a parent decision reference; a joint decision records every gate.
## Readiness check
Apply tasks/README.md: gate criterion -> relevant task -> completion record/result_ref -> current evidence/review -> verdict or gap. Check blockers, remaining work and dropped exclusions. Taskless work requires a reason and equivalent evidence; done does not approve a gate.
After the Owner decision, update next-gate work in the dossier with task links, owners and dependencies. Reuse it across statuses; new work follows normal approval.
## Signals
Relevant SIG IDs in signal_refs; verify source evidence, never copy CSV as a second registry.
