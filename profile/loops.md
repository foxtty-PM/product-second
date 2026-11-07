# Loop settings

[loops.yaml](loops.yaml) stores selected workflows, timezone, inputs, and pilot evidence references. Times and actual `enabled` state live only in the [morning](../nimbalyst-local/automations/inbox-morning.md), [afternoon](../nimbalyst-local/automations/inbox-afternoon.md), and [weekly](../nimbalyst-local/automations/weekly-focus-backlog.md) definitions. Change times there; do not create a second schedule table.

The Owner selected daily signal triage, BRD revision, and weekly focus review. The initial `Europe/Kyiv` timezone comes from the session environment; show that assumption during onboarding. Use the timezone's daylight-saving rules rather than a fixed UTC offset. The automation schema has no verified timezone field: the operator checks Nimbalyst/OS timezone, sleep, and missed-run behavior. Keep schedules disabled until checked.

## First launch

1. Setup reads the [procedure](../procedures/setup.md), these settings, and schedule definitions. Show saved values together and allow changes through an interactive form. Do not re-ask previously selected times or reset settings, `runCount`, results, or pilot evidence.
2. Complete inbox sources/access; for BRD, obtain the specific document, permitted sources, criteria, and independent reviewer. Empty means unconfigured.
3. Run one manual pilot per workflow using real permitted inputs. Keep automations disabled throughout. A native manual-run command is usable only after checking inputs/rights; do not work around missing capabilities through shell/network.
4. Record who/when, session ID, exact input paths/versions/hashes, result, uncertainties, and allowed/actual writes. Repeat inbox with identical inputs to check for data loss and duplicate candidates. Empty DEMO-only or blocked runs are not successful pilots.
5. The Owner reviews results. Fill `pilot_report` and `owner_activation_ref` for each scheduled workflow with evidence and the verbatim decision; only then does the operator enable its definitions. One inbox pilot may cover morning/afternoon if it includes both schedules/prompts. This grants no publication or canonical-edit permission.

Combine missing source, timezone/runtime, and BRD questions in one interactive form with at most three thematic groups. Times are already selected for the current Owner; ask only about missing inputs or requested changes.

## After the pilot

Scheduled inbox and weekly runs create only a new report/draft. Inbox returns candidates and existing SIG references; coordinator registration through `tools/signals.py` CAS/lock is a separately permitted action. Advance source cursors only after actual capture. Reports are not a second signal registry; never allocate SIG IDs there or duplicate CSV rows.

Run BRD manually for one document under the [procedure](../procedures/brd.md). Allow at most two author passes: initial draft and one revision following independent review. Lower applicable budgets take precedence. Without an independent reviewer, save the draft and hand it off; no self-review or ready claim.

Each run rechecks settings and pilot evidence. Changed timezone, schedule, sources, prompt, or write boundaries require a new pilot. Changes only to `enabled`, `runCount`, or service timestamps do not change the behavioral contract. Missing access/inputs, conflicts, or unknown results require a checkpoint and reason; no blind retries or unchecked batch catch-up of missed runs.

These are agent instructions/configuration, not software enforcement or proof of scheduler execution. Other workspace automations remain unchanged.
