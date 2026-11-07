# Preparing a Git repository

Git stores and versions this workspace; users run the Python tools locally and optionally open it in Nimbalyst or another editor. This folder currently has no Git repository or remote. This guide prepares a reviewable distribution; publishing and remote writes remain operator actions.

## Repository description

Suggested short description:

> Local-first product management workspace with Markdown knowledge, ideas, tasks, evidence gates, a CSV signal registry, Python validation, and Nimbalyst/AI-editor adapters.

Use [README.md](README.md) as the repository landing page and [GETTING_STARTED.md](GETTING_STARTED.md) for local startup. The current version identifier is in [VERSION](VERSION).

## Prepare the distributable content

1. Resolve release blockers or describe them explicitly for a preview. macOS checks do not establish Linux/Windows or live-editor support.
2. Decide which content belongs in a public starter. Inspect profiles, knowledge, signals, artifacts, local source references, automation outputs, and native-discovery reports for private information. Preserve originals in your private workspace; sanitize a separate release candidate. Retain the DEMO fixtures used by tests and the empty starter signal registry. Rerun generation/validation after reviewed changes.
3. The project is licensed under the [MIT License](LICENSE). Review redistribution rights for any material you add. Development history under artifacts/ and the original source document are not part of the public package.
4. Review the supplied hidden configuration directories. Keep canonical role/skill adapters and tracker definitions. The ignore rules omit editor-generated skill caches, Python environments/caches, local settings, secret-file patterns, and transient state. Ignoring a path does not remove it from existing history or prove other files are safe to publish.
5. Keep the external virtual environment out of the release folder. Keep the LF line-ending rules in [.gitattributes](.gitattributes) so text files have a consistent checkout representation.

The current [manifest builder](tools/build_manifest.py) excludes only its own fixed skip list; it does not consume Git ignore rules. In particular, ignored environments, `.env` files, and runtime state must be absent from a release candidate before an operator builds its manifest. Its verifier checks listed files and does not detect unlisted additions. Use an inspected clean candidate, not an active working folder, for a release baseline.

## Validate a clean candidate

From the candidate root, using the external environment in [Getting started](GETTING_STARTED.md):

```sh
python tools/build_adapters.py
python tools/build_indices.py
python tools/check_package.py
python -m unittest discover -s tests -v
```

Inspect the changes and required review evidence. Verify the actual final candidate independently of any working-folder result. After reviewing the final candidate, the trusted operator runs:

```sh
python tools/build_manifest.py
python tools/verify_manifest.py
```

These commands define and compare a local hash baseline; they are not a security signature or approval. Do not regenerate a baseline just to hide unexplained differences. Rerun verification after any final file change. Run `PMOS_RELEASE_CHECK=1` only when evaluating the specific untouched-release invariants; it is not appropriate for this already modified workspace.

## Initialize and inspect locally

After the content and license decisions, the operator may initialize the candidate:

```sh
git init
git status --short --untracked-files=all
```

Inspect the full proposed file list before staging. Keep `.agents/skills/.nimbalyst-generated` and other ignored runtime files out of the commit; preserve the twelve canonical adapters under `.agents/skills`. Include the reviewed manifest and documentation. Commit through the Nimbalyst commit proposal workflow when working in Nimbalyst; otherwise use your normal reviewed Git workflow.

Create the remote and publish through the repository host only after reviewing that exact commit and choosing visibility. No remote URL, repository name, license, or public visibility is assumed by these instructions. Test a fresh clone in a new folder using the startup guide before describing the repository as ready for other users.
