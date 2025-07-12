#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import platform
from datetime import datetime
import shutil

def log(message):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}")

def find_venv_directory():
    """Find virtual environment directory in current directory."""
    # Common virtual environment directory names
    venv_names = ['.venv', 'venv', '.env', 'env', 'virtualenv', '.virtualenv']
    
    current_dir = os.getcwd()
    log(f"Searching for virtual environment in: {current_dir}")
    
    for venv_name in venv_names:
        venv_path = os.path.join(current_dir, venv_name)
        if os.path.exists(venv_path):
            # Check if it's actually a virtual environment
            if os.name == 'nt':  # Windows
                activate_script = os.path.join(venv_path, 'Scripts', 'activate')
                python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
            else:  # Unix/MacOS
                activate_script = os.path.join(venv_path, 'bin', 'activate')
                python_exe = os.path.join(venv_path, 'bin', 'python')
            
            if os.path.exists(activate_script) or os.path.exists(python_exe):
                log(f"Found virtual environment: {venv_name}")
                return venv_path, venv_name
    
    return None, None

def activate_venv():
    """Activate the virtual environment."""
    venv_path, venv_name = find_venv_directory()
    
    if not venv_path:
        log("Error: No virtual environment found in current directory")
        log("Searched for: .venv, venv, .env, env, virtualenv, .virtualenv")
        return False
    
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
        if not os.path.exists(activate_script):
            activate_script = os.path.join(venv_path, 'Scripts', 'activate')
        
        if os.path.exists(activate_script):
            log("=" * 60)
            log(f"Activating virtual environment: {venv_name}")
            log("=" * 60)
            log("On Windows, run this command:")
            log(f"  {activate_script}")
            log("=" * 60)
            return True
        else:
            log(f"Error: Activation script not found at {activate_script}")
            return False
    else:  # Unix/MacOS
        activate_script = os.path.join(venv_path, 'bin', 'activate')
        
        if os.path.exists(activate_script):
            log("=" * 60)
            log(f"Activating virtual environment: {venv_name}")
            log("=" * 60)
            
            # Create a temporary shell script that can be sourced
            temp_script = "/tmp/qvenv_activate.sh"
            try:
                with open(temp_script, 'w') as f:
                    f.write(f"#!/bin/bash\n")
                    f.write(f"source {activate_script}\n")
                    f.write(f"echo 'Virtual environment {venv_name} activated!'\n")
                    f.write(f"echo 'Python: '$(which python)\n")
                    f.write(f"echo 'Pip: '$(which pip)\n")
                
                os.chmod(temp_script, 0o755)
                
                log("To activate the virtual environment, run:")
                log(f"  source {temp_script}")
                log("")
                log("Or manually run:")
                log(f"  source {venv_name}/bin/activate")
                log("=" * 60)
                
                # Also print just the source command for easy copying
                print(f"\n# Copy and paste this command:")
                print(f"source {activate_script}")
                
                return True
            except Exception as e:
                log(f"Error creating activation script: {str(e)}")
                log("Manual activation command:")
                log(f"  source {activate_script}")
                return True
        else:
            log(f"Error: Activation script not found at {activate_script}")
            return False

def get_latest_python_version():
    """Get the latest stable Python version installed on the system."""
    log("Checking for latest stable Python version...")
    
    try:
        # Try python3 --version first
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip().split()[1]
            log(f"Found Python {version}")
            return "python3", version
    except Exception as e:
        log(f"Error checking python3 version: {str(e)}")
    
    # If python3 fails, try python
    try:
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip().split()[1]
            log(f"Found Python {version}")
            return "python", version
    except Exception as e:
        log(f"Error checking python version: {str(e)}")
    
    return None, None

