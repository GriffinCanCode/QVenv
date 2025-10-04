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

def deactivate_venv():
    """Provide instructions to deactivate the virtual environment."""
    if os.name == 'nt':  # Windows
        log("=" * 60)
        log("To deactivate the virtual environment on Windows:")
        log("  deactivate")
        log("=" * 60)
    else:  # Unix/MacOS
        log("=" * 60)
        log("To deactivate the virtual environment:")
        log("  deactivate")
        log("=" * 60)
        print("\n# Copy and paste this command:")
        print("deactivate")
    return True

def build_venv():
    """Find the virtual environment and install requirements."""
    venv_path, venv_name = find_venv_directory()
    
    if not venv_path:
        log("Error: No virtual environment found in current directory")
        log("Run 'qvenv make' to create one first")
        return False
    
    log(f"Found virtual environment: {venv_name}")
    
    # Install requirements
    success = install_requirements(venv_path)
    
    if success:
        log("=" * 60)
        log("Build complete! Requirements installed successfully.")
        log("=" * 60)
        
        # Provide activation instructions
        if os.name == 'nt':  # Windows
            activate_script = os.path.join(venv_path, 'Scripts', 'activate')
            log("To activate the environment, run:")
            log(f"  {activate_script}")
        else:  # Unix/MacOS
            activate_script = os.path.join(venv_path, 'bin', 'activate')
            log("To activate the environment, run:")
            log(f"  source {activate_script}")
            print(f"\n# Copy and paste this command:")
            print(f"source {activate_script}")
        log("=" * 60)
        return True
    else:
        log("Build failed: Could not install requirements")
        return False

def remake_venv():
    """Remake the virtual environment by removing and recreating it with requirements."""
    venv_path, venv_name = find_venv_directory()
    
    if not venv_path:
        log("Error: No virtual environment found in current directory")
        log("Run 'qvenv make' to create one first")
        return False
    
    log(f"Found virtual environment: {venv_name}")
    log("Remaking virtual environment...")
    
    # Remove existing venv
    log(f"Removing existing virtual environment: {venv_name}")
    try:
        shutil.rmtree(venv_path)
        log("Removed successfully")
    except Exception as e:
        log(f"Error removing existing environment: {str(e)}")
        return False
    
    # Get the latest Python version
    python_cmd, version = get_latest_python_version()
    if not python_cmd:
        log("Error: Could not find Python installation")
        return False
    
    # Recreate the virtual environment
    success = create_venv(venv_path, python_cmd)
    if not success:
        log("Error: Failed to recreate virtual environment")
        return False
    
    # Install requirements
    install_success = install_requirements(venv_path)
    if install_success:
        log("=" * 60)
        log("Remake complete! Virtual environment recreated with requirements.")
        log("=" * 60)
    else:
        log("=" * 60)
        log("Virtual environment recreated, but no requirements file found.")
        log("=" * 60)
    
    return True

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Quick tool to setup and manage Python virtual environments"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)
    
    # Create subparser for the make command
    make_parser = subparsers.add_parser('make', help='Create a new virtual environment')
    make_parser.add_argument(
        "path", 
        nargs="?", 
        default="venv",
        help="Path for the virtual environment (default: ./venv)"
    )
    make_parser.add_argument(
        "-f", "--force", 
        action="store_true",
        help="Force recreation if the environment already exists"
    )
    make_parser.add_argument(
        "--complete", 
        action="store_true",
        help="Detect and install requirements after creating the environment"
    )
    
    # Create subparser for the activate command
    activate_parser = subparsers.add_parser('activate', help='Activate virtual environment in current directory')
    
    # Create subparser for the deactivate command
    deactivate_parser = subparsers.add_parser('deactivate', help='Deactivate the current virtual environment')
    
    # Create subparser for the build command
    build_parser = subparsers.add_parser('build', help='Install requirements in the existing virtual environment')
    
    # Create subparser for the install command (alias for build)
    install_parser = subparsers.add_parser('install', help='Install requirements in the existing virtual environment')
    
    # Create subparser for the remake command
    remake_parser = subparsers.add_parser('remake', help='Remake the virtual environment with updated packages')
    
    args = parser.parse_args()
    
    # Handle subcommands
    if args.command == 'activate':
        success = activate_venv()
        return 0 if success else 1
    elif args.command == 'deactivate':
        success = deactivate_venv()
        return 0 if success else 1
    elif args.command == 'build' or args.command == 'install':
        success = build_venv()
        return 0 if success else 1
    elif args.command == 'remake':
        success = remake_venv()
        return 0 if success else 1
    elif args.command == 'make':
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
    
    return 1

if __name__ == "__main__":
    sys.exit(main()) 