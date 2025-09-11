# 📌 PyRunner Summary  

**Purpose:**  
PyRunner is a Python virtual environment and script runner that automates environment creation, dependency installation, and script execution.  

**Key Features:**  
- Auto-detects configs (`requirements.txt` or `config.yaml`)  
- Hot reloading (`--watch`)  
- One-command execution: `pyrunner run script.py`  
- Package management (`install`, `remove`)  
- Environment tools: clone, reset, cleanup, validate, doctor  
- Profiles (dev, test, prod) via YAML configs  
- Lock files for reproducible builds  

**Check install**
Check install: `pyrunner --version`  
```

**Quick Start:**  
```bash
pyrunner run script.py              # auto environment
pyrunner run app.py flask requests  # with dependencies
pyrunner run server.py --watch      # with hot reload
```

**Common Commands:**  
- Run script: `pyrunner run script.py`  
- Install packages: `pyrunner install flask`  
- Remove packages: `pyrunner remove flask`  
- Launch shell: `pyrunner shell my_env`  
- Diagnose: `pyrunner doctor my_env`  
- Cleanup old envs: `pyrunner --cleanup-envs 30`  

**Profiles (YAML):**  
```bash
pyrunner run app.py --profile development
pyrunner run app.py --profile production
```

**Debug & Fix:**  
- Verbose errors: `--debug`  
- Auto-fix: `--fix-env my_env`  
- Reset: `--reset my_env`  

**Best Use Cases:**  
- Pen-testing / CTF environments  
- Data science experiments  
- Shared/team environments  
- Quick reproducible setups  

**--HELP**
usage: pyrunner [-h] [-f FILE] [-c CONFIG] [-l LOCATION] [--env ENV] [-p] [-e EXTRA]
                [--log [LOCATION [FILENAME ...]]] [--watch] [--watch-deps] [--reset LOCATION] [--force-update]
                [--list-envs] [--cleanup-envs DAYS] [--clone-env SOURCE TARGET] [--validate-env ENV_PATH]
                [--fix-env ENV_PATH] [--health-check] [--debug] [--version]
                {run,install,remove,shell,doctor} ...

PyRunner - Advanced Python Virtual Environment Manager

positional arguments:
  {run,install,remove,shell,doctor}
                        Quick commands
    run                 Run script with smart defaults
    install             Add package to environment
    remove              Remove package from environment
    shell               Launch shell in environment
    doctor              Diagnose environment issues

options:
  -h, --help            show this help message and exit
  -f, --file FILE       Python script to run
  -c, --config CONFIG   Configuration file (requirements.txt or .yaml)
  -l, --location LOCATION
                        Virtual environment folder name (deprecated, use --env)
  --env ENV             Virtual environment path (can be shared between scripts)
  -p, --pid             Run as background process with PID tracking
  -e, --extra EXTRA     Arguments to pass to target script (e.g., "[-p 8000 --debug]")
  --log [LOCATION [FILENAME ...]]
                        Enable logging: --log [location] [filename]
  --watch               Enable hot reloading (restart on file changes)
  --watch-deps          Watch dependency files for changes
  --reset LOCATION      Reset virtual environment at specified location
  --force-update        Force update dependencies even if they appear unchanged
  --list-envs           List all PyRunner environments
  --cleanup-envs DAYS   Cleanup environments unused for specified days
  --clone-env SOURCE TARGET
                        Clone environment from source to target
  --validate-env ENV_PATH
                        Validate environment integrity
  --fix-env ENV_PATH    Auto-fix environment issues
  --health-check        Check health of all environments
  --debug               Enable debug mode with verbose error messages
  --version             show program's version number and exit

Examples:
  pyrunner run script.py                           # Smart run with auto-detection
  pyrunner run script.py --watch                   # Run with hot reloading
  pyrunner install flask                           # Add package to current env
  pyrunner shell my_env                           # Launch shell in environment
  pyrunner doctor                                 # Diagnose all environments
  pyrunner -f app.py -c config.yaml --env shared  # Traditional usage

**Installation:**  
```bash
# Download
git clone https://github.com/emaldos/PyRunner.git
cd PyRunner

# Make it executable and global
chmod +x pyrunner.py
sudo ln -s $(pwd)/pyrunner.py /usr/local/bin/pyrunner

# Install dependencies
sudo apt install python3-pip python3-venv python3-yaml
pip3 install watchdog pyyaml

# Verify install
pyrunner --version
