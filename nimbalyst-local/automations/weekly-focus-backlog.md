---
automationStatus:
  id: weekly-focus-backlog
  title: Weekly focus and backlog
  enabled: false
  schedule:
    type: weekly
    days: [wed]
    time: "16:00"
  output:
    mode: new-file
    location: artifacts/loops/weekly-focus-backlog/
    fileNameTemplate: "{{date}}-{{time}}-weekly.md"
  runCount: 0
---

# Weekly focus and backlog review — draft
Work in English. Read AGENTS.md, KNOWLEDGE_MAP.md, agents/keeper.md, profile/INDEX.md, profile/loops.yaml, profile/loops.md, procedures/weekly.md, and signals/README.md. Then read only relevant profiles/indexes/nodes, excluding DEMO and reference.

## Before running
Draft-only: create only a report at the configured output location. Never change status/stage/priority, cards, signals/signals.csv, knowledge, or source cursors. No external writes/sends or new sessions.
Check loops.weekly.selected and execution_mode=draft_only. Scheduled runs require verified loops.weekly.pilot_report and owner_activation_ref with the verbatim Owner decision. Compare behavioral inputs with the pilot: settings/timezone, source scope, schedule, prompt, and write boundaries. Changes only to enabled/runCount/service timestamps do not change behavior. Missing evidence, changed scope, or unverified scheduler timezone means blocked_activation.
Without activation references, a manual pilot requires an explicit Owner pilot request in the current session plus verified inputs/rights/timezone. Manual invocation alone is neither such a request nor proof of success.

## Execute
Read actual Owner priorities, active real ideas/tasks, and deferred references. Backlog VIEW/CSV is derived: check freshness with available metadata/tools; if insufficient, mark unverified and use canonical cards. Do not rebuild or edit anything in this run.
Missing real context, DEMO-only cards, or unconfigured profiles preventing focus selection means blocked_no_real_context with required inputs, not successful review/pilot.
For signals, first filter metadata by status=new and exact related_ids of relevant initiatives; inspect only needed rows. Verify consequential claims against permitted primary sources. Reference SIG IDs without copying the registry. Repetition counts do not automatically establish priority.
Compare the last seven days with the previous weekly report if available. That report is supporting context, not canon. Separate documented outcomes from activity; never invent baselines, impact, costs, or completed work.
Propose at most three priorities for next week with reasons, blockers, nearest gates, important unprocessed signals, and revisit items. Decisions remain with the Owner.

## Report
status: draft / blocked_activation / blocked_no_real_context / blocked_inputs; time/timezone and period; outcomes/evidence; current focus; blockers/gates; important unresolved SIG references; deferred revisit; at most three Owner proposals; gaps/unknowns. Checkpoint input paths/revisions/hashes, coverage, actual writes, and stop reason.
Empty/DEMO-only/blocked runs are not successful pilots. Never claim costs or scheduler behavior verified from a prompt. Missing rights, conflicts, exhausted applicable budget, or unknown results require stop/checkpoint; no blind retries or batch catch-up of missed runs.