def create_venv(path, python_cmd):
    """Create a virtual environment at the specified path."""
    log(f"Creating virtual environment at {path}...")
    
    try:
        # Check if venv module is available
        result = subprocess.run(
            [python_cmd, "-m", "venv", "--help"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            log("Error: Python venv module not available.")
            log("Please install it with: pip install venv")
            return False
            
        # Create the virtual environment
        result = subprocess.run(
            [python_cmd, "-m", "venv", path],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            log(f"Error creating virtual environment: {result.stderr}")
            return False
            
        # Print activation instructions
        if os.name == 'nt':  # Windows
            activate_cmd = f"{os.path.join(path, 'Scripts', 'activate')}"
        else:  # Unix/MacOS
            activate_cmd = f"source {os.path.join(path, 'bin', 'activate')}"
            
        log("=" * 60)
        log("Virtual environment created successfully!")
        log("=" * 60)
        log(f"To activate, run:")
        log(f"  {activate_cmd}")
        log("=" * 60)
        
        return True
    except Exception as e:
        log(f"Error creating virtual environment: {str(e)}")
        return False

def install_requirements(venv_path):
    """Detect and install requirements file in the virtual environment."""
    log("Checking for requirements file...")
    
    # Common requirements file names
    req_files = ["requirements.txt", "requirements.pip"]
    
    # Find the first existing requirements file
    req_file = None
    for file in req_files:
        if os.path.exists(file):
            req_file = file
            break
    
    if not req_file:
        log("No requirements file found.")
        return False
    
    log(f"Found requirements file: {req_file}")
    log("Installing requirements...")
    
    # Get pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_path, 'Scripts', 'pip')
    else:  # Unix/MacOS
        pip_path = os.path.join(venv_path, 'bin', 'pip')
    
    try:
        # Install requirements
        result = subprocess.run(
            [pip_path, "install", "-r", req_file],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            log(f"Error installing requirements: {result.stderr}")
            return False
        
        log("Requirements installed successfully!")
        return True
    except Exception as e:
        log(f"Error installing requirements: {str(e)}")
        return False

def create_symlink():
    """Create a symlink to the script in a directory that's in the user's PATH."""
    script_path = os.path.abspath(__file__)
    
    if os.name == 'nt':  # Windows
        log("Symlink creation on Windows requires administrator privileges")
        log("Please manually add this script to your PATH")
        return False
    else:  # Unix/MacOS
        # Common locations for executables
        bin_dirs = ['/usr/local/bin', os.path.expanduser('~/.local/bin')]
        
        # Check which directory exists and is in PATH
        target_dir = None
        for d in bin_dirs:
            if os.path.exists(d) and d in os.environ.get('PATH', '').split(':'):
                target_dir = d
                break
        
        # If no suitable directory found, use ~/.local/bin and create if necessary
        if not target_dir:
            target_dir = os.path.expanduser('~/.local/bin')
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                log(f"Created directory: {target_dir}")
                log(f"Remember to add {target_dir} to your PATH")
        
        # Create the symlink
        symlink_path = os.path.join(target_dir, 'qvenv')
        
        # Check if symlink already exists
        if os.path.exists(symlink_path):
            log(f"Symlink already exists at {symlink_path}")
            return True
        
        try:
            os.symlink(script_path, symlink_path)
            os.chmod(symlink_path, 0o755)  # Make executable
            log(f"Symlink created at {symlink_path}")
            
            # Check if target_dir is in PATH
            if target_dir not in os.environ.get('PATH', '').split(':'):
                log(f"NOTE: {target_dir} is not in your PATH")
                if target_dir == os.path.expanduser('~/.local/bin'):
                    log("Consider adding it with: export PATH=$PATH:~/.local/bin")
            
            return True
        except Exception as e:
            log(f"Error creating symlink: {str(e)}")
            return False

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Quick tool to setup a Python virtual environment with the latest stable version"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create subparser for the activate command
    activate_parser = subparsers.add_parser('activate', help='Activate virtual environment in current directory')
    
    # Create subparser for the install command
    install_parser = subparsers.add_parser('install', help='Install qvenv globally')
    
    # Default create command (when no subcommand is specified)
    parser.add_argument(
        "path", 
        nargs="?", 
        default="venv",
        help="Path for the virtual environment (default: ./venv)"
    )
    parser.add_argument(
        "-f", "--force", 
        action="store_true",
        help="Force recreation if the environment already exists"
    )
    parser.add_argument(
        "--complete", 
        action="store_true",
        help="Detect and install requirements after creating the environment"
    )
    
    args = parser.parse_args()
    
    # Handle subcommands
    if args.command == 'activate':
        success = activate_venv()
        return 0 if success else 1
    elif args.command == 'install':
        success = create_symlink()
        return 0 if success else 1

    # Default behavior: create virtual environment
    # Make path absolute if it's relative
    path = os.path.abspath(args.path)
    
    # Check if the directory already exists
    if os.path.exists(path):
        if args.force:
            log(f"Removing existing directory: {path}")
            try:
                shutil.rmtree(path)
            except Exception as e:
                log(f"Error removing existing directory: {str(e)}")
                return 1
        else:
            log(f"Error: Directory already exists: {path}")
            log("Use -f/--force to force recreation")
            return 1
    
    # Get the latest Python version
    python_cmd, version = get_latest_python_version()
    if not python_cmd:
        log("Error: Could not find Python installation")
        return 1
        
    # Create the virtual environment
    success = create_venv(path, python_cmd)
    if not success:
        return 1
    
    # Install requirements if --complete is specified
    if args.complete:
        install_success = install_requirements(path)
        if not install_success:
            log("Warning: Failed to install requirements")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 