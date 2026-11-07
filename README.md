# PM Second Brain OS

A local-first product management workspace for AI-assisted research, ideas, tasks, decisions, and evidence. Markdown cards and a single CSV signal registry keep the work inspectable and versionable with Git. Python helpers validate links, schemas, and generated views.

The workspace includes Nimbalyst tracker definitions and role/skill adapters for Claude and Codex. The files and operator tools can also be used from a terminal and a Markdown editor.

## What is included

- Structured product and domain knowledge, with source references and a distinction between current capabilities and proposed changes.
- Initiative and iteration dossiers, task contracts, review evidence, and Owner decision gates.
- A single signal registry with a controlled writer, duplicate checks, and spreadsheet-safe exports.
- Generated backlog, indexes, and relationship graph.
- Nine role contracts, twelve entry skills, templates, and local validation tests.
- Disabled example automation definitions for inbox and weekly work, plus a manual BRD workflow.

## Start locally

New to the terminal? Follow the [beginner install guide](INSTALL_FOR_BEGINNERS.md) step by step. Otherwise follow [Getting started](GETTING_STARTED.md) for prerequisites, installation commands, a first smoke check, and optional Nimbalyst setup. Use the [first-session prompt](BOOTSTRAP_PROMPT_EN.md) after installation.

Python **3.11 or newer** is required. Runtime dependencies are listed in [requirements.txt](requirements.txt). Git is needed for cloning and version control; Nimbalyst and an AI provider are needed for their respective editor/agent features. Local Python checks do not require provider credentials or a running model.

## Portability and current limits

The core uses Markdown, YAML, JSON, CSV, and Python. Local validation has been exercised on macOS with Python 3.13; Linux, WSL, and native Windows remain unverified. The shipped agent shell uses a Unix-style interpreter path and `shasum`; native Windows needs a separately reviewed runtime configuration.

Active workspace instructions, tracker labels, and automation prompts are English. Original source material and verbatim quotations retain their source language. Product/team/provider profiles are unconfigured. DEMO records are synthetic fixtures, and the signal registry starts empty. Saved automation times and the `Europe/Kyiv` timezone preference come from the original workspace and need review by each new user. Schedules start disabled.

Live editor discovery, provider access, OS isolation, connectors, and scheduler behavior require checks in the user's own environment. The local helpers use cooperating callers rather than authenticated production authorization. External writes are disabled. See [implementation status](IMPLEMENTATION_STATUS.md) for details.

## Workspace map

- [Context map](KNOWLEDGE_MAP.md): where agents retrieve context.
- [Architecture](ARCHITECTURE.md): canonical entities and relationships.
- [Profiles](profile/INDEX.md): owner, product, team, stack, and preferences.
- [Backlog view](backlog/VIEW.md): generated view of canonical work.
- [Task contract](tasks/README.md) and [signal contract](signals/README.md): execution and data rules.
- [Operator tools](tools/README.md): supported commands and agent shell boundaries.
- [Publishing guide](PUBLISHING.md): repository preparation and release checks.

## Distribution status

Released under the [MIT License](LICENSE). The public package is a clean starter: development history (session reports, patches, review evidence) and the original source document are not included. Verify your copy with `python tools/verify_manifest.py`; an integrity result does not approve publication. See the [publishing guide](PUBLISHING.md) before releasing a new version.
