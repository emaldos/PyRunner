# 🚀 PyRunner

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/emaldos/PyRunner.svg)](https://github.com/emaldos/PyRunner/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/emaldos/PyRunner.svg)](https://github.com/emaldos/PyRunner/issues)

**The Ultimate Python Virtual Environment Manager and Script Runner** 🐍✨

PyRunner simplifies Python development by intelligently managing virtual environments, dependencies, and script execution. Say goodbye to manual environment setup and hello to effortless Python development!

---

## 🌟 Features

### ⚡ **Smart & Fast**
- 🧠 **Auto-detection** of configuration files
- 🔄 **Hot reloading** with file watching
- 🚀 **Parallel dependency installation**
- 💾 **Intelligent caching** - only updates what changed
- 🔒 **Lock files** for reproducible builds

### 🛠️ **Developer Experience**
- 🎯 **One-command execution** - `pyrunner run script.py`
- 🐚 **Interactive shells** within environments
- 📋 **Configuration profiles** (dev/test/prod)
- 💊 **Auto-fix** corrupted environments
- 🏥 **Health diagnostics** for all environments

### 🔧 **Advanced Management**
- 📊 **Environment analytics** and cleanup suggestions
- 🎭 **Environment cloning** and templates
- 🔍 **Smart error messages** with solutions
- 📦 **Package management** (install/remove/update)

---

## 📥 Installation

### **Option 1: Quick Setup (Recommended)**
```bash
# Download PyRunner
git clone https://github.com/emaldos/PyRunner.git
cd PyRunner

# Make it executable
sudo chmod +x pyrunner.py

# Add to system PATH (use PyRunner anywhere)
sudo ln -s $(pwd)/pyrunner.py /usr/local/bin/pyrunner
```

### **Option 2: Manual Installation**
```bash
# Download the script
wget https://raw.githubusercontent.com/emaldos/PyRunner/main/pyrunner.py

# Make executable
chmod +x pyrunner.py

# Copy to system directory
sudo cp pyrunner.py /usr/local/bin/pyrunner
```

### **Option 3: Alias Method**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'alias pyrunner="/path/to/pyrunner.py"' >> ~/.bashrc
source ~/.bashrc
```

### **Dependencies**
```bash
# Install required system packages
sudo apt update
sudo apt install python3-pip python3-venv python3-yaml

# Install Python dependencies for hot reloading
pip3 install watchdog pyyaml
```

### **Verify Installation**
```bash
pyrunner --version
# Should output: PyRunner 2.0.0
```

---

## 🚀 Quick Start

### **Your First Script (30 seconds)**
```bash
# Just run it! PyRunner handles everything
pyrunner run your_script.py

# Or with dependencies
pyrunner run app.py flask requests

# With hot reloading for development
pyrunner run server.py --watch
```

That's it! 🎉 PyRunner automatically:
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Runs your script
- ✅ Caches everything for next time

---

## 📖 Complete Usage Guide

### 🎯 **Quick Commands (Modern Syntax)**

#### **Smart Run**
```bash
# Auto-detect configuration and run
pyrunner run script.py

# Specify packages if no config file exists
pyrunner run app.py flask pandas numpy

# Use specific environment
pyrunner run script.py --env my_environment

# Use configuration profile
pyrunner run app.py --profile production

# Enable hot reloading (auto-restart on file changes)
pyrunner run server.py --watch
```

#### **Package Management**
```bash
# Add packages to environment
pyrunner install flask
pyrunner install "requests>=2.25.0"
pyrunner install numpy pandas matplotlib

# Add to specific environment
pyrunner install flask --env web_development

# Remove packages
pyrunner remove unused-package
pyrunner remove old-library --env specific_env
```

#### **Environment Interaction**
```bash
# Launch interactive shell in environment
pyrunner shell my_env
pyrunner shell /path/to/environment

# List all environments with details
pyrunner --list-envs
```

#### **Health & Diagnostics**
```bash
# Check all environments
pyrunner doctor

# Check specific environment
pyrunner doctor my_env

# Auto-fix environment issues
pyrunner --fix-env corrupted_env

# Quick health check
pyrunner --health-check

# Validate environment integrity
pyrunner --validate-env my_env
```

### 🏗️ **Traditional Syntax (Full Control)**

#### **Basic Execution**
```bash
# Traditional mode with full control
pyrunner -f script.py -c requirements.txt

# Specify custom environment location
pyrunner -f script.py -c requirements.txt --env /path/to/environment

# Legacy location parameter (still supported)
pyrunner -f script.py -c requirements.txt --location my_env
```

#### **Advanced Execution Options**
```bash
# Background execution with PID tracking
pyrunner -f server.py -c requirements.txt --pid

# Pass arguments to target script
pyrunner -f app.py -c requirements.txt -e "[--port 8000 --debug]"
pyrunner -f script.py -c requirements.txt -e "arg1 arg2 --flag"

# Force dependency update
pyrunner -f script.py -c requirements.txt --force-update

# Enable hot reloading
pyrunner -f app.py -c requirements.txt --watch
pyrunner -f server.py -c requirements.txt --watch-deps

# Debug mode with verbose errors
pyrunner -f script.py -c requirements.txt --debug
```

#### **Logging Options**
```bash
# Enable logging with default location
pyrunner -f script.py -c requirements.txt --log

# Specify log directory
pyrunner -f script.py -c requirements.txt --log ./logs/

# Specify log directory and filename
pyrunner -f script.py -c requirements.txt --log ./logs/ app.log
```

### 📂 **Environment Location Management**

#### **Default Behavior**
```bash
# Creates environment in current directory as "script_env"
pyrunner -f script.py -c requirements.txt
# Creates: ./script_env/
```

#### **Custom Locations**
```bash
# Relative path
pyrunner -f script.py -c requirements.txt --env my_custom_env
# Creates: ./my_custom_env/

# Absolute path
pyrunner -f script.py -c requirements.txt --env /opt/python_envs/web_app
# Creates: /opt/python_envs/web_app/

# Home directory
pyrunner -f script.py -c requirements.txt --env ~/environments/data_science
# Creates: /home/user/environments/data_science/

# Relative to parent directory
pyrunner -f script.py -c requirements.txt --env ../shared_envs/api_backend
# Creates: ../shared_envs/api_backend/
```

#### **Shared Environments**
```bash
# Multiple scripts sharing the same environment
pyrunner -f api_server.py -c web_requirements.txt --env /shared/web_stack
pyrunner -f background_worker.py -c web_requirements.txt --env /shared/web_stack
pyrunner -f database_migrator.py -c web_requirements.txt --env /shared/web_stack
```

#### **Organizational Strategies**
```bash
# By project type
pyrunner -f webapp.py -c requirements.txt --env ~/envs/web_development/
pyrunner -f analysis.py -c requirements.txt --env ~/envs/data_science/
pyrunner -f scanner.py -c requirements.txt --env ~/envs/security_tools/

# Centralized management
pyrunner -f script1.py -c req.txt --env /opt/python_environments/project_alpha
pyrunner -f script2.py -c req.txt --env /opt/python_environments/project_beta

# Team environments
pyrunner -f team_script.py -c requirements.txt --env /mnt/shared/team_envs/backend
```

### 🔧 **Environment Management Commands**

#### **Environment Operations**
```bash
# Clone environment
pyrunner --clone-env source_environment target_environment
pyrunner --clone-env /path/to/source /path/to/target

# Reset (delete and recreate) environment
pyrunner --reset my_environment
pyrunner --reset /path/to/environment

# Cleanup unused environments (older than X days)
pyrunner --cleanup-envs 30
pyrunner --cleanup-envs 7
```

#### **Environment Information**
```bash
# List all environments with statistics
pyrunner --list-envs

# Validate specific environment
pyrunner --validate-env my_environment

# Get detailed environment information
pyrunner doctor my_environment
```

### 🔥 **Hot Reloading & File Watching**

#### **Basic Hot Reloading**
```bash
# Watch Python script for changes
pyrunner run app.py --watch
pyrunner -f server.py -c requirements.txt --watch

# Also watch dependency files
pyrunner run app.py --watch-deps
pyrunner -f app.py -c requirements.txt --watch-deps
```

#### **What Gets Watched**
- 🐍 **Python script files** → Auto-restart script
- 📦 **requirements.txt** → Update dependencies + restart
- ⚙️ **config.yaml** → Reload configuration + restart

#### **Hot Reload Behavior**
```bash
# When you save the Python script:
🔄 Script changed: app.py
⏹️  Stopping current process...
🚀 Restarting script...
✅ Script restarted (PID: 12345)

# When you modify requirements.txt:
📦 Dependencies changed: requirements.txt
⏹️  Stopping current process...
📦 Updating dependencies...
✅ Dependencies updated
🚀 Restarting script...
✅ Script restarted (PID: 12346)
```

---

## ⚙️ Configuration

### 📄 **Simple Requirements.txt**
```txt
# Basic requirements.txt
flask>=2.0.0
requests
pandas
numpy>=1.20.0
gunicorn
```

### 🎛️ **Advanced YAML Configuration**

#### **Basic YAML Config**
```yaml
# config.yaml
python_version: "3.11"

dependencies:
  - "flask>=2.0.0"
  - "requests"
  - "pandas"

dev_dependencies:
  - "pytest"
  - "black"
  - "mypy"

environment_variables:
  DATABASE_URL: "postgresql://localhost/mydb"
  SECRET_KEY: "your-secret-key"
  DEBUG: "true"
```

#### **Advanced YAML with Profiles**
```yaml
# config.yaml
python_version: "3.11"

# Profile-based configuration
profiles:
  development:
    dependencies:
      - "flask[dev]"
      - "pytest"
      - "black"
      - "mypy"
      - "flask-debugtoolbar"
    env_vars:
      DEBUG: "true"
      LOG_LEVEL: "debug"
      DATABASE_URL: "sqlite:///dev.db"
  
  testing:
    dependencies:
      - "flask"
      - "pytest"
      - "coverage"
      - "pytest-cov"
    env_vars:
      TESTING: "true"
      DATABASE_URL: "sqlite:///:memory:"
  
  production:
    dependencies:
      - "flask"
      - "gunicorn"
      - "psycopg2-binary"
      - "redis"
    env_vars:
      DEBUG: "false"
      LOG_LEVEL: "info"
      DATABASE_URL: "postgresql://prod_server/mydb"

# Active profile (change this to switch environments)
active_profile: "development"

# Base dependencies (always installed regardless of profile)
dependencies:
  - "requests"
  - "python-dotenv"

# Additional development dependencies
dev_dependencies:
  - "ipython"
  - "jupyter"

# Global environment variables
environment_variables:
  SECRET_KEY: "global-secret-key"
  APP_NAME: "MyApplication"

# Hot reloading configuration
hot_reload: true

# Use environment template
template: "./templates/web_template"

# External requirements file (optional)
requirements_file: "./additional_requirements.txt"
```

#### **Profile Usage Examples**
```bash
# Use development profile
pyrunner run app.py --profile development

# Use production profile
pyrunner run app.py --profile production

# Use testing profile
pyrunner run tests.py --profile testing

# Traditional syntax with profiles
pyrunner -f app.py -c config.yaml --profile production
```

### 🎭 **Profile System Benefits**
- 🔄 **Easy switching** between environments
- 📦 **Different dependencies** per environment
- 🌍 **Environment-specific variables**
- ⚡ **No config file changes** needed
- 🎯 **Targeted configurations** for specific use cases

---

## 🔍 **Error Handling & Debugging**

### 🚨 **Smart Error Messages**
PyRunner provides intelligent error messages with actionable solutions:

```bash
❌ Error: Failed to install flask==2.3.0
📍 Context: my_project_env
💡 Suggestions:
   • There's a dependency version conflict
   • Try: pyrunner --fix-env my_project_env to resolve conflicts
   • Or use: --force-update to override version constraints
```

```bash
❌ Error: Script file not found: /path/to/script.py
📍 Context: /path/to/script.py
💡 Suggestions:
   • Check if the file exists: ls -la /path/to/script.py
   • Make sure you're in the correct directory
   • Use absolute path if the script is in another directory
```

### 🔧 **Debug Mode**
```bash
# Enable verbose debugging
pyrunner run script.py --debug
pyrunner -f script.py -c requirements.txt --debug

# Debug mode shows:
# - Full error tracebacks
# - Detailed dependency resolution
# - Environment validation steps
# - Configuration parsing details
```

### 🏥 **Health Diagnostics**

#### **System-Wide Health Check**
```bash
pyrunner doctor

# Output example:
🏥 PyRunner Health Check
==================================================
🚨 Critical Issues:
   • web_env: Python executable missing
   • old_env: Environment directory missing

⚠️  Warnings:
   • data_env: Dependency conflicts detected
   • ml_env: Could not check dependencies

💡 Suggestions:
   • web_env: Large environment (245.2MB) - consider cleanup
   • old_env: Unused for 45 days - consider removal
```

#### **Specific Environment Diagnosis**
```bash
pyrunner doctor my_environment

# Output example:
🔍 Diagnosing environment: my_environment
✅ Environment directory exists
✅ Python executable found and functional
✅ Pip executable found
⚠️  Dependency conflicts detected
💡 Run: pyrunner --fix-env my_environment
```

#### **Auto-Fix Capabilities**
```bash
# Automatically fix common issues
pyrunner --fix-env corrupted_environment

# Auto-fix performs:
# - Recreates corrupted Python executables
# - Fixes dependency conflicts
# - Cleans pip cache
# - Repairs metadata files
```

---

## 📊 **Environment Analytics**

### 📈 **Environment Listing**
```bash
pyrunner --list-envs

# Output:
Name                 Size (MB)  Dependencies Scripts  Last Used   
---------------------------------------------------------------------------
web_app_env         45.2       12           3        2025-08-20
shared_env          78.1       25           5        2025-08-19
ml_project_env      156.7      45           2        2025-08-15
data_science_env    234.5      67           8        2025-08-10
old_test_env        12.3       5            1        2025-07-01
```

### 🧹 **Environment Cleanup**
```bash
# Clean environments unused for 30+ days
pyrunner --cleanup-envs 30

# Clean environments unused for 7+ days
pyrunner --cleanup-envs 7

# Output example:
Cleaned up 2 unused environments: old_test_env, abandoned_project_env
```

### 📊 **Environment Details**
```bash
pyrunner --validate-env my_environment

# Output:
✅ Environment my_environment is valid and healthy.
   Size: 78.1 MB
   Dependencies: 25
   Scripts: 5 (app.py, worker.py, migrate.py, test.py, cli.py)
   Last used: 2025-08-19 14:30
```

---

## 🔒 **Lock Files & Reproducibility**

### 📋 **Automatic Lock File Generation**
PyRunner automatically generates `requirements.lock` files for reproducible builds:

```json
{
  "generated_at": 1692547200,
  "python_version": "3.11",
  "entries": [
    {
      "name": "flask",
      "version": "2.3.2",
      "hash": "",
      "dependencies": []
    },
    {
      "name": "requests", 
      "version": "2.31.0",
      "hash": "",
      "dependencies": []
    }
  ]
}
```

### 🔄 **Lock File Benefits**
- ✅ **Exact version reproduction** across environments
- ✅ **Faster subsequent installs** (uses cached versions)
- ✅ **Dependency conflict detection**
- ✅ **Build reproducibility** for team development

### 🚀 **Smart Dependency Management**
```bash
# First run: Installs all dependencies, generates lock file
pyrunner -f app.py -c requirements.txt

# Subsequent runs: Uses lock file for faster installation
pyrunner -f app.py -c requirements.txt

# Force regenerate lock file
pyrunner -f app.py -c requirements.txt --force-update
```

---

## 🎭 **Environment Templates & Cloning**

### 📋 **Environment Cloning**
```bash
# Clone existing environment
pyrunner --clone-env source_environment target_environment

# Clone with absolute paths
pyrunner --clone-env /opt/envs/web_template /opt/envs/new_project

# Clone for team development
pyrunner --clone-env master_environment team_member_environment
```

### 🎨 **Using Templates in Configuration**
```yaml
# config.yaml
template: "./templates/web_development_template"

dependencies:
  - "additional-package"

# The template environment is cloned and then additional packages are installed
```

### 🏗️ **Template Creation Workflow**
```bash
# 1. Create a perfect environment
pyrunner -f setup_script.py -c base_requirements.txt --env perfect_web_env

# 2. Clone it as a template
pyrunner --clone-env perfect_web_env ./templates/web_template

# 3. Use template for new projects
pyrunner -f new_project.py -c config.yaml  # config.yaml references the template
```

---

## 🛡️ **Security & Kali Linux Usage**

### 🔧 **Perfect for Penetration Testing**
```bash
# Isolated environments for security tools
pyrunner -f port_scanner.py -c security_requirements.txt --env /opt/security_envs/reconnaissance
pyrunner -f sql_injection_test.py -c webapp_testing.txt --env /opt/security_envs/web_testing
pyrunner -f network_analyzer.py -c network_tools.txt --env /opt/security_envs/network_analysis
```

### 🎯 **CTF and Competition Usage**
```bash
# Quick setup for CTF challenges
pyrunner run crypto_solver.py pycrypto gmpy2 sage

# Binary analysis environment
pyrunner -f reverse_engineer.py -c binary_analysis.txt --env /opt/ctf_envs/reverse_engineering

# Web exploitation environment
pyrunner -f web_exploit.py -c web_security.txt --env /opt/ctf_envs/web_exploitation
```

### 🔒 **Environment Isolation Benefits**
- 🛡️ **Tool isolation** - Keep different security tools separate
- 🚀 **Fast deployment** - Quick environment setup for specific tasks
- 🔄 **Reproducible setups** - Same environment across team members
- 📊 **Environment tracking** - Monitor tool environments and usage

---

## 📋 **Complete Command Reference**

### 🎯 **Quick Commands**
| Command | Description | Example |
|---------|-------------|---------|
| `run` | Smart run with auto-detection | `pyrunner run app.py` |
| `run --watch` | Run with hot reloading | `pyrunner run server.py --watch` |
| `run --profile` | Run with specific profile | `pyrunner run app.py --profile prod` |
| `install` | Add package to environment | `pyrunner install flask` |
| `remove` | Remove package from environment | `pyrunner remove flask` |
| `shell` | Launch shell in environment | `pyrunner shell my_env` |
| `doctor` | Diagnose environment issues | `pyrunner doctor my_env` |

### 🏗️ **Traditional Arguments**
| Flag | Description | Example |
|------|-------------|---------|
| `-f, --file` | Python script to run | `pyrunner -f script.py` |
| `-c, --config` | Configuration file | `pyrunner -c requirements.txt` |
| `--env` | Environment path | `pyrunner --env /path/to/env` |
| `-e, --extra` | Arguments for target script | `pyrunner -e "[--port 8000]"` |
| `-p, --pid` | Background execution | `pyrunner -p` |
| `--watch` | Enable hot reloading | `pyrunner --watch` |
| `--watch-deps` | Watch dependency files | `pyrunner --watch-deps` |
| `--force-update` | Force dependency update | `pyrunner --force-update` |
| `--debug` | Verbose error messages | `pyrunner --debug` |

### 🔧 **Environment Management**
| Flag | Description | Example |
|------|-------------|---------|
| `--list-envs` | List all environments | `pyrunner --list-envs` |
| `--cleanup-envs` | Clean old environments | `pyrunner --cleanup-envs 30` |
| `--clone-env` | Clone environment | `pyrunner --clone-env src dst` |
| `--validate-env` | Validate environment | `pyrunner --validate-env my_env` |
| `--fix-env` | Auto-fix environment | `pyrunner --fix-env my_env` |
| `--reset` | Reset environment | `pyrunner --reset my_env` |
| `--health-check` | Quick health check | `pyrunner --health-check` |

### 📝 **Logging Options**
| Flag | Description | Example |
|------|-------------|---------|
| `--log` | Enable logging (default location) | `pyrunner --log` |
| `--log DIR` | Log to specific directory | `pyrunner --log ./logs/` |
| `--log DIR FILE` | Log to specific file | `pyrunner --log ./logs/ app.log` |

---

## 💡 **Best Practices & Tips**

### 🎯 **Project Organization**
```bash
# Organize by project type
~/environments/
├── web_development/
├── data_science/
├── machine_learning/
└── security_tools/

# Use descriptive environment names
pyrunner --env ~/environments/web_development/ecommerce_api
pyrunner --env ~/environments/data_science/customer_analysis
```

### 🔄 **Development Workflow**
```bash
# 1. Development with hot reloading
pyrunner run app.py --profile development --watch

# 2. Testing with separate environment
pyrunner run tests.py --profile testing

# 3. Production deployment
pyrunner run app.py --profile production --pid
```

### 📦 **Dependency Management**
```bash
# Add new packages during development
pyrunner install new-package --env development_env

# Update all dependencies
pyrunner -f app.py -c requirements.txt --force-update

# Check for dependency conflicts
pyrunner doctor my_env
```

### 🧹 **Environment Maintenance**
```bash
# Regular health checks
pyrunner --health-check

# Clean up old environments monthly
pyrunner --cleanup-envs 30

# Validate critical environments
pyrunner --validate-env production_env
```

---

## 🌟 **Advanced Use Cases**

### 🏢 **Enterprise Development**
```bash
# Team shared environments
pyrunner -f api.py -c requirements.txt --env /shared/team_envs/backend_api
pyrunner -f worker.py -c requirements.txt --env /shared/team_envs/background_workers

# Environment templates for consistency
pyrunner --clone-env /templates/enterprise_base /projects/new_microservice
```

### 🎓 **Education & Learning**
```bash
# Course-specific environments
pyrunner run lesson1.py --env ~/courses/python_basics/
pyrunner run data_analysis.py --env ~/courses/data_science/

# Workshop environments
pyrunner --clone-env workshop_template student_environment
```

### 🔬 **Research & Data Science**
```bash
# Experiment isolation
pyrunner run experiment_v1.py --env ~/research/experiment_1/
pyrunner run experiment_v2.py --env ~/research/experiment_2/

# Reproducible research
pyrunner -f analysis.py -c research_requirements.txt --force-update
```

### 🎮 **CTF & Security Research**
```bash
# Challenge-specific environments
pyrunner run crypto_challenge.py --env ~/ctf/picoctf/crypto/
pyrunner run web_challenge.py --env ~/ctf/hackthebox/web/

# Tool development
pyrunner run exploit_dev.py --env ~/security_research/exploits/ --watch
```

---

## 🐛 Troubleshooting

### ❌ **Common Issues & Solutions**

#### **Permission Errors**
```bash
# Problem: Permission denied when creating environments
# Solution: Check directory permissions or use different location
pyrunner -f script.py -c requirements.txt --env ~/my_envs/project

# Problem: Cannot install packages
# Solution: Don't use sudo with virtual environments
pyrunner install package  # ✅ Correct
sudo pyrunner install package  # ❌ Wrong
```

#### **Dependency Conflicts**
```bash
# Problem: Package version conflicts
# Solution: Use auto-fix or force update
pyrunner --fix-env my_environment
pyrunner -f script.py -c requirements.txt --force-update
```

#### **Corrupted Environments**
```bash
# Problem: Environment not working after system update
# Solution: Validate and auto-fix
pyrunner --validate-env my_env
pyrunner --fix-env my_env

# Last resort: Reset environment
pyrunner --reset my_env
```

#### **Missing Dependencies**
```bash
# Problem: PyRunner command not found
# Solution: Install system dependencies
sudo apt install python3-pip python3-venv python3-yaml
pip3 install watchdog pyyaml

# Problem: Hot reloading not working
# Solution: Install watchdog
pip3 install watchdog
```

### 🔧 **Debug Steps**
1. **Enable debug mode**: `pyrunner run script.py --debug`
2. **Check environment health**: `pyrunner doctor my_env`
3. **Validate installation**: `pyrunner --validate-env my_env`
4. **Check system dependencies**: `python3 -m venv --help`
5. **Review configuration**: Check your `requirements.txt` or `config.yaml`

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 🚀 **Getting Started**
1. **🍴 Fork** the repository
2. **📥 Clone** your fork: `git clone https://github.com/your-username/PyRunner.git`
3. **🌿 Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **✍️ Make** your changes
5. **🧪 Test** your changes thoroughly
6. **📝 Commit** your changes: `git commit -m 'Add amazing feature'`
7. **📤 Push** to the branch: `git push origin feature/amazing-feature`
8. **🎯 Open** a Pull Request

### 🐛 **Bug Reports**
Found a bug? Please open an issue with:
- 🔍 **Clear description** of the problem
- 📋 **Steps to reproduce** the issue
- 💻 **System information** (OS, Python version)
- 📄 **Configuration files** (if relevant)
- 🖼️ **Screenshots** or error messages

### 💡 **Feature Requests**
Have an idea? We'd love to hear it! Open an issue with:
- 🎯 **Clear description** of the feature
- 💭 **Use case** and benefits
- 🔧 **Implementation suggestions** (optional)
- 📊 **Priority level** (nice-to-have vs critical)

### 🧪 **Development Setup**
```bash
# Clone the repository
git clone https://github.com/emaldos/PyRunner.git
cd PyRunner

# Install development dependencies
pip3 install watchdog pyyaml pytest black mypy

# Run tests
python3 -m pytest tests/

# Format code
black pyrunner.py

# Type checking
mypy pyrunner.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- 🐍 **Python community** for the amazing ecosystem
- 📦 **pip** and **venv** for providing the foundation
- 👥 **Contributors** who make PyRunner better every day
- 💡 **Users** who provide valuable feedback and ideas
- 🛡️ **Security community** for testing and validation

---

## 📞 Support & Community

### 📚 **Documentation**
- 📖 **README**: Complete usage guide (this document)
- 💡 **Examples**: Check the examples throughout this guide
- 🎯 **Command Reference**: See the complete command reference section

### 🆘 **Getting Help**
- 🐛 **Issues**: [GitHub Issues](https://github.com/emaldos/PyRunner/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/emaldos/PyRunner/discussions)
- 📧 **Direct Contact**: Open an issue for questions
- 🌐 **Community**: Join discussions and help others

### 🔗 **Links**
- 🏠 **Homepage**: [GitHub Repository](https://github.com/emaldos/PyRunner)
- 📊 **Issues
