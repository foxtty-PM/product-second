# Local tools: requirements and operating instructions

Install and run from the workspace root using [Getting started](../GETTING_STARTED.md). Tool descriptions do not grant execution or write permissions. Operator commands and the supplied scoped agent shell have different limits; a denied command receives an operator handoff.

## Required before execution

- Python 3.11+ with venv/pip; PyYAML and jsonschema from [requirements.txt](../requirements.txt), installed in the same interpreter used for the tools. tomllib is part of Python 3.11+. A system Python below 3.11 is insufficient.
- An external environment. The supplied scoped shell specifically requires ~/.venvs/pm-os/bin/python; an environment inside the workspace can break the recursive checker. A temporary PYTHONPATH dependency directory is not a durable installation.
- Actual read access to the selected inputs and local write access for generators/writers. Source references and actor strings do not prove permission or identity. Protected changes remain operator-controlled unless explicitly authorized for the current work.
- For first launch, follow [setup](../procedures/setup.md): analyse the user's input, inventory relevant existing files, prefill evidence-backed values and ask only about gaps/conflicts. No tool automatically imports corporate context or produces valid pilot evidence.

If the environment is missing, record runtime_setup_pending and provide the [installation steps](../GETTING_STARTED.md). Do not silently substitute another interpreter or change the shell allowlist. After operator installation, these operator-terminal checks use the exact environment:

```sh
"$HOME/.venvs/pm-os/bin/python" --version
"$HOME/.venvs/pm-os/bin/python" -c "import yaml, jsonschema, tomllib; print('Dependencies available')"
"$HOME/.venvs/pm-os/bin/python" tools/check_package.py
"$HOME/.venvs/pm-os/bin/python" -m unittest discover -s tests -v
```

Record executable/dependency versions and actual results; an unrun check stays pending. Activate that environment before the shorter `python` examples below. Installation and preflight commands are operator commands, not additions to the agent allowlist.

## Tool descriptions

| Tool | Required inputs and instructions | Recommended verification |
| --- | --- | --- |
| [build_adapters](build_adapters.py) | Operator write access to generated host adapters. Reads canonical agents/ and skills/; run after those contracts change. Do not edit generated adapters as a second source. | Inspect generated changes; run the package checker for host sync. |
| [build_indices](build_indices.py) | Valid canonical cards and signal registry; write access to derived indices, graph and backlog. Run after material card/document/link changes. | Check backlog freshness and package integrity; generated tables are not editable canon. |
| [check_package](check_package.py) | Complete workspace, supported interpreter/dependencies and read access. Run `python tools/check_package.py`. | Expect PASS; retain exact failures and fix causes before regenerating a release baseline. Does not verify live discovery, model quality or OS isolation. |
| [build_manifest](build_manifest.py) | Explicitly authorized baseline refresh after reviewing final changes. Run `python tools/build_manifest.py` last, after generators, tests and evidence updates. Builder uses its own exclusions, not .gitignore. | Inspect included paths; use a clean inspected candidate for distribution. Never use regeneration to conceal unexplained differences. |
| [verify_manifest](verify_manifest.py) | Existing baseline; run `python tools/verify_manifest.py`. Read-only, exits nonzero on listed-file mismatches. | Expect PASS after final refresh. It checks listed files only; unlisted additions and content correctness require separate inspection. |
| [signals](signals.py) | Read/filter/get through the CSV helper. Capture/update: coordinator, approved JSON payload, current expected_hash and canonical ID links; writes use CAS/lock. Never directly edit the CSV. | Reconcile conflicts before retry; exact-source dedup is not semantic dedup. Export a separate formula-neutralized derivative for spreadsheet use. |
| [search](search.py) | Query or exact ID; filter related IDs before long content. `python tools/search.py ID --resolve` resolves a node or SIG row. DEMO/reference excluded by default. | Use --include-demo only to inspect synthetic examples; check the primary source for consequential claims. Empty search before onboarding is not missing product evidence. |
| [backlog](backlog.py) | Coordinator scoped shell. Reads: status/list/get. Writes: approved payload plus actor, expected_revision/op_id/note; artifact writes also use expected_hash. Preserve op_id for an identical retry. | Check status fresh=true after sync/apply; reconcile interrupted transactions/conflicts. Task/document writes do not approve a gate or move stage. |
| [runtime](runtime.py) | Library helpers for cooperating local writes, transition proposals and approval simulation; not a standalone CLI or authenticated authority. | Use the owning validated writer/procedure. Simulated approvals cannot authorize external actions; external transport is absent. |
| [export_pack](export_pack.py) | Library API: explicit local sources, new artifacts destination and completed human sensitivity review. Never overwrite an existing pack. | Inspect source hashes/content; immutable local export is not DLP or permission to send. |
| [migration_inventory](migration_inventory.py) | Operator read-only Markdown inventory: `python tools/migration_inventory.py PATH` with an explicitly permitted root. It hashes all Markdown below that root. | Prefer bounded metadata/path inspection for onboarding; do not run a whole-workspace inventory over caches, archives or private material unnecessarily. No migration is applied. |
| [shell_guard](shell_guard.py) | Existing Claude PreToolUse hook and actual host permission configuration. It checks the supplied coordinator command allowlist. | Verify the hook loads in the real host; do not weaken rules to make a command pass. A hook is not an OS sandbox. |
| [common](common.py) | Internal frontmatter/record/hash helpers used by the tools; no standalone user command. | Canonical record scans exclude templates; native tracker discovery must be checked separately. |

