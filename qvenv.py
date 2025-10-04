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

def find_venv_directory(quiet=False, max_depth=5):
    """Find virtual environment directory in current directory or subdirectories."""
    # Common virtual environment directory names
    venv_names = ['.venv', 'venv', 'env', 'virtualenv', '.virtualenv']
    
    current_dir = os.getcwd()
    if not quiet:
        log(f"Searching for virtual environment in: {current_dir} (up to {max_depth} levels deep)")
    
    def is_venv(path):
        """Check if a directory is a virtual environment."""
        if os.name == 'nt':  # Windows
            activate_script = os.path.join(path, 'Scripts', 'activate')
            python_exe = os.path.join(path, 'Scripts', 'python.exe')
        else:  # Unix/MacOS
            activate_script = os.path.join(path, 'bin', 'activate')
            python_exe = os.path.join(path, 'bin', 'python')
        
        return os.path.exists(activate_script) or os.path.exists(python_exe)
    
    def search_directory(directory, depth):
        """Recursively search for venv in directory up to max_depth."""
        if depth > max_depth:
            return None, None
        
        # First check current directory for common venv names
        for venv_name in venv_names:
            venv_path = os.path.join(directory, venv_name)
            if os.path.exists(venv_path) and is_venv(venv_path):
                rel_path = os.path.relpath(venv_path, current_dir)
                if not quiet:
                    log(f"Found virtual environment: {rel_path}")
                return venv_path, rel_path
        
        # If not found, search subdirectories (but skip hidden dirs and common non-venv dirs)
        if depth < max_depth:
            try:
                for entry in os.listdir(directory):
                    # Skip hidden directories and common non-venv directories
                    if entry.startswith('.') and entry not in venv_names:
                        continue
                    if entry in ['node_modules', 'build', 'dist', '__pycache__', 'target', '.git']:
                        continue
                    
                    entry_path = os.path.join(directory, entry)
                    if os.path.isdir(entry_path):
                        # Check if this directory itself is a venv
                        if entry in venv_names and is_venv(entry_path):
                            rel_path = os.path.relpath(entry_path, current_dir)
                            if not quiet:
                                log(f"Found virtual environment: {rel_path}")
                            return entry_path, rel_path
                        
                        # Recurse into subdirectory
                        venv_path, venv_name = search_directory(entry_path, depth + 1)
                        if venv_path:
                            return venv_path, venv_name
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
        
        return None, None
    
    return search_directory(current_dir, 0)

def activate_venv(quiet=False):
    """Activate the virtual environment."""
    venv_path, venv_name = find_venv_directory(quiet=quiet)
    
    if not venv_path:
        if not quiet:
            log("Error: No virtual environment found")
            log("Searched current directory and subdirectories (5 levels deep)")
            log("Looking for: .venv, venv, .env, env, virtualenv, .virtualenv")
        return False
    
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
        if not os.path.exists(activate_script):
            activate_script = os.path.join(venv_path, 'Scripts', 'activate')
        
        if os.path.exists(activate_script):
            if quiet:
                # Just print the command for eval
                print(activate_script)
            else:
                log("=" * 60)
                log(f"Virtual environment found: {venv_name}")
                log("=" * 60)
                log("Run this command to activate:")
                print(f"\n{activate_script}")
                log("\n" + "=" * 60)
            return True
        else:
            if not quiet:
                log(f"Error: Activation script not found at {activate_script}")
            return False
    else:  # Unix/MacOS
        activate_script = os.path.join(venv_path, 'bin', 'activate')
        
        if os.path.exists(activate_script):
            if quiet:
                # Just print the source command for eval
                print(f"source {activate_script}")
            else:
                log("=" * 60)
                log(f"Virtual environment found: {venv_name}")
                log("=" * 60)
                log("Run this command to activate:")
                print(f"\nsource {activate_script}")
                log("\nOr use eval to activate automatically:")
                log(f'  eval "$(qvenv activate --quiet)"')
                log("=" * 60)
            return True
        else:
            if not quiet:
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
        log("=" * 60)
        log("Virtual environment created successfully!")
        log("=" * 60)
        log("To activate, run:")
        if os.name == 'nt':  # Windows
            activate_cmd = f"{os.path.join(path, 'Scripts', 'activate')}"
            print(f"\n{activate_cmd}")
        else:  # Unix/MacOS
            activate_cmd = f"source {os.path.join(path, 'bin', 'activate')}"
            print(f"\n{activate_cmd}")
            log("\nOr use eval:")
            log('  eval "$(qvenv activate --quiet)"')
        log("=" * 60)
        
        return True
    except Exception as e:
        log(f"Error creating virtual environment: {str(e)}")
        return False

