# Task execution

One canonical task per unit of work. DEMO is synthetic; load real context through setup/source review. Signals remain in signals/signals.csv.

## Plan only when useful

Simple tasks use the ready contract: goal, procedure, inputs, expected output, acceptance criteria and execution limits.

For dependent steps, substantial uncertainty or multiple agents, add a short plan to the task body: action -> expected result; name owners and dependencies where needed. Keep one shared plan in the coordinating task; child tasks link to it.

Update progress, deviations and the next step after material findings, blockers or approach changes. Reuse linked checkpoints; avoid rewriting the plan each turn. Scope/acceptance changes require a new revision and Owner approval when they affect approved work or gates.

## Verify before done

Keep one completion record in the existing result file, or in the task body linked from that result. Record:

- Each acceptance/gate criterion -> actual result -> evidence with revision/hash or exact locator.
- Checks performed and outcomes; list unrun checks and evidence gaps explicitly.
- Required independent review of the exact revision, resolution of blocking findings, or a reason review is not applicable.
- Plan deviations and remaining work: none, or a reason and link to approved follow-up work/decision.

Unmet criteria or unrun required checks block done. Use doing/needs-me/waiting/failed according to the transition rules. Moving a failed criterion to follow-up does not satisfy it. Dropped requires the Owner's reason. Repeat affected checks and required review after output changes.

Every done task, including operational work, needs a nonblank result_ref: a workspace-relative file path under artifacts/, ideas/ or tasks/, without URL/fragment. Verify the file exists before closing; put section locators in the completion record. Schema checks enforce the field, while executors and required independent reviewers verify evidence quality and coverage.

## Verify gates and next work

Coordinator selects tasks by their own idea_id and the nearest applicable gate_codes. Verify completion records, evidence, current inputs/reviews, dropped-task exclusions and blockers. Work without tasks needs an explicit reason and equivalent criterion evidence in the gate artifact.

After the Owner decision, update the dossier: next-gate criterion/result -> task or gap -> owner/dependency. Link canonical tasks; check freshness on stage entry. New work follows normal approval. Reuse this list across statuses; G3 still approves the product iteration plan. Task completion and next-work lists do not approve gates or change stage.