## Operational recommendations

- Use the current user input, saved profiles and exact source references before requesting context already present. Keep source text separate from interpretation and preserve provenance in the setup report.
- Use available read-only Nimbalyst tools to compare native tracker lists with canonical cards. Master templates can appear as `TO_FILL` work items; a passing checker and five canonical DEMO cards do not prove a clean UI. Resolve discovery with a supported approach that preserves card creation. Until a UI-created card passes live validation, create cards from the templates with valid IDs/entity_type and run generators/checks.
- Keep schedules disabled until real permitted-input pilots, runtime/timezone checks and the Owner's activation decision. No local script here implements a scheduler, broker or corporate connector.
- Record tool failures as missing runtime/dependency, denied access, invalid input, conflict or unknown result. Checkpoint the evidence; do not blindly retry or treat blocked/no-data as success.
- After reviewed changes: regenerate affected adapters/indices, run package/regression checks, save evidence, then build and verify the manifest. Preserve prior review reports as historical evidence. See [Deployment](../DEPLOYMENT.md) and [Publishing](../PUBLISHING.md).

## Supplied scoped agent shell

Only the coordinator uses these commands under the supplied Claude configuration, from the root with relative paths and no chaining. Actual runtime permissions still apply:

```sh
~/.venvs/pm-os/bin/python tools/signals.py hash
~/.venvs/pm-os/bin/python tools/signals.py list --related F-0001 --status new
~/.venvs/pm-os/bin/python tools/signals.py get SIG-000001
~/.venvs/pm-os/bin/python tools/signals.py capture --payload artifacts/signal-payload.json --expected-hash HASH --actor coordinator
~/.venvs/pm-os/bin/python tools/signals.py update SIG-000001 --payload artifacts/signal-payload.json --expected-hash HASH --actor coordinator
~/.venvs/pm-os/bin/python tools/signals.py export artifacts/signals-safe.csv
~/.venvs/pm-os/bin/python tools/search.py "query"
~/.venvs/pm-os/bin/python tools/backlog.py status
~/.venvs/pm-os/bin/python tools/backlog.py sync
~/.venvs/pm-os/bin/python tools/backlog.py list --stage bdr
~/.venvs/pm-os/bin/python tools/backlog.py get I-0001
~/.venvs/pm-os/bin/python tools/backlog.py apply --payload artifacts/backlog-op.json --actor coordinator
~/.venvs/pm-os/bin/python tools/build_indices.py
~/.venvs/pm-os/bin/python tools/check_package.py
~/.venvs/pm-os/bin/python -m unittest discover -s tests -v
shasum -a 256 path/to/file
```

--payload is a path to a JSON file. Everything else stays operator-only: build_adapters, build_manifest, verify_manifest, pip.
Agents cannot Edit tools/, policy/, .claude/, .codex/, signals/signals.csv or any .py file, otherwise the allowlist could be rewritten or skipped; tests run repository Python code. The operator changes them by hand after review.
