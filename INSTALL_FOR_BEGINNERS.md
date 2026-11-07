# Install and launch PM Second Brain OS — beginner guide

This guide is for someone who has never used a terminal or Git. It takes about 30–45 minutes. Follow the steps in order and do not skip any.

**Works on:** macOS (tested). Windows and Linux are not tested yet. If you use Windows, ask the person who gave you this package for help.

**You need:**

- A Mac with internet access.
- Your Mac login password (you may need it to install apps).
- A paid AI account to use the assistant inside the app: Claude (Pro or Max) or OpenAI Codex. You can install everything without one, but the assistant will not work.
- The package: a ZIP file, or a Git link from the person who shared it.

---

## Words you will see

| Word | What it means |
| --- | --- |
| **Terminal** | A Mac app where you type commands instead of clicking. It is already on your Mac. |
| **Command** | One line of text you paste into Terminal and run by pressing **Enter**. |
| **Folder / project** | The folder with all the OS files. Its main file is `AGENTS.md`. |
| **Python** | A free program that runs the checking tools in this package. |
| **Git** | A tool that downloads and tracks versions of files. It is **optional** if you got a ZIP. |
| **Nimbalyst** | The desktop app where you open the OS and work with the AI assistant. |

**How to run a command:** copy the line from this guide, click inside the Terminal window, paste it (**⌘ Cmd + V**), then press **Enter**. Wait until the text cursor appears again before running the next command.

> When Terminal asks for your password, the letters do not appear while you type. This is normal. Type your password and press **Enter**.

---

## Step 1. Install Python

1. Open <https://www.python.org/downloads/> in your browser.
2. Click the yellow **Download Python 3.x.x** button. Any version **3.11 or newer** works.
3. Open the downloaded `.pkg` file from your Downloads folder and click **Continue / Agree / Install** until it finishes.
4. When the installer opens a Python folder in Finder, you can close it.

Do not use the Python that comes with your Mac. It is usually version 3.9, which is too old.

## Step 2. Open Terminal and check Python

1. Press **⌘ Cmd + Space**, type `Terminal`, and press **Enter**.
2. Run this command:

```sh
python3 --version
```

You should see `Python 3.11` or a higher number (for example `Python 3.13.5`).

- **You see 3.9 or lower:** close Terminal completely (**⌘ Cmd + Q**), open it again, and repeat. If the number is still low, use `/usr/local/bin/python3` instead of `python3` in Step 5.
- **A window asks you to install "command line developer tools":** click **Install** and wait. Then repeat the command.

## Step 3. Get the package files

Choose **one** option.

### Option A — you received a ZIP file (easiest, no Git needed)

1. Open Finder and press **⌘ Cmd + Shift + H** to go to your home folder (the one with a house icon).
2. Move the ZIP file (for example `PM-OS-4.2.1.zip`) into this home folder.
3. Double-click the ZIP. A new folder appears (for example `PM-OS-4.2.1`).
4. Rename the folder to `PM-OS` (click it once, press **Enter**, type the name, press **Enter**). If a `PM-OS` folder already exists from an older version, rename the old one first (for example to `PM-OS-old`); do not mix the two.

### Option B — you received a Git link

1. In Terminal, run:

```sh
git --version
```

   If a window asks to install developer tools, click **Install**, wait, then run it again. You should see a version such as `git version 2.x`.

2. Run these two commands. Replace `PASTE-THE-LINK-HERE` with the link you received:

```sh
cd ~
git clone PASTE-THE-LINK-HERE PM-OS
```

### Important for both options

- Use a **fresh, empty folder**. Do not copy this package over an older version.
- Avoid folders synced to iCloud, Dropbox, or Google Drive. Use your home folder as shown above.
- The package contains **hidden folders** (`.claude`, `.nimbalyst`, `.codex`, `.agents`). Do not delete them. To see them in Finder, press **⌘ Cmd + Shift + .** (period).

## Step 4. Go to the folder in Terminal

Run:

```sh
cd ~/PM-OS
```

If you named or placed the folder differently: type `cd ` (with a space at the end), drag the folder from Finder into the Terminal window, then press **Enter**.

Check that you are in the right place:

```sh
ls -a
```

The list must include `AGENTS.md`, `requirements.txt`, `.claude`, and `.nimbalyst`. If it does not, you are in the wrong folder, or hidden folders were lost when the files were copied. Ask for a new copy.

## Step 5. Install the tools (one time only)

Run these commands one by one, in this order:

```sh
python3 -m venv ~/.venvs/pm-os
```

```sh
source ~/.venvs/pm-os/bin/activate
```

```sh
export PYTHONUTF8=1
```

```sh
python -m pip install -r requirements.txt
```

What this does:

