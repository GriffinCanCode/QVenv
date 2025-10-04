# QVenv - Python Virtual Environment Manager

[![PyPI version](https://badge.fury.io/py/qvenv.svg)](https://badge.fury.io/py/qvenv)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qvenv)](https://pypi.org/project/qvenv/)

A command-line tool for managing Python virtual environments with automatic requirements detection and installation.

**PyPI Package:** https://pypi.org/project/qvenv/

## Features

- Automatic Python version detection
- Requirements file detection and installation (requirements.txt, requirements.pip)
- Cross-platform support (Windows, macOS, Linux)
- Environment activation helpers
- Environment recreation and rebuilding
- Timestamped logging

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

### Development Installation

Clone the repository and use the installation script:

```bash
git clone https://github.com/GriffinCanCode/QVenv.git
cd QVenv
./install.sh
```

The script will automatically:
- Make `qvenv.py` executable
- Create a symlink in `/usr/local/bin` or `~/.local/bin`
- Provide instructions if PATH configuration is needed

### Manual Installation

```bash
chmod +x qvenv.py
ln -s "$(pwd)/qvenv.py" /usr/local/bin/qvenv
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
Display activation instructions for the nearest virtual environment.

```bash
qvenv activate
```

**qvenv deactivate**
Display deactivation instructions.

```bash
qvenv deactivate
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

## Typical Workflow

```bash
# Create a new virtual environment
qvenv make

# Activate it (copy and run the command shown)
source venv/bin/activate

# Install dependencies
qvenv install

# Later, rebuild environment if needed
qvenv remake
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

Ensure you're in a directory containing one of these:
- `.venv`
- `venv`
- `.env`
- `env`
- `virtualenv`
- `.virtualenv`

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