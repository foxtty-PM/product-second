# brd
Version4.2.0. Role agents/product-writer.md; template templates/spec.md.
## Context/inputs
AGENTS.md, KNOWLEDGE_MAP.md; relevant domain/feature/idea/task; signals/signals.csv + signals/README.md when relevant. Goal, IDs/revisions/hashes, source ACL, applicability/risk, output format, tools/path boundaries, acceptance, budget.
## Steps
Scale/type/risk/modules; route S uses templates/s-mini.md instead of spec; RQ traceability; relevant SIG IDs in signal_refs, no raw row copy.

### Manual revision loop
Parameters: [loop settings](../profile/loops.yaml). Selecting the workflow does not permit a run without a specific document.
1. The coordinator records the document/idea ID, exact revision and permitted-source hashes, readiness criteria, author/reviewer roles, allowed output paths, and applicable policy/budgets.json budget. Missing inputs require a `blocked_inputs` checkpoint, never invented requirements. Interviews and scope changes require the Owner response.
2. The product-writer creates a new draft revision under artifacts/<idea>/, preserving RQ traceability, SIG references, and explicit questions. Never overwrite the initial document. Planned specifications do not update AS-IS knowledge.
3. An independent reviewer follows procedures/critique.md on the exact revision/hash and returns pass/revise/blocked using templates/review.md. Authors do not review their own work. Without an available independent session/person, return `awaiting_independent_review`; never simulate review.
4. On revise, the author fixes confirmed findings and submits a new revision for fresh review. Settings allow two author passes (initial plus one correction); a lower policy/budgets.json limit takes precedence. Stop with open questions if progress stalls, budget is exhausted, or a business decision is missing. Never raise limits automatically.
5. Only pass on the latest revision plus satisfied criteria yields `ready_for_owner_review`. This is neither approval nor a stage transition. For pilots, save author/reviewer refs, revisions/hashes, criterion evidence, pass count, and the result for Owner review.

Each handoff includes goal, inputs/hashes, output format, allowed paths/tools, acceptance, budget/stop. The coordinator does not launch new sessions without applicable permission. Store pilot evidence in `loops.brd.pilot_report`; no automatic scheduler is implied.
## Postconditions/outputs
Applicable versioned artifact, source evidence, signal_refs IDs (not copied rows), explicit gaps, checkpoint, short summary. Independent reviewer for applicable risk. No double state or planned/current confusion.
## Side effects/idempotency
Local permitted draft/proposed patch. Coordinator alone mutates CSV through tools/signals.py CAS+lock; others submit candidates. Signals do not automatically create task/backlog/verified fact. External writes OFF. Read-only cannot be bypassed.
## Stop/failure
Missing evidence/access, invalid schema, conflict, budget/policy, unknown external result→stop+checkpoint+failure classification. Safe bounded retry only. Do not invent successful writes, model availability or evidence.