1. Creates a private Python space named `pm-os` in a hidden folder in your home folder. Keep this exact name and location: the AI assistant is allowed to use only this one.
2. Turns that space on. You will see `(pm-os)` at the start of the Terminal line.
3. Makes text with non-English letters work correctly.
4. Downloads two small helper libraries. The last line should start with `Successfully installed`, or say `Requirement already satisfied`.

## Step 6. Check that everything works

Still in the same Terminal window, run:

```sh
python tools/check_package.py
```

Look for `"status": "PASS"` in the output.

Then run the tests:

```sh
python -m unittest discover -s tests -v
```

Wait until it finishes. The last line should be `OK`, or `OK (skipped=N)`. Skipped tests are normal.

If you see `FAIL` or `ERROR`, stop. See [Troubleshooting](#troubleshooting) and send the last 20 lines of Terminal output to the person who shared the package.

You can close Terminal now. You do not need it for daily work.

## Step 7. Install Nimbalyst

1. Open <https://nimbalyst.com> and download the macOS version. To choose between the two Mac versions, open the Apple menu  > **About This Mac**:
   - **Chip: Apple M1/M2/M3/M4…** → download **Apple Silicon**.
   - **Processor: Intel…** → download **Intel**.
2. Open the downloaded `.dmg` file and drag **Nimbalyst** into the **Applications** folder.
3. Open Nimbalyst from Applications. If macOS warns that the app was downloaded from the internet, click **Open**.
4. Follow Nimbalyst's on-screen steps to connect your AI account (Claude or Codex). The exact screens may change between Nimbalyst versions.

## Step 8. Open the OS in Nimbalyst

1. In Nimbalyst, open a folder/project and select your `PM-OS` folder (the folder that contains `AGENTS.md`). Select the folder itself, not a file inside it.
2. Optional check: go to **Settings > Project > Trackers**. You should see four trackers: `pm-idea`, `pm-task`, `pm-backlog`, `pm-feature`.

## Step 9. Start your first session

1. In the project files, open `BOOTSTRAP_PROMPT_EN.md`.
2. Select all of its text (**⌘ Cmd + A**) and copy it (**⌘ Cmd + C**).
3. Start a new AI session in Nimbalyst, paste the text, and send it.
4. The assistant reads the workspace and asks you a short set of questions about your product, team, sources, and first workflow. Answer them. It then runs one small, safe first task with you.

Good to know:

- Records marked **DEMO** are fake examples. Do not delete them; the checks use them.
- Automations (scheduled tasks) start **turned off**. Leave them off until you have tried the workflows manually.
- If the assistant says a command was **denied** or asks you to run something yourself, this is a safety rule, not an error. Ask the assistant to explain the command, then run it in Terminal yourself (Step 4 + `source ~/.venvs/pm-os/bin/activate` first) only if you understand what it does.

---

## Launching it next time

1. Open **Nimbalyst**.
2. Open your `PM-OS` project (it appears in the recent projects list).
3. Start or continue an AI session.

You do **not** need to repeat Steps 1–6.

To run the checks again later, open Terminal and run:

```sh
cd ~/PM-OS
source ~/.venvs/pm-os/bin/activate
python tools/check_package.py
```

---

## Troubleshooting

| What you see | What to do |
| --- | --- |
| `command not found: python` | Turn the tools on again: `source ~/.venvs/pm-os/bin/activate`. You must do this every time you open a new Terminal window. |
| `command not found: python3` | Python is not installed. Repeat Step 1, then close and reopen Terminal. |
| `No module named 'tomllib'` | Python is too old. Install a new version (Step 1), then delete the old space with `rm -rf ~/.venvs/pm-os` and repeat Step 5. |
| `No module named 'yaml'` or `'jsonschema'` | Run `python -m pip install -r requirements.txt` again with `(pm-os)` visible. Check your internet connection. |
| `No such file or directory: requirements.txt` | You are in the wrong folder. Repeat Step 4. |
| `UnicodeDecodeError` or other text errors | Run `export PYTHONUTF8=1`, then repeat the command. |
| The checker fails right after you added or changed cards | Run `python tools/build_indices.py`, then run the checker again. |
| The assistant cannot run any commands | Make sure Python is installed (Step 1) and the `pm-os` space exists (Step 5), then restart Nimbalyst. |
| Extra template items appear in tracker lists | This is a known issue with the current version. You can ignore it. |

---

## Safety rules

- Do not paste passwords, API keys, or personal data about citizens or customers into the workspace.
- Do not delete hidden folders, `tools/`, or `policy/`.
- Do not change permission settings to make a blocked command work.
- Edit `signals/signals.csv` only through the assistant, never in Excel or Numbers.

## Where to read more

- [README](README.md) — what the OS is.
- [Getting started](GETTING_STARTED.md) — the same setup for technical users.
- [Deployment](DEPLOYMENT.md) — advanced checks.
