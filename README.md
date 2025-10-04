# QVenv - Python Virtual Environment Manager

[![PyPI version](https://badge.fury.io/py/qvenv.svg)](https://badge.fury.io/py/qvenv)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qvenv)](https://pypi.org/project/qvenv/)

A command-line tool for managing Python virtual environments with automatic requirements detection and installation.

**PyPI Package:** https://pypi.org/project/qvenv/

## Features

- **Automatic activation/deactivation** (when sourcing `qvenv.sh`)
- **Recursive venv search** (searches up to 5 levels deep in subdirectories)
- Automatic Python version detection
- Requirements file detection and installation (requirements.txt, requirements.pip)
- Cross-platform support (Windows, macOS, Linux)
- Environment recreation and rebuilding
- Timestamped logging
- Compatible with bash and zsh

## Installation

### PyPI Installation (Recommended)

Install qvenv directly from PyPI:

```bash
pip install qvenv
```

or for user installation:

```bash
pip install --user qvenv
```

After installation, the `qvenv` command will be available globally.

**For automatic activation/deactivation (optional):**
Add this line to your `~/.bashrc` or `~/.zshrc`:
```bash
# Enable qvenv auto-activation
eval "$(pip show -f qvenv | grep qvenv.sh | head -1 | awk '{print "source " $NF}')"
```

Or manually find and source `qvenv.sh` from your Python site-packages.

### Development Installation (Recommended for Latest Features)

Clone the repository and install using the Makefile:

```bash
git clone https://github.com/GriffinCanCode/QVenv.git
cd QVenv
make install
```

The installation will:
- Make `qvenv.py` and `qvenv.sh` executable
- Create a symlink in `/usr/local/bin` or `~/.local/bin`
- **Automatically configure your shell** for instant activation/deactivation
- Prompt you before making changes to your shell config

After installation, reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc for bash
```

### Makefile Commands

```bash
make install    # Install qvenv globally
make uninstall  # Remove qvenv completely
make build      # Build distribution packages
make publish    # Publish to PyPI
make clean      # Remove build artifacts
make help       # Show all commands
```

### Manual Installation

```bash
chmod +x qvenv.py qvenv.sh
ln -s "$(pwd)/qvenv.py" /usr/local/bin/qvenv
# Then manually add to your shell config:
echo 'source /path/to/qvenv.sh' >> ~/.zshrc
```

## Usage

### Commands

**qvenv make [path]**
Create a new virtual environment.

```bash
qvenv make                    # Creates ./venv
qvenv make myenv              # Creates ./myenv
qvenv make myenv -f           # Force recreate if exists
qvenv make myenv --complete   # Create and install requirements
```

**qvenv activate**
Activate the nearest virtual environment.

```bash
# If you sourced qvenv.sh (auto-activation enabled):
qvenv activate                    # Activates instantly! ✨

# Without sourcing qvenv.sh:
eval "$(qvenv activate --quiet)"  # Activate with eval
```

**qvenv deactivate**
Deactivate the current virtual environment.

```bash
# If you sourced qvenv.sh (auto-activation enabled):
qvenv deactivate                  # Deactivates instantly! ✨

# Without sourcing qvenv.sh:
eval "$(qvenv deactivate --quiet)"  # Deactivate with eval
```

**qvenv install**
Install requirements from requirements.txt or requirements.pip into the existing virtual environment.

```bash
qvenv install
```

**qvenv build**
Alias for `qvenv install`. Installs requirements into the existing virtual environment.

```bash
qvenv build
```

**qvenv remake**
Remove and recreate the virtual environment with fresh packages from requirements file.

```bash
qvenv remake
```

### Options

#### make command options:
- `path` - Path for the virtual environment (default: venv)
- `-f, --force` - Force recreation if environment already exists
- `--complete` - Detect and install requirements after creation

#### activate/deactivate command options:
- `-q, --quiet` - Output only the command (for use with eval)

## Typical Workflow

### With Auto-Activation (Recommended)
After sourcing `qvenv.sh` in your shell config:

```bash
# Create a new virtual environment
qvenv make

# Activate it instantly
qvenv activate

# Install dependencies
qvenv install

# Later, rebuild environment if needed
qvenv remake

# Deactivate when done
qvenv deactivate
```

### Without Auto-Activation
```bash
# Create a new virtual environment
qvenv make

# Activate with eval
eval "$(qvenv activate --quiet)"

# Install dependencies
qvenv install

# Deactivate with eval
eval "$(qvenv deactivate --quiet)"
```

## Requirements Detection

The tool searches for requirements files in this order:
1. `requirements.txt`
2. `requirements.pip`

The first available file will be used for package installation.

## Platform Support

### Unix and macOS
- Uses `python3` by default
- Activation: `source venv/bin/activate`
- Symlink location: `/usr/local/bin/qvenv` or `~/.local/bin/qvenv`

### Windows
- Falls back to `python` if `python3` is unavailable
- Activation: `venv\Scripts\activate`
- Manual PATH configuration may be required

## Prerequisites

- Python 3.6 or higher
- Python `venv` module (typically included with Python)
- Write permissions for the target directory

## Troubleshooting

### Python venv module not available

```bash
python3 -m pip install --user virtualenv
```

### Permission denied during installation

```bash
sudo ./install.sh
```

Or manually specify a user directory:

```bash
ln -s "$(pwd)/qvenv.py" "$HOME/.local/bin/qvenv"
export PATH="$PATH:$HOME/.local/bin"
```

### Virtual environment not found

qvenv searches the current directory and up to 5 levels deep in subdirectories for:
- `.venv`
- `venv`
- `.env`
- `env`
- `virtualenv`
- `.virtualenv`

Run `qvenv make` to create a new virtual environment if none exists.

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/feature-name`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to the branch (`git push origin feature/feature-name`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Related Tools

Part of the GSuite collection of development tools. 