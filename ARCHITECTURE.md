# Entities and relationships
Domain: a functional area and its subject rules. Feature: a stable capability and confirmed AS-IS. Idea/initiative: a proposed change or investigation. Iteration: a child idea linked through iteration_of. Task: a specific unit of work. Product backlog: an assembled view of dossiers; a BL-reference records deferral rather than a second copy. Signal: an incoming observation/request in CSV, not a task or verified fact.

## Canonical locations
- knowledge/domains/: domains, rules, processes, roles.
- knowledge/product/features/: AS-IS capabilities.
- knowledge/product/interfaces/, systems/, integrations/: implementation context.
- knowledge/metrics/, decisions/, sources/: definitions, rationale, evidence.
- ideas/: idea cards, artifacts, and iterations. Flat cards are valid; iteration_of defines the parent.
- tasks/: task cards. backlog/: deferred references/revisit and generated backlog.csv, VIEW.md, backlog.meta.json; contract: README.md.
- signals/signals.csv: SIG IDs, metadata, source/ref, related_ids, status, action_ref. Contract: signals/README.md.
- profile/: Owner/product/value-map/team/stack/tone.
- artifacts/<idea>/: outputs, reviews, derived exports; do not duplicate the canonical specification.

## Relationships
Domain D→Feature F through belongs_to_domain; Idea I affects F; child I.k iteration_of I; feature/improvement/bug member_of initiative; Task T implements I.k. A signal's related_ids can refer to multiple D/F/I/I.k IDs. Card.signal_refs contains only SIG IDs, not signal copies. SIG.action_ref identifies actual work/decisions; the source row stays in CSV.
Backlog source_id references an idea/task/iteration rather than copying its content. Unprocessed signals stay new in CSV; do not create a backlog entry for each one.

## Two kinds of context
Current feature/domain knowledge differs from planned initiative requirements. A planned specification does not make a feature current; the keeper updates AS-IS after implementation evidence and Owner permission. A domain can cover many features, and an initiative can affect multiple features/domains without copying them.

## Tracker
Four custom types: pm-idea, pm-task, pm-backlog, pm-feature. A UI status change is not gate evidence. Markdown top-level fields are canonical; trackerStatus={type}. Keep stable PM IDs separate from app-generated keys. No duplicate stage or SQLite state. Signals are not native/inline tracker items.

## Product view
One I-dossier produces one product row of type initiative/feature/iteration/improvement/bug. F-nodes remain confirmed AS-IS and are linked by feature_ids rather than duplicated in the table. Gates and nearest-gate tasks derive from gate_log/gate_codes and workflows/gates.json. Documents, tasks, BL-references, and SIG rows do not become product backlog rows. The writer and sync do not modify signals/signals.csv.
