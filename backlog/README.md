# Product backlog

[Table](VIEW.md) · [CSV for spreadsheets and other editors](backlog.csv)

The sources of truth are Markdown dossiers under ideas/, tasks under tasks/, and existing BL-references under backlog/. CSV and VIEW.md are generated; manual view edits do not update cards. Signals remain exclusively in signals/signals.csv.

## Field provenance

| Table data | Canonical source |
|---|---|
| Title, type, priority, queue, remaining work, blockers | Dossier title, item_type, priority, queue_rank, priority_reason, remainder, blockers |
| Parent and path | member_of or iteration_of; neither folders nor spawned_from |
| Stage | Dossier status; work_status is shown separately |
| Approved | Accumulated gate_log history with distinct approved/inherited/not_applicable labels |
| Next approval | workflows/routes.json, applicable workflows/gates.json groups, and current decisions |
| Gate tasks | Own idea_id and gate_codes intersecting nearest gates |
| Documents and results | Dossier artifact_refs and task result_ref |
| ClickUp documents | Dossier clickup_docs: each document's title and URL |
| Development knowledge documents | Dossier dev_knowledge_docs: titles and URLs in the team's knowledge repository |
| Deferral and revisit | Active BL-card with source_id, reason, revisit |
| Value and measurement | Dossier value and measured_by links |
| Last change, when, who | Actual changed_at/changed_by/change_note records in dossiers, tasks, and BL-references |
| Signals | SIG IDs in signal_refs and exact related_ids; signal text is not copied |

One row represents one I-dossier of type initiative, feature, iteration, improvement, or bug. feature_ids links stable AS-IS capabilities F without duplicating them. Standalone features can have no parent. Documents, options, tasks, BL, and SIG records do not become product rows.

The first ten columns are title, parent, priority, stage, approved, next approval, gate tasks, last change, when, and who. ClickUp documents and Development knowledge documents follow in CSV and Markdown. Full CSV also includes ID, path, queue, links, remaining work, blockers, value, and provenance. Encoding is UTF-8 with BOM; formula neutralization applies only to the derived CSV.

clickup_docs and dev_knowledge_docs are optional {title, url} lists; multiple documents per type are allowed. Markdown shows clickable titles; CSV stores full URLs, one per line inside a cell. Only absolute HTTP(S) URLs without embedded credentials are allowed; the generator does not open them. Unknown links remain empty. Use set_fields on the dossier to update data and regenerate views. Links belong to their own row and are not inherited from parents.

A URL change is not approval, does not change stage, and does not verify remote content freshness. Local artifacts and gate revisions remain subject to separate checks.

## Writes and synchronization

tools/backlog.py apply is the controlled writer for cooperating callers. Supply op/id/expected_revision/op_id/note plus operation fields. Retain op_id for retries; a changed payload needs a new op_id. create requires expected_revision=0, an explicit ID, and a complete card; signals do not create ideas automatically.

Operations: create, set_fields, set_parent, task, artifact, gate, stage, defer, resume.
- set_fields cannot write status or gate_log.
- task updates only the task, including gate_codes/expected_result/gate_criteria/result_ref.
- artifact writes a permitted document under artifacts/ with expected_hash, links it to the dossier, and records the author. expected_hash=null is only for a new file.
- gate records every gate in a joint decision with a verbatim quote, decided_by, recorded_by, input_revision, and artifact_revisions (path → SHA-256). The vocabulary includes G1a–G7 and GX1–GX3.
- stage independently checks the route, all preceding gates, tasks, artifacts, revisions, blockers, and applicable review. Task/document operations never change stage.
- defer preserves stage, requires reason/revisit, and reuses a BL-reference. revisit is a date or a condition with an owner and check method. resume restores work_status=active.

After each actual write, apply regenerates the table. Procedures and entry skills also request coordinator rebuild through tools/build_indices.py after card/document/decision/SIG-link changes. Until explicitly permitted by the runtime, the operator runs the new CLI; documentation does not change the allowlist.

tools/build_indices.py generates indexes, graph, and backlog. tools/check_package.py rejects inconsistent canon or stale views. tools/backlog.py status checks sources and CSV/Markdown hashes. External edits are detected as stale; no background filesystem watcher is included, and the generator does not invent their author.

## Gates and value

No tasks means readiness is unconfirmed. done is not approval; dropped does not satisfy a criterion. Child iteration tasks remain in their own rows. After approval, show the next gate's tasks; previous tasks remain in cards/history.

Requested changes preserve history and require renewed approval of dependent later gates. N/A requires a reason; inherited requires an approved ancestor decision. A product feature's own G7 cannot be skipped or inherited. Changing an artifact with an approved SHA-256 blocks transitions based on the older revision.

product_feature uses a validating route even at scale S. Before G5/dev, require value: expected_value, metric, baseline or baseline_missing_reason, target, data_source, deadline, evaluation_rule. A mini-metric is allowed. Applicable operational/regulatory/technical_enabler criteria are not replaced with user-behavior metrics.

Iteration G7:
- next_iteration opens the next planned iteration.
- adjust_plan requires a new parent G3.
- stop blocks future iterations; close them separately with evidence.
- close does not start the next iteration.

The parent waits for child closure. Closed items have no next gate.

## Retries and recovery

A global lock serializes the writer. Validate schemas, links, revision, and the complete future state before writing. state/backlog.transaction.json stores before hashes and after-images; state/backlog.operations.json stores durable completed-operation receipts.

The same op_id/payload does not duplicate a change, even after other operations. Interrupted multi-file writes recover only when current files match before/after hashes; an intervening edit stops recovery without overwriting it. A generator failure returns synced=false/fresh=false; retry restores views. The operator reconciles stale crash locks after checking the process and journal.

This coordinates trusted local callers; it is not OS authentication or an immutable audit broker. Actor strings do not prove identity. The lock cannot protect direct UI/Excel/Edit writes that bypass the writer.

## Synthetic walkthrough

1. An iteration's task prepares G2+G4 with expected_result and gate_criteria.
2. The author records result_ref; done leaves G2+G4 unapproved.
3. The Owner approves exact revisions; the coordinator records the verbatim decision for both gates.
4. The table switches to G5 and its tasks.
5. With value, successful handoff, and applicable review, a separate stage operation moves the dossier to dev.
6. G6 → validating → actual measurement → G7; the conclusion can be inconclusive.

This walkthrough and DEMO cards are not real approval or value evidence. Live Nimbalyst UI, drag-and-drop, models, and MCP remain separate operator smoke checks.
