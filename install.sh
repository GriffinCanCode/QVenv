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
QVENV_SHELL_WRAPPER="$SCRIPT_DIR/qvenv.sh"

# Check if qvenv.py exists
if [ ! -f "$QVENV_SCRIPT" ]; then
    echo -e "${RED}Error: qvenv.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Check if qvenv.sh exists
if [ ! -f "$QVENV_SHELL_WRAPPER" ]; then
    echo -e "${RED}Error: qvenv.sh not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$QVENV_SCRIPT"
chmod +x "$QVENV_SHELL_WRAPPER"

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

# Detect shell configuration file
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    else
        SHELL_CONFIG="$HOME/.bash_profile"
    fi
fi

# Auto-configure shell wrapper
if [ -n "$SHELL_CONFIG" ]; then
    QVENV_SOURCE_LINE="# QVenv auto-activation"$'\n'"source \"$QVENV_SHELL_WRAPPER\""
    
    # Check if already configured
    if grep -q "source.*qvenv.sh" "$SHELL_CONFIG" 2>/dev/null; then
        echo -e "${YELLOW}QVenv shell wrapper already configured in $SHELL_CONFIG${NC}"
    else
        echo ""
        echo "Configure automatic activation/deactivation?"
        echo "This will add the following to $SHELL_CONFIG:"
        echo ""
        echo "  $QVENV_SOURCE_LINE"
        echo ""
        read -p "Add to shell config? [Y/n] " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            echo "" >> "$SHELL_CONFIG"
            echo "$QVENV_SOURCE_LINE" >> "$SHELL_CONFIG"
            echo -e "${GREEN}✓ Added to $SHELL_CONFIG${NC}"
            echo ""
            echo "Reload your shell to activate:"
            echo "  source $SHELL_CONFIG"
        else
            echo "Skipped automatic configuration."
            echo ""
            echo "To enable later, add this to $SHELL_CONFIG:"
            echo "  source $QVENV_SHELL_WRAPPER"
        fi
    fi
else
    echo -e "${YELLOW}Could not detect shell config file${NC}"
    echo "Add this to your shell config file manually:"
    echo "  source $QVENV_SHELL_WRAPPER"
fi

echo ""
echo "=================================================="
echo "Usage:"
echo "=================================================="
echo ""
echo "After reloading your shell, these work instantly:"
echo "  qvenv make           - Create a new virtual environment"
echo "  qvenv activate       - Activate venv (instant!)"
echo "  qvenv deactivate     - Deactivate venv (instant!)"
echo "  qvenv install        - Install requirements"
echo "  qvenv remake         - Rebuild the venv"
echo ""
echo "Try running: qvenv --help"
echo "=================================================="

