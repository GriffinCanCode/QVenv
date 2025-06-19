# QVenv - Quick Python Virtual Environment Manager

A simple, efficient tool for creating Python virtual environments with automatic requirements detection and installation.

## 🚀 Features

- **Automatic Python Detection**: Finds the latest stable Python version on your system
- **Smart Requirements Installation**: Detects and installs from `requirements.txt` or `requirements.pip`
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Global Installation**: Easy symlink creation for system-wide access
- **Force Recreation**: Option to recreate existing environments
- **Comprehensive Logging**: Timestamped output for better debugging

## 📦 Installation

### Quick Install
```bash
# Clone and make executable
git clone https://github.com/GriffinCanCode/QVenv.git
cd QVenv
chmod +x qvenv.py

# Create global symlink (optional)
python3 qvenv.py --install
```

### Manual Install
```bash
# Copy to a directory in your PATH
cp qvenv.py /usr/local/bin/qvenv
chmod +x /usr/local/bin/qvenv
```

## 🛠️ Usage

### Basic Usage
```bash
# Create virtual environment in ./venv
qvenv

# Create virtual environment in custom path
qvenv my_project_env

# Force recreate existing environment
qvenv -f venv

# Create environment and install requirements
qvenv --complete my_env
```

### Command Options

| Option | Description |
|--------|-------------|
| `path` | Path for the virtual environment (default: `./venv`) |
| `-f, --force` | Force recreation if environment already exists |
| `--install` | Create symlink in PATH for global access |
| `--complete` | Auto-detect and install requirements after creation |

### Examples

```bash
# Standard workflow
qvenv project_env
source project_env/bin/activate  # Unix/macOS
# or
project_env\Scripts\activate     # Windows

# Complete setup with requirements
qvenv --complete --force production_env

# Global installation
qvenv --install
```

## 🔧 Requirements Detection

QVenv automatically searches for and installs from:
- `requirements.txt`
- `requirements.pip`

The tool will find the first available requirements file and install all packages in the newly created virtual environment.

## 🖥️ Platform Support

### Unix/macOS
- Uses `python3` command by default
- Activation: `source venv/bin/activate`
- Symlink location: `~/.local/bin/qvenv` or `/usr/local/bin/qvenv`

### Windows
- Falls back to `python` if `python3` unavailable
- Activation: `venv\Scripts\activate`
- Manual PATH addition required

## 📋 Prerequisites

- Python 3.6 or higher
- `venv` module (usually included with Python)
- Write permissions for target directory

## 🔍 Troubleshooting

### Common Issues

**"Python venv module not available"**
```bash
# Install venv module
pip install venv
# or on some systems
python3 -m pip install --user virtualenv
```

**"Permission denied" on symlink creation**
```bash
# Run with appropriate permissions
sudo python3 qvenv.py --install
# or manually copy to PATH directory
```

**Virtual environment not activating**
- Ensure you're using the correct activation command for your platform
- Check that the virtual environment was created successfully
- Verify Python installation and PATH configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Tools

Part of the [GSuite](https://github.com/GriffinCanCode/GSuite) collection of development tools. 