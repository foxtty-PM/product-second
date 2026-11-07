# Getting started locally

These steps install the operator tools and explain how to start a supervised workspace session. Run terminal commands yourself from the project root. Agent permissions are a separate runtime configuration; a denied agent command is handed to the operator.

## 1. Prerequisites

- Python 3.11 or newer, including `venv` and `pip`. The checker imports `tomllib`, which sets this minimum version.
- Git for a clone, or an extracted copy of the repository downloaded as a ZIP.
- Network access to install the dependencies in [requirements.txt](requirements.txt). Once installed, the local checks below work without AI/provider credentials.
- A Markdown editor. Nimbalyst and a configured AI provider are optional for basic file inspection and Python checks.

macOS is the tested environment. The POSIX commands below also describe the intended Linux/WSL setup, which still needs testing. The PowerShell path covers operator tools only; native Windows and its symlink-dependent tests are unverified. The shipped agent shell assumes POSIX paths.

## 2. Get a fresh copy

Clone the repository using its actual Clone URL, then open a terminal in the resulting folder. With a ZIP download, extract it to a fresh folder and open a terminal there. The folder name is arbitrary; commands below assume the current folder contains [AGENTS.md](AGENTS.md) and [requirements.txt](requirements.txt).

Keep your existing workspace separate. Back up real data before a reviewed migration; do not overlay this starter on an older package. Hidden directories such as `.nimbalyst`, `.claude`, `.codex`, and `.agents` are part of the starter.

## 3. Create an environment outside the workspace

Use an external virtual environment because the package checker scans the workspace recursively. The supplied Claude shell allowlist specifically expects `~/.venvs/pm-os/bin/python`. Basic operator commands can use another external environment.

### macOS, Linux, or WSL — bash/zsh

```sh
python3 --version
python3 -m venv "$HOME/.venvs/pm-os"
source "$HOME/.venvs/pm-os/bin/activate"
export PYTHONUTF8=1
python -m pip install -r requirements.txt
```

If `python3 --version` reports a version below 3.11, use an installed Python 3.11+ executable for the `venv` command. If this environment already belongs to another project, create a separate external environment for operator use rather than changing it.

### Native Windows — PowerShell, experimental operator setup

```powershell
py -3.11 --version
py -3.11 -m venv "$HOME\.venvs\pm-os"
$pmosPython = "$HOME\.venvs\pm-os\Scripts\python.exe"
$env:PYTHONUTF8 = "1"
& $pmosPython -m pip install -r requirements.txt
```

Select another installed version at least 3.11 if needed. Calling the environment's interpreter directly avoids needing to activate a PowerShell script. Use `& $pmosPython` wherever subsequent examples use `python`. The supplied Claude hook and shell allowlist need operator review before agent use on native Windows; these instructions do not change them.

Dependency versions use ranges rather than a lockfile. Record the installed versions with any reproducibility report; identical versions on all machines are not guaranteed.

## 4. Verify the core

For a fresh copy, start with validation:

```sh
python tools/check_package.py
python -m unittest discover -s tests -v
python tools/signals.py list --status new
python tools/search.py DEMO --include-demo
```

Expected results: the checker returns `"status": "PASS"`; tests exit successfully with any skips reported; a clean starter returns `[]` for new signals; the explicit DEMO search shows synthetic examples. Searches exclude DEMO records by default, so an empty normal search is expected before real context is configured. Keep DEMO fixtures: the regression tests use them.

After reviewing changes to canonical cards or role/skill contracts, regenerate the appropriate derived files, then check again:

```sh
python tools/build_adapters.py
python tools/build_indices.py
python tools/check_package.py
```

These are local writes: adapters are generated from the canonical role/skill contracts; indexes, graph, and backlog are generated from canonical records. They do not import corporate data or approve gates. Run `build_indices.py` after a material workspace document/card update as required by the shared contract.

The normal test suite skips the untouched-release assertions. `PMOS_RELEASE_CHECK=1` is only for an actual untouched release whose profiles and data still satisfy those assertions; this working folder has accumulated changes. A skip is not a passing live-runtime check.

