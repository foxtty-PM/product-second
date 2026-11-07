# PM Second Brain OS 4.2 — consolidated package

Start with the [repository overview](README.md), [local setup](GETTING_STARTED.md) or the [beginner install guide](INSTALL_FOR_BEGINNERS.md), and [first-session prompt](BOOTSTRAP_PROMPT_EN.md).

First launch follows [setup](procedures/setup.md): analyse user input and saved preferences, scan relevant existing files, prefill supported context with provenance, then ask only about gaps/conflicts in one interactive intake. Unconfigured starter profiles are expected; real pilot evidence is produced during onboarding. Check [Python and tool requirements](tools/README.md) before execution; missing environments receive an operator setup handoff.

2026-11-07. Replaces v4.1, v4.0, the Nimbalyst overlay, and the separate signals document. Do not install another package over this one.
1. Extract to a fresh folder. Open the folder containing AGENTS.md and this file in Nimbalyst.
2. Inspect Settings > Project > Trackers: pm-idea, pm-task, pm-backlog, pm-feature; five synthetic canonical cards. Signals use a separate local CSV, not a fifth tracker.
3. Start a session with BOOTSTRAP_PROMPT_EN.md. The agent starts from KNOWLEDGE_MAP.md and profile/INDEX.md. DEMO is not real product data.
4. Review [loop settings](profile/loops.md): inbox at 08:30/16:30 daily, weekly on Wednesday at 16:00, and BRD manually. Run real manual pilots before deciding to enable schedules; all new automations start disabled.

## Everything in one place
knowledge/domains/: functional domains and subject rules.
knowledge/product/: current capabilities, interfaces, systems, integrations.
knowledge/metrics/, decisions/, sources/: metrics, decisions, evidence.
ideas/: initiatives and iterations; tasks/: one canonical task entity; backlog/: generated VIEW.md/backlog.csv and deferred references; its README explains field provenance.
signals/signals.csv: the single primary signal registry; source evidence and interpretation remain separate. The coordinator is the only writer.
profile/: Owner/product/team/stack/tone context. Unconfigured values are expected: setup uses real permitted sources and never invents context.

## Source of truth
Cards are Markdown; signals are CSV. There is no SQLite tracker. Nimbalyst trackerStatus contains only type; title/status/priority stay top-level. Idea status is stage; feature status is lifecycle. ID links establish parentage, not folder nesting.

## Readiness limits
AUDIT_REPORT.md records executed local checks. Live Nimbalyst/providers/MCP, real sends, OS isolation, and LLM behavior require separate verification. The external sender is disabled and absent. Simulated approval does not authorize real actions. Changes require scoped local rights and diff review; denied permissions must not be bypassed.

Read [Deployment](DEPLOYMENT.md). Previous packages and a separate signal supplement are no longer needed.

Open the product backlog as a [readable view](backlog/VIEW.md) or [CSV](backlog/backlog.csv). Regenerate with tools/build_indices.py after card changes; do not edit the table as independent state. Synthetic fixtures are marked DEMO. Native table editing in Nimbalyst remains unverified.
