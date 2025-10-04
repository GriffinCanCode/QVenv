#!/bin/bash

# QVenv Shell Wrapper
# This wrapper allows direct activation/deactivation while using Python for other commands
# Compatible with both bash and zsh

qvenv() {
    local command="$1"
    shift
    
    # Get the script directory (works in both bash and zsh)
    local script_dir
    if [ -n "${ZSH_VERSION-}" ]; then
        # zsh
        script_dir="$(cd "$(dirname "${(%):-%x}")" && pwd)"
    elif [ -n "${BASH_SOURCE-}" ]; then
        # bash
        script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    else
        # Fallback: use qvenv command in PATH
        script_dir=""
    fi

    case "$command" in
        activate)
            # Get the activation command from Python
            local activate_cmd
            if [ -n "$script_dir" ]; then
                activate_cmd=$(python3 "$script_dir/qvenv.py" activate --quiet "$@" 2>/dev/null)
            else
                activate_cmd=$(qvenv activate --quiet "$@" 2>/dev/null)
            fi
            
            if [ $? -eq 0 ] && [ -n "$activate_cmd" ]; then
                # Execute in current shell
                eval "$activate_cmd"
            else
                # Show error/instructions
                if [ -n "$script_dir" ]; then
                    python3 "$script_dir/qvenv.py" activate "$@"
                else
                    command qvenv activate "$@"
                fi
            fi
            ;;
            
        deactivate)
            # Get the deactivation command from Python
            local deactivate_cmd
            if [ -n "$script_dir" ]; then
                deactivate_cmd=$(python3 "$script_dir/qvenv.py" deactivate --quiet "$@" 2>/dev/null)
            else
                deactivate_cmd=$(qvenv deactivate --quiet "$@" 2>/dev/null)
            fi
            
            if [ $? -eq 0 ] && [ -n "$deactivate_cmd" ]; then
                # Execute in current shell
                eval "$deactivate_cmd"
            else
                # Show error/instructions
                if [ -n "$script_dir" ]; then
                    python3 "$script_dir/qvenv.py" deactivate "$@"
                else
                    command qvenv deactivate "$@"
                fi
            fi
            ;;
            
        *)
            # All other commands: pass through to Python
            if [ -n "$script_dir" ]; then
                python3 "$script_dir/qvenv.py" "$command" "$@"
            else
                command qvenv "$command" "$@"
            fi
            ;;
    esac
}

