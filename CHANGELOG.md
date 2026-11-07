# 4.2.1 — 2026-11-07
Owner decisions, verbatim: "Так, додати (Recommended)" (backlog tool in the coordinator shell); "чому тести не дозволені зроби щоб дозволені" (tests in the coordinator shell); "треба новий пакет у вигаляді нової версії спакувати".
Coordinator scoped shell now runs tools/backlog.py and exactly `python -m unittest discover -s tests [-v]`. In exchange, agents cannot edit any .py file, so a planted test or module cannot bypass the allowlist; Python changes reach the operator as patches. Added INSTALL_FOR_BEGINNERS.md and linked it from README and START_HERE. Owner decisions for the public package, verbatim: "Ліцензія - обери можна використовувати"; "Вміст artifacts/ ... треба прибрати"; "право маю але воно там не потрібне видали його". Added MIT LICENSE. Development history under artifacts/ and reference/PM_SECOND_BRAIN_v8_original.md moved out of the package to the maintainer's dev-history folder; the original_retained check and test removed; doc links to them removed; artifacts/README.md translated. Release built from a clean candidate by the maintainer release script; logs are kept next to the ZIP. Card schema_version stays 4.2.0. Earlier entries cite artifacts/ paths that are not shipped.

# 4.2.0 English instruction replacement — 2026-11-07
Replaced active Ukrainian instructions with English across onboarding, context/specification, roles, skills, procedures, loop prompts, tracker labels, and backlog output. Removed the Ukrainian bootstrap entry point and updated checker/link references. Regenerated adapters and views; internal IDs, workflow states, runtime rights, and saved schedule values remain stable. Source archives and verbatim Owner quotations remain in their original language. Verification: artifacts/english-localization/RESULT.md.

# 4.2.0 first-launch readiness follow-up — 2026-11-07
Expanded setup/bootstrap instructions to analyse user input and existing files before a prefilled gap-only intake; preserve preferences and record provenance. Added Python 3.11+/external-environment preflight and operator installation handoff. Expanded tool descriptions with prerequisites, usage, permissions and checks; documented the existing native template-discovery gap. Owner requested a release-manifest refresh; current validation evidence is in artifacts/readiness-followup-2026-11-07/RESULT.md. No runtime policy, corporate data, scheduled activation or successful pilot is implied by these documentation changes.

# 4.2.0 task planning and completion — 2026-11-07
Owner instruction, verbatim: "Виконай рекомендацію".
Simple tasks use the existing contract; complex work uses one short in-card plan. Before done, verify each criterion against evidence and required review; record remaining work. Coordinator checks gate readiness and updates next-gate work after the Owner decision. Every done task requires nonblank result_ref.
Shared context, nine roles, relevant skills/procedures/templates and host adapters are aligned. Added instructions/templates are English; short references reduce repetition. New operational documentation defaults to concise English; source quotations remain verbatim.
Implementation checks: package PASS 513; 204 tests, 200 passed, 4 skipped. After wording cleanup: package PASS 513 and all six completion regression tests passed. Evidence: artifacts/task-planning/VERIFICATION.md. Live behavior, quality improvement and token savings are unmeasured.

# 4.2.0 backlog document links — 2026-11-07
Added separate ClickUp and dev knowledge repository document columns to CSV and Markdown, optional named URL lists in dossiers, controlled updates, validation, handoff/team-pack instructions and five regression tests. Full suite 198 (194 passed, 4 skipped), package 512 PASS; independent focused review completed. No actual external URLs supplied.

# 4.2.0 product backlog — 2026-11-07
Owner instruction, verbatim: "То закніч роботу". One-time interactive choice: "Так, завершити тут"; protected installation, test fixes and local generators/checks authorized without changing permanent policy/permissions.
Generated product backlog from canonical dossiers/tasks/BL references: Ukrainian labels, hierarchy, accumulated/joint/inherited/N/A gates and current-gate tasks. Product features require value evaluation, including S; iteration G7 controls continuation. Added CAS/lock writer, durable receipts/recovery, approval input freshness and stale-view checks. build_indices/check_package integrated; schemas/templates/procedures/skills/native fields and host adapters aligned. Canonical signals preserved.
Local verification: package PASS 512; unittest 193, passed 189, skipped 4. Independent reviewed code and limitations recorded in AUDIT_REPORT.md and artifacts/backlog-rollout/REVIEW.md. Live Nimbalyst not claimed.

# 4.2.0 coordinator read-only git — 2026-11-07
Owner decision, verbatim: "так, Додавати git status, git diff і git log для coordinator".
Scoped shell gains git status/diff/log with allowlisted flags; commit, restore and push stay with the operator. Edit denied on .git/ and git config, which could otherwise run commands from git status. Protected files change through artifacts/coordinator-git-readonly.patch, applied by the operator.

# 4.2.0 post-audit patch — 2026-11-07
Owner decision, verbatim: "пофікси всі пробелми"; "дати coordinator scoped shell. Це зручніше, але дає агенту shell-доступ".
Coordinator scoped shell: allowlist, shell_guard hook, Edit denied on CSV and scope-defining paths; Codex shell stays off. Tests split into regression and PMOS_RELEASE_CHECK=1 release state. Root paths resolved so tools and tests work under macOS /var→/private/var temp dirs. Malformed cards reported by build/check without breaking signal tools; _drafts are not nodes. Task template freed of DEMO values, TO_FILL rejected in cards. I-DEMO-0001 moved to L_parent, check requires it for parents. Schemas enforce scale/risk/work_type/route/priority/rel/source fields. check_package cross-checks workflows and policy. Added build_manifest, signals export, data_policy; keeper-only commit path and template use made explicit. AUDIT_REPORT figures predate this patch.

# 4.2.0 — 2026-11-07
Integrated accepted CSV signal workflow into single main package. Canonical signals registry, coordinator writer/CAS/dedup, typed SIG resolver/index/search, signal_refs in all authoring templates, updated all roles/skills/procedures, integrity/unit tests and spreadsheet-safe export. Existing domain/feature/flat ID-linked initiative/child/task/backlog model retained. No new overlay, agent, tracker or SQL state.
Model/provider/MCP/security/live Nimbalyst readiness remain explicit unverified; empty real signal table, DEMO synthetic context. Original v3.5 retained as reference, not active conflicting policy.
