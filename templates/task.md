---
schema_version: 4.2.0
id: TO_FILL
entity_type: task
title: TO_FILL
revision: 1
status: inbox
demo: false
aliases: []
summary: TO_FILL
sources: []
links: []
signal_refs: []
trackerStatus:
  type: pm-task
priority: low
idea_id: TO_FILL
agent: TO_FILL
procedure: TO_FILL
model_profile: standard
goal: TO_FILL
output_format: TO_FILL
input_manifest: []
tools_allowed:
- Read
allowed_write_paths:
- artifacts/TO_FILL/
no_gos:
- external writes
acceptance:
- TO_FILL
budget:
  max_retries: 0
  max_parallel: 1
stop_conditions:
- missing access
gate_codes: []
expected_result: TO_FILL
gate_criteria: []
result_ref: null
---

# task
## Required content
One goal; idea_id/iteration; procedure/version/input_manifest/output_format/tools_allowed/allowed_write_paths/no_gos/acceptance/model/budget/stop; checkpoints/failure; independent review; handover/evidence; signal_refs not raw copies. Gate-preparing task: gate_codes/expected_result/gate_criteria/result_ref on the row's own idea_id; operational task keeps gate_codes empty. done is not approval, dropped is not a met criterion.
## Short plan (complex work only)
Omit for simple tasks. List actions -> results, owners/dependencies as needed. Update material progress, deviations and the next step. Link shared plans instead of copying them. Contract: tasks/README.md.
## Completion record (before done)
Fill in here or link the record in the existing result_ref file; keep one canonical record.

| Acceptance / gate criterion | Actual result | Evidence: path + revision/hash/locator | Check and outcome |
| --- | --- | --- | --- |
| One row per criterion | What was delivered | Exact evidence | Performed/unrun; outcome and reason |

Review: link the exact revision and verdict, or explain why independent review is not applicable. Plan: record deviations and reasons. Remaining work: none, or reason + approved follow-up link. Unmet criteria or unrun required checks block done. Every done task requires result_ref to an existing result file, including operational work.
## Signals
Relevant SIG IDs in signal_refs; verify source evidence, never copy CSV as a second registry.
