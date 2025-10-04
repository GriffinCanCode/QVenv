#!/bin/bash

# install.sh - Install qvenv globally on your system

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "Installing qvenv..."
echo "=================================================="

# Get the absolute path to the qvenv.py script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QVENV_SCRIPT="$SCRIPT_DIR/qvenv.py"

# Check if qvenv.py exists
if [ ! -f "$QVENV_SCRIPT" ]; then
    echo -e "${RED}Error: qvenv.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Make qvenv.py executable
echo "Making qvenv.py executable..."
chmod +x "$QVENV_SCRIPT"

# Determine the target directory
if [ -w "/usr/local/bin" ]; then
    TARGET_DIR="/usr/local/bin"
elif [ -d "$HOME/.local/bin" ]; then
    TARGET_DIR="$HOME/.local/bin"
else
    # Create ~/.local/bin if it doesn't exist
    mkdir -p "$HOME/.local/bin"
    TARGET_DIR="$HOME/.local/bin"
fi

SYMLINK_PATH="$TARGET_DIR/qvenv"

# Check if symlink already exists
if [ -L "$SYMLINK_PATH" ]; then
    echo -e "${YELLOW}Symlink already exists at $SYMLINK_PATH${NC}"
    echo "Removing old symlink..."
    rm "$SYMLINK_PATH"
elif [ -e "$SYMLINK_PATH" ]; then
    echo -e "${RED}Error: A file (not a symlink) already exists at $SYMLINK_PATH${NC}"
    echo "Please remove it manually and try again."
    exit 1
fi

# Create the symlink
echo "Creating symlink: $SYMLINK_PATH -> $QVENV_SCRIPT"
ln -s "$QVENV_SCRIPT" "$SYMLINK_PATH"

# Verify the symlink was created successfully
if [ -L "$SYMLINK_PATH" ]; then
    echo -e "${GREEN}✓ Symlink created successfully!${NC}"
else
    echo -e "${RED}Error: Failed to create symlink${NC}"
    exit 1
fi

# Check if TARGET_DIR is in PATH
if [[ ":$PATH:" != *":$TARGET_DIR:"* ]]; then
    echo ""
    echo -e "${YELLOW}WARNING: $TARGET_DIR is not in your PATH${NC}"
    echo ""
    echo "Add the following line to your shell configuration file:"
    echo "  (~/.bashrc, ~/.zshrc, or ~/.profile)"
    echo ""
    echo "  export PATH=\"\$PATH:$TARGET_DIR\""
    echo ""
    echo "Then reload your shell:"
    echo "  source ~/.bashrc  # or ~/.zshrc"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}Installation complete!${NC}"
echo "=================================================="
echo ""
echo "You can now use qvenv commands:"
echo "  qvenv make [path]    - Create a new virtual environment"
echo "  qvenv activate       - Activate nearest virtual environment"
echo "  qvenv deactivate     - Show deactivation instructions"
echo "  qvenv install        - Install requirements in existing venv"
echo "  qvenv build          - Install requirements in existing venv (alias)"
echo "  qvenv remake         - Rebuild the venv with fresh packages"
echo ""
echo "Try running: qvenv --help"
echo "=================================================="

