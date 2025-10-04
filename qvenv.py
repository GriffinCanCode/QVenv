#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import platform
from datetime import datetime
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text
from rich import box
from rich.tree import Tree

# Initialize Rich console
console = Console()

def log_info(message):
    """Print an info message."""
    console.print(f"  [cyan]→[/cyan] {message}")

def log_success(message):
    """Print a success message."""
    console.print(f"  [green]✓[/green] {message}")

def log_error(message):
    """Print an error message."""
    console.print(f"  [red]✗[/red] {message}")

def log_warning(message):
    """Print a warning message."""
    console.print(f"  [yellow]⚠[/yellow] {message}")

def find_venv_directory(quiet=False, max_depth=5):
    """Find virtual environment directory in current directory or subdirectories."""
    # Common virtual environment directory names
    venv_names = ['.venv', 'venv', 'env', 'virtualenv', '.virtualenv']
    
    current_dir = os.getcwd()
    if not quiet:
        with console.status("[cyan]Searching...", spinner="dots"):
            result = _do_find_venv(current_dir, venv_names, max_depth)
        return result
    else:
        return _do_find_venv(current_dir, venv_names, max_depth)

def _do_find_venv(current_dir, venv_names, max_depth):
    """Internal function to perform venv search."""
    
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
                log_success(f"Found [cyan]{rel_path}[/cyan]")
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
                            log_success(f"Found [cyan]{rel_path}[/cyan]")
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
            log_error("No virtual environment found")
            console.print("  [dim]Run[/dim] [cyan]qvenv make[/cyan] [dim]to create one[/dim]")
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
                console.print()
                console.print(f"  [cyan]→[/cyan] Run: [bold cyan]{activate_script}[/bold cyan]")
            return True
        else:
            if not quiet:
                log_error(f"Activation script not found")
            return False
    else:  # Unix/MacOS
        activate_script = os.path.join(venv_path, 'bin', 'activate')
        
        if os.path.exists(activate_script):
            if quiet:
                # Just print the source command for eval
                print(f"source {activate_script}")
            else:
                console.print()
                console.print(f"  [cyan]→[/cyan] Run: [bold cyan]source {activate_script}[/bold cyan]")
                console.print(f"  [dim]or:[/dim] [dim cyan]eval \"$(qvenv activate --quiet)\"[/dim cyan]")
            return True
        else:
            if not quiet:
                log_error(f"Activation script not found at {activate_script}")
            return False

def get_latest_python_version():
    """Get the latest stable Python version installed on the system."""
    with console.status("[cyan]Checking Python...", spinner="dots"):
        try:
            # Try python3 --version first
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[1]
                log_success(f"Python [cyan]{version}[/cyan]")
                return "python3", version
        except Exception:
            pass
        
        # If python3 fails, try python
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[1]
                log_success(f"Python [cyan]{version}[/cyan]")
                return "python", version
        except Exception:
            pass
        
        return None, None

