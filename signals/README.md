# Signals contract OS 4.2
signals.csv is the single canonical signal registry: UTF-8 CSV with twelve fixed columns. A new empty registry contains no fake feedback. One row represents one meaningful observation; one source may describe several issues.

## Fields
signal_id: stable SIG-NNNNNN allocated by the coordinator under lock; observed_at: date/aware timestamp or empty; captured_at: required aware ISO timestamp; type: request/complaint/error/observation/suggestion; summary: what happened; context: where/who/conditions without PII; interpretation: why it matters, as a hypothesis rather than fact; source: system name; source_ref: URL/message/file+locator or empty; related_ids: existing D/F/I/iteration IDs separated by semicolons, empty if unknown; status: new/reviewed/actioned/dismissed; action_ref: work/decision IDs or a reason, multiple values separated by semicolons.
For reviewed and later states, require source_ref or an explicit missing_source_ref: <reason> marker in context. actioned/dismissed requires action_ref. actioned does not mean fixed. Minimal capture fields: summary/type/source; the tool generates SIG/captured_at/status=new. Do not invent unknown fields.

## Writes
Only the coordinator writes through tools/signals.py capture/update with expected_hash. Do not edit concurrently through Excel, UI, or another agent. A read-only session returns a candidate/patch and respects the actual sandbox. The actor string is a prototype check, not trusted authentication; OS/broker protection is separate.
Lock + read hash → validate the whole table → atomic temporary-file replacement. Repeating the same source/ref/type/normalized summary/context returns the existing row rather than a duplicate. Without source_ref, identical text is not automatically the same feedback. Independent sources remain distinct. Humans/agents can propose semantic deduplication; code does not declare paraphrases equivalent.
Transitions: new→reviewed/actioned/dismissed; reviewed→actioned/dismissed; actioned/dismissed→reviewed only with a reason in action_ref. Keep ordinary local-edit history in reviewed Git/backups. This procedure does not replace a durable immutable audit broker.

## Reads and ID links
List/filter by exact related ID/status before loading full content; resolve SIG to a row. Generated ID registry/graph includes rows without duplicating them as node files. Card.signal_refs=[SIG IDs]; related_ids creates typed signal→domain/feature/idea links; action_ref links actual work IDs when explicitly given. Broken IDs reject writes. New work follows normal capture/gates rather than being created automatically from a row.

## Knowledge and backlog
A raw signal is not a verified fact. With permission, the keeper can synthesize supported knowledge from SIG plus primary sources; do not copy every row. New signals remain new, not separate backlog entries. Backlog references are for actual deferred work.

## Safety
Minimize data; no secrets or raw citizen PII. A source link grants no additional rights. Canonical CSV preserves permitted text without silent corruption. spreadsheet_export produces a separate formula-neutralized CSV, prefixing dangerous starts with an apostrophe. Do not open unreviewed raw CSV in spreadsheets that execute formulas.
No native Nimbalyst signal-board guarantee, new agents, or new visible skills are implied. Read the local table through files/tools; the Owner verifies actual UI/provider permissions.
