"""Command Line Interface for Repo-Guardian.

This module provides the CLI functionality for scanning and repairing Git repositories.
"""

import argparse
import sys
from pathlib import Path

from guardian.object_scanner import GitObjectError, scan_packfile


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Repo-Guardian: Git repository auditing and repair tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Configure 'scan' subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan repository for issues")
    scan_parser.add_argument(
        "repo_path", 
        type=Path, 
        help="Path to the Git repository to scan"
    )
    scan_parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command was specified, show help
    if args.command is None:
        parser.print_help()
        return 0
    
    # Execute the appropriate command
    if args.command == "scan":
        return cmd_scan(args)
    
    return 0


def cmd_scan(args):
    """Execute the 'scan' command.
    
    Args:
        args: Parsed arguments from argparse
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    repo_path = args.repo_path
    verbose = args.verbose
    
    # Verify repository exists
    if not repo_path.exists():
        print(f"Error: Repository path {repo_path} does not exist", file=sys.stderr)
        return 1
    
    print(f"Scanning repository at {repo_path}...")
    
    # Scan for packfiles
    pack_dir = repo_path / "objects" / "pack"
    if pack_dir.exists() and pack_dir.is_dir():
        pack_files = list(pack_dir.glob("*.pack"))
        if not pack_files:
            print("No packfiles found", file=sys.stderr)
        
        for pack_file in pack_files:
            try:
                print(f"Scanning packfile {pack_file.name}...")
                entries = scan_packfile(pack_file)
                print(f"Found {len(entries)} objects in packfile")
            except GitObjectError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 2  # Error code 2 for packfile errors
    
    print("Scan completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