def create_venv(path, python_cmd):
    """Create a virtual environment at the specified path."""
    
    try:
        # Check if venv module is available
        result = subprocess.run(
            [python_cmd, "-m", "venv", "--help"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            log_error("Python venv module not available")
            console.print("  [dim]Install with:[/dim] [cyan]pip install venv[/cyan]")
            return False
            
        # Create the virtual environment
        with console.status("[cyan]Creating...", spinner="dots"):
            result = subprocess.run(
                [python_cmd, "-m", "venv", path],
                capture_output=True, text=True
            )
        
        if result.returncode != 0:
            log_error(f"Failed to create: {result.stderr}")
            return False
        
        log_success(f"Created at [cyan]{path}[/cyan]")
        
        # Print activation instructions
        if os.name == 'nt':  # Windows
            activate_cmd = f"{os.path.join(path, 'Scripts', 'activate')}"
        else:  # Unix/MacOS
            activate_cmd = f"source {os.path.join(path, 'bin', 'activate')}"
        
        console.print()
        console.print(f"  [cyan]→[/cyan] Run: [bold cyan]{activate_cmd}[/bold cyan]")
        if os.name != 'nt':
            console.print(f"  [dim]or:[/dim] [dim cyan]eval \"$(qvenv activate --quiet)\"[/dim cyan]")
        
        return True
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

def find_requirements_file(max_depth=5):
    """Find requirements file in current directory or subdirectories."""
    # Common requirements file names
    req_files = ["requirements.txt", "requirements.pip"]
    
    current_dir = os.getcwd()
    
    with console.status("[cyan]Searching requirements...", spinner="dots"):
        result = _do_find_requirements(current_dir, req_files, max_depth)
    
    return result

def _do_find_requirements(current_dir, req_files, max_depth):
    """Internal function to search for requirements file."""
    def search_directory(directory, depth):
        """Recursively search for requirements file up to max_depth."""
        if depth > max_depth:
            return None
        
        # Check current directory for requirements files
        for req_file in req_files:
            req_path = os.path.join(directory, req_file)
            if os.path.exists(req_path) and os.path.isfile(req_path):
                rel_path = os.path.relpath(req_path, current_dir)
                log_success(f"Found [cyan]{rel_path}[/cyan]")
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
        log_warning("No requirements file found")
        return False
    
    # Get pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_path, 'Scripts', 'pip')
    else:  # Unix/MacOS
        pip_path = os.path.join(venv_path, 'bin', 'pip')
    
    try:
        # Install requirements with a progress indicator
        with console.status("[cyan]Installing...", spinner="dots"):
            result = subprocess.run(
                [pip_path, "install", "-r", req_file],
                capture_output=True, text=True
            )
        
        if result.returncode != 0:
            log_error(f"Installation failed")
            return False
        
        log_success("Requirements installed")
        
        return True
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False

def deactivate_venv(quiet=False):
    """Provide instructions to deactivate the virtual environment."""
    if quiet:
        # Just print the command for eval
        print("deactivate")
    else:
        console.print()
        console.print(f"  [cyan]→[/cyan] Run: [bold cyan]deactivate[/bold cyan]")
        console.print(f"  [dim]or:[/dim] [dim cyan]eval \"$(qvenv deactivate --quiet)\"[/dim cyan]")
    return True

def build_venv():
    """Find the virtual environment and install requirements."""
    venv_path, venv_name = find_venv_directory()
    
    if not venv_path:
        log_error("No virtual environment found")
        console.print("  [dim]Run[/dim] [cyan]qvenv make[/cyan] [dim]to create one[/dim]")
        return False
    
    # Install requirements
    console.print()
    success = install_requirements(venv_path)
    
    if success:
        console.print()
        console.print(f"  [green]✓[/green] Build complete for [cyan]{venv_name}[/cyan]")
        return True
    else:
        return False

def remake_venv():
    """Remake the virtual environment by removing and recreating it with requirements."""
    venv_path, venv_name = find_venv_directory()
    
    if not venv_path:
        log_error("No virtual environment found")
        console.print("  [dim]Run[/dim] [cyan]qvenv make[/cyan] [dim]to create one[/dim]")
        return False
    
    console.print()
    log_info(f"Remaking [cyan]{venv_name}[/cyan]")
    
    # Remove existing venv
    with console.status("[yellow]Removing...", spinner="dots"):
        try:
            shutil.rmtree(venv_path)
            log_success("Removed")
        except Exception as e:
            log_error(f"Error: {str(e)}")
            return False
    
    # Get the latest Python version
    python_cmd, version = get_latest_python_version()
    if not python_cmd:
        log_error("Python not found")
        return False
    
    console.print()
    # Recreate the virtual environment
    success = create_venv(venv_path, python_cmd)
    if not success:
        return False
    
    console.print()
    # Install requirements
    install_success = install_requirements(venv_path)
    
    if install_success:
        console.print()
        console.print(f"  [green]✓[/green] Remake complete for [cyan]{venv_name}[/cyan]")
    else:
        console.print()
        console.print(f"  [yellow]⚠[/yellow] No requirements to install")
    
    return True

def main():
    """Main execution function."""
    # Display minimal header
    console.print()
    console.print("[bold cyan]qvenv[/bold cyan]", justify="left")
    console.print()
    
    parser = argparse.ArgumentParser(
        description="Python virtual environment manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
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
                with console.status("[yellow]Removing...", spinner="dots"):
                    try:
                        shutil.rmtree(path)
                        log_success("Removed existing")
                    except Exception as e:
                        log_error(f"Error: {str(e)}")
                        return 1
            else:
                log_error(f"Directory exists: [yellow]{path}[/yellow]")
                console.print("  [dim]Use[/dim] [cyan]-f[/cyan] [dim]to force recreation[/dim]")
                return 1
        
        # Get the latest Python version
        python_cmd, version = get_latest_python_version()
        if not python_cmd:
            log_error("Python not found")
            return 1
        
        console.print()
        # Create the virtual environment
        success = create_venv(path, python_cmd)
        if not success:
            return 1
        
        # Install requirements if --complete is specified
        if args.complete:
            console.print()
            install_success = install_requirements(path)
        
        return 0
    
    return 1

if __name__ == "__main__":
    sys.exit(main()) 