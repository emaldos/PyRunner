Here’s an updated **README.md** that matches your current GUI (with the **Config Maker** form, no YAML editor/templates), plus cleaner install steps that copy **both** `pyrunner.py` and `pyrunner_gui.py` into a single folder under `/usr/local/bin/pyrunner/`, and add tidy launchers.

---

# 🚀 PyRunner

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/emaldos/PyRunner.svg)](https://github.com/emaldos/PyRunner/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/emaldos/PyRunner.svg)](https://github.com/emaldos/PyRunner/issues)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](https://github.com/emaldos/PyRunner)

**The Ultimate Python Virtual Environment Manager and Script Runner** 🐍✨

PyRunner streamlines Python development by handling virtualenvs, dependencies, profiles, and script execution—so you stay focused on your code.

---

## 🎉 What’s New in V2.0

### 🖥️ GUI Mode (Now Available)

A clean, dark-mode GUI for visual management.
you can use -g , -G , --gui or --GUI

```bash
# Launch the GUI
pyrunner --gui
```

**Current GUI highlights:**

* 🧰 **Config Maker (Form-based)** — build/edit `config.yaml` via text fields (comma-separated lists and KEY=VALUE pairs) and save.
* 🧪 **Normal vs Advanced views** — quick start in Normal; full controls in Advanced.
* ▶️ **Run / Stop** — with optional hot reload.
* 📦 **Package add/remove** — manage packages per environment.
* 🩺 **Doctor & Validate** — diagnose and validate envs; auto-fix from CLI.
* 🧭 **Profile dropdown** — select active profile from `config.yaml`.
* 🧾 **Console output** — real-time logs for your process.
* 🗂️ **Environment list** — size, deps count, and scripts per env.

### ⚡ Core Improvements

* 🧠 Smarter auto-detection of configs
* 🚀 Faster installs with caching
* 🔒 Lock-file friendly flow (via your own workflows)
* 🩹 Better diagnostics with actionable output
* 🎭 Profiles (dev/test/prod) respected by both CLI and GUI

---

## 🌟 Features

### ⚡ Smart & Fast

* Auto-detect `requirements.txt` / `config.yaml`
* Hot reloading with file watching
* Parallel installs and caching
* Reproducible dependency workflows

### 🛠️ Developer Experience

* **GUI Mode** for everything visual
* One-command run: `pyrunner run app.py`
* Interactive shells inside envs
* Configuration profiles
* Auto-fix helpers (CLI)

### 🔧 Advanced Management

* List, validate, reset, and clone environments
* Add/remove packages quickly
* Helpful, context-rich errors

---

## 📥 Installation

### Option 1: Tidy system install (recommended)

This keeps `/usr/local/bin` clean by placing both files in **one folder** and creating two small launchers.

```bash
# Clone
git clone https://github.com/emaldos/PyRunner.git
cd PyRunner

# Ensure executables
chmod +x pyrunner.py pyrunner_gui.py

# Create a tidy folder in /usr/local/bin and copy both scripts there
sudo mkdir -p /usr/local/bin/pyrunner
sudo cp pyrunner.py pyrunner_gui.py /usr/local/bin/pyrunner/

# Make sure they are executable there too
sudo chmod +x /usr/local/bin/pyrunner/pyrunner.py /usr/local/bin/pyrunner/pyrunner_gui.py

# Create launchers:
# 1) 'pyrunner' -> CLI (also accepts --gui)
sudo ln -sf /usr/local/bin/pyrunner/pyrunner.py /usr/local/bin/pyrunner

# 2) 'pyrunner-gui' -> direct GUI entry (optional convenience)
sudo ln -sf /usr/local/bin/pyrunner/pyrunner_gui.py /usr/local/bin/pyrunner-gui
```

Now you can run:

```bash
pyrunner --version
pyrunner --gui
pyrunner-gui
```

### Reinstall / overwrite if an older install exists

```bash
# Reinstall (idempotent): removes any old install/symlinks, then re-copies and relinks
sudo bash -c 'set -euo pipefail
DEST="/usr/local/bin/pyrunner"; CLI="/usr/local/bin/pyrunner"; GUI="/usr/local/bin/pyrunner-gui"
rm -f "$CLI" "$GUI"
rm -rf "$DEST"
mkdir -p "$DEST"
cp pyrunner.py pyrunner_gui.py "$DEST/"
chmod +x "$DEST/pyrunner.py" "$DEST/pyrunner_gui.py"
ln -sf "$DEST/pyrunner.py" "$CLI"
ln -sf "$DEST/pyrunner_gui.py" "$GUI"
echo "PyRunner reinstalled to $DEST and launchers updated: $CLI, $GUI"
'
```

---

### Uninstall (clean removal)

```bash
# Uninstall: removes launchers and install folder
sudo bash -c 'set -euo pipefail
rm -f /usr/local/bin/pyrunner /usr/local/bin/pyrunner-gui
rm -rf /usr/local/bin/pyrunner
echo "PyRunner uninstalled."
'
```

---

### One-shot full setup (deps + install + launchers)

```bash
# One-liner full setup: system deps, Python deps, copy, link
bash -c 'set -euo pipefail
# 1) System deps (Debian/Ubuntu). Skip if not needed.
if command -v apt >/dev/null 2>&1; then
  sudo apt update -y
  sudo apt install -y python3-pip python3-venv python3-yaml
fi
# 2) Python deps (CLI + GUI + watch)
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade pyyaml watchdog PyQt6
# 3) Ensure scripts are executable locally
chmod +x pyrunner.py pyrunner_gui.py
# 4) Install to /usr/local/bin/pyrunner + link launchers
sudo rm -f /usr/local/bin/pyrunner /usr/local/bin/pyrunner-gui
sudo rm -rf /usr/local/bin/pyrunner
sudo mkdir -p /usr/local/bin/pyrunner
sudo cp pyrunner.py pyrunner_gui.py /usr/local/bin/pyrunner/
sudo chmod +x /usr/local/bin/pyrunner/pyrunner.py /usr/local/bin/pyrunner/pyrunner_gui.py
sudo ln -sf /usr/local/bin/pyrunner/pyrunner.py /usr/local/bin/pyrunner
sudo ln -sf /usr/local/bin/pyrunner/pyrunner_gui.py /usr/local/bin/pyrunner-gui
echo "✅ PyRunner installed and ready."
'
```

### Option 2: Local alias (no sudo)

```bash
# From the project directory
chmod +x pyrunner.py pyrunner_gui.py
mkdir -p ~/.local/bin/pyrunner
cp pyrunner.py pyrunner_gui.py ~/.local/bin/pyrunner/
chmod +x ~/.local/bin/pyrunner/pyrunner.py ~/.local/bin/pyrunner/pyrunner_gui.py
ln -sf ~/.local/bin/pyrunner/pyrunner.py ~/.local/bin/pyrunner
ln -sf ~/.local/bin/pyrunner/pyrunner_gui.py ~/.local/bin/pyrunner-gui
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Dependencies

```bash
# System packages (Debian/Ubuntu)
sudo apt update
sudo apt install -y python3-pip python3-venv python3-yaml

# Python packages
pip3 install --upgrade pip
pip3 install pyyaml watchdog PyQt6
```

---

## ✅ Verify Installation

```bash
pyrunner --version
pyrunner --gui
```

---

## 🚀 Quick Start

### GUI (V2)

1. Open GUI: `pyrunner --gui`
2. Normal view: select **Script** and **Config** → **Easy Start**
3. Advanced view: set **env path**, **profile**, **args**, toggle **Watch**, then **Prepare/Run**
4. Use **Config Maker** (top bar) to create/edit `config.yaml` with friendly inputs

### CLI

```bash
# Smart run (auto-detects config and env)
pyrunner run app.py

# With packages if no config exists
pyrunner run app.py flask requests

# With hot reload
pyrunner run server.py --watch

# Choose profile
pyrunner run app.py --profile production
```

---

## ⚙️ Configuration

### requirements.txt

```txt
flask>=2.0.0
requests
pandas
```

### config.yaml (supported fields)

```yaml
python_version: "3.11"
dependencies: ["flask", "requests"]
dev_dependencies: ["pytest", "black"]
environment_variables: {DEBUG: "true", APP_NAME: "MyApp"}
profiles:
  development:
    dependencies: ["flask[dev]"]
    env_vars: {LOG_LEVEL: "debug"}
  production:
    dependencies: ["gunicorn"]
    env_vars: {DEBUG: "false", LOG_LEVEL: "info"}
active_profile: "development"
hot_reload: true
template: "./templates/web_template"
requirements_file: "./additional_requirements.txt"
```

> In the GUI, use **Config Maker** to create this without hand-editing YAML. Lists are comma-separated; env vars use `KEY=VALUE` comma-pairs.

---

## 🔍 Health, Validate, Fix

```bash
pyrunner doctor
pyrunner --validate-env my_env
pyrunner --fix-env my_env
```

In the GUI, use **Doctor** and **Validate** from the Advanced toolbar.

---

## 📦 Package Management

```bash
# Add packages
pyrunner install flask
pyrunner install "requests>=2.31.0" --env my_env

# Remove packages
pyrunner remove oldlib --env my_env
```

In the GUI Advanced view, use the **Package** field + **Add/Remove**.

---

## 🐚 Shells & Envs

```bash
# Shell into an env
pyrunner shell my_env

# List environments
pyrunner --list-envs

# Reset or clone
pyrunner --reset my_env
pyrunner --clone-env src_env dst_env
```

---

## 🐛 Troubleshooting

* **GUI won’t open** → `pip3 install PyQt6`
* **Watch not working** → `pip3 install watchdog`
* **Permission errors** → choose a writable `--env` path (avoid sudo inside venvs)
* **Conflicts** → `pyrunner --fix-env my_env`

Enable debug output:

```bash
pyrunner run app.py --debug
```

---

## 🤝 Contributing

1. Fork → branch → PR
2. Include tests where possible
3. Test both CLI and GUI paths

Dev setup:

```bash
pip3 install watchdog pyyaml pytest black mypy PyQt6
python3 -m pytest tests/
black pyrunner.py
mypy pyrunner.py
python3 pyrunner.py --gui
```

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 📞 Support

* Issues: GitHub Issues
* Discussions: GitHub Discussions
* Wiki: Project Wiki

---

## 📊 Project Stats

* Version: 2.0.0
* Python: 3.7+
* Modes: CLI + GUI
* Status: Active

---

## 🧾 Quick Reference

```bash
# GUI
pyrunner --gui
pyrunner-gui

# Smart run
pyrunner run script.py

# Dev with reload
pyrunner run server.py --watch

# Profiles
pyrunner run app.py --profile production

# Packages
pyrunner install flask
pyrunner remove flask --env my_env

# Health
pyrunner doctor
pyrunner --validate-env my_env
pyrunner --fix-env my_env
```

**Made with ❤️ by the PyRunner Team**