def find_requirements_file(max_depth=5):
    """Find requirements file in current directory or subdirectories."""
    # Common requirements file names
    req_files = ["requirements.txt", "requirements.pip"]
    
    current_dir = os.getcwd()
    log("Checking for requirements file...")
    log(f"Searching in: {current_dir} (up to {max_depth} levels deep)")
    
    def search_directory(directory, depth):
        """Recursively search for requirements file up to max_depth."""
        if depth > max_depth:
            return None
        
        # Check current directory for requirements files
        for req_file in req_files:
            req_path = os.path.join(directory, req_file)
            if os.path.exists(req_path) and os.path.isfile(req_path):
                rel_path = os.path.relpath(req_path, current_dir)
                log(f"Found requirements file: {rel_path}")
                return req_path
        
        # Search subdirectories
        if depth < max_depth:
            try:
                for entry in os.listdir(directory):
                    # Skip hidden directories and common non-project directories
                    if entry.startswith('.'):
                        continue
                    if entry in ['node_modules', 'build', 'dist', '__pycache__', 'target', 
                                 'venv', '.venv', 'env', '.env', 'virtualenv', '.virtualenv']:
                        continue
                    
                    entry_path = os.path.join(directory, entry)
                    if os.path.isdir(entry_path):
                        req_path = search_directory(entry_path, depth + 1)
                        if req_path:
                            return req_path
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
        
        return None
    
    return search_directory(current_dir, 0)

def install_requirements(venv_path):
    """Detect and install requirements file in the virtual environment."""
    # Find requirements file (searches recursively)
    req_file = find_requirements_file()
    
    if not req_file:
        log("No requirements file found.")
        log("Searched current directory and subdirectories (5 levels deep)")
        return False
    
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

def deactivate_venv(quiet=False):
    """Provide instructions to deactivate the virtual environment."""
    if quiet:
        # Just print the command for eval
        print("deactivate")
    else:
        log("=" * 60)
        log("Run this command to deactivate:")
        print("\ndeactivate")
        log("\nOr use eval to deactivate automatically:")
        log('  eval "$(qvenv deactivate --quiet)"')
        log("=" * 60)
    return True

def build_venv():
    """Find the virtual environment and install requirements."""
    venv_path, venv_name = find_venv_directory()
    
    if not venv_path:
        log("Error: No virtual environment found")
        log("Searched current directory and subdirectories (5 levels deep)")
        log("Run 'qvenv make' to create one first")
        return False
    
    log(f"Found virtual environment: {venv_name}")
    
    # Install requirements
    success = install_requirements(venv_path)
    
    if success:
        log("=" * 60)
        log("Build complete! Requirements installed successfully.")
        log("=" * 60)
        log("To activate the environment, run:")
        
        # Provide activation instructions
        if os.name == 'nt':  # Windows
            activate_script = os.path.join(venv_path, 'Scripts', 'activate')
            print(f"\n{activate_script}")
        else:  # Unix/MacOS
            activate_script = os.path.join(venv_path, 'bin', 'activate')
            print(f"\nsource {activate_script}")
            log("\nOr use eval:")
            log('  eval "$(qvenv activate --quiet)"')
        log("=" * 60)
        return True
    else:
        log("Build failed: Could not install requirements")
        return False

def remake_venv():
    """Remake the virtual environment by removing and recreating it with requirements."""
    venv_path, venv_name = find_venv_directory()
    
    if not venv_path:
        log("Error: No virtual environment found")
        log("Searched current directory and subdirectories (5 levels deep)")
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
    activate_parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Output only the command (for use with eval)"
    )
    
    # Create subparser for the deactivate command
    deactivate_parser = subparsers.add_parser('deactivate', help='Deactivate the current virtual environment')
    deactivate_parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Output only the command (for use with eval)"
    )
    
    # Create subparser for the build command
    build_parser = subparsers.add_parser('build', help='Install requirements in the existing virtual environment')
    
    # Create subparser for the install command (alias for build)
    install_parser = subparsers.add_parser('install', help='Install requirements in the existing virtual environment')
    
    # Create subparser for the remake command
    remake_parser = subparsers.add_parser('remake', help='Remake the virtual environment with updated packages')
    
    args = parser.parse_args()
    
    # Handle subcommands
    if args.command == 'activate':
        quiet = getattr(args, 'quiet', False)
        success = activate_venv(quiet=quiet)
        return 0 if success else 1
    elif args.command == 'deactivate':
        quiet = getattr(args, 'quiet', False)
        success = deactivate_venv(quiet=quiet)
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