Manifest verification is a separate release check:

```sh
python tools/verify_manifest.py
```

Run verification for your actual copy rather than assuming a historical result still applies. A failure reports differences from its baseline. Keep the evidence and follow [Publishing](PUBLISHING.md); rebuilding a baseline does not establish that its contents are correct or reviewed.

## 5. Open the workspace and configure your context

For file-only use, read the [context map](KNOWLEDGE_MAP.md), [architecture](ARCHITECTURE.md), and [profile index](profile/INDEX.md). Inspect the [backlog view](backlog/VIEW.md) and the [task contract](tasks/README.md). Create future cards from the templates with valid IDs and links, then regenerate indexes and validate. Generated backlog tables are views, not a second editable state.

For Nimbalyst:

1. Open the whole project folder, including hidden configuration directories.
2. Inspect the four project tracker definitions: `pm-idea`, `pm-task`, `pm-backlog`, and `pm-feature`. The canonical examples contain five tracked DEMO cards. A previous native review also found four master templates in tracker lists; canonical checker counts do not prove a clean UI. Resolve template discovery before routine use.
3. Configure your own AI provider using the runtime's supported setup. Verify role/skill discovery, actual model access, and permissions. The shipped Codex parent starts read-only; Claude has a scoped shell hook. Files on disk do not prove that a host loaded these settings.
4. Start with the [bootstrap prompt](BOOTSTRAP_PROMPT_EN.md). First-launch [setup](procedures/setup.md) analyses your input and saved preferences, scans relevant existing files, and prefills supported context with provenance. Review one interactive intake for remaining gaps/conflicts, then apply confirmed supported profiles within actual rights. Knowledge promotion follows the keeper permission/provenance flow. Check [tool requirements](tools/README.md); absent runtime setup is an operator handoff, not a reason to invent context or pilot evidence.
5. Review [loop preferences](profile/loops.yaml), [loop onboarding](profile/loops.md), and their referenced automation definitions. The original saved schedules/timezone/language are examples for a new user to review. Keep schedules disabled until permitted real-input pilots, runtime checks, and Owner review are complete.
6. Choose one small real workflow with permitted inputs. Preserve source references, inspect the output/diff, and obtain independent review wherever the procedure requires it. A successful synthetic test is separate from a useful real pilot.

For another AI editor, open the project root and supply [AGENTS.md](AGENTS.md), the applicable role contract, and [KNOWLEDGE_MAP.md](KNOWLEDGE_MAP.md). Native Nimbalyst trackers and automations require host support. Validate that editor's discovery and access behavior yourself; adapters are not proof of compatibility.

## Troubleshooting

- **`python` is missing:** activate the POSIX environment again in a new terminal, or use its full interpreter path. On PowerShell use `& $pmosPython`.
- **Missing `yaml` or `jsonschema`:** run `python -m pip install -r requirements.txt` with the same interpreter used for checks. Installation needs network access or a separately provisioned offline package source.
- **Missing `tomllib`:** the interpreter is older than Python 3.11. Recreate an external environment using a supported interpreter.
- **Encoding errors:** enable `PYTHONUTF8=1` in the current shell before running the tools. Original source material and multilingual data may contain non-ASCII text.
- **Unexpected JSON/TOML/database errors after installing:** ensure the environment is outside the workspace. The checker currently scans all subdirectories, including ignored files.
- **`backlog_views_fresh` fails after valid card changes:** review the canonical changes, run `python tools/build_indices.py`, and rerun the checker.
- **Agent command denied:** keep the denial and hand the command/payload to the operator. Do not alter the hook or permission rules to bypass it.
- **Windows symlink/permission failure:** native Windows remains unverified; use a separately tested WSL setup or record the failing test for portability work. Passing operator commands does not establish that the POSIX agent adapter works there.
- **Extra template tracker items:** use the existing readiness report for the known discovery finding; changing a UI count is not proof of schema correctness.

For deeper runtime checks and activation boundaries, see [Deployment](DEPLOYMENT.md) and [Implementation status](IMPLEMENTATION_STATUS.md).
