"""Command Line Interface for Repo-Guardian.

This module provides the CLI functionality for scanning and repairing Git repositories.
"""

import argparse
import sys
from pathlib import Path

import networkx as nx

from guardian.dag_builder import build_graph
from guardian.object_scanner import GitObjectError, iter_objects, scan_packfile


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

    # Configure 'export-graph' subcommand
    export_parser = subparsers.add_parser(
        "export-graph",
        help="Export repository graph to file"
    )
    export_parser.add_argument(
        "--repo",
        type=Path,
        default=".",
        help="Path to the Git repository (default: current directory)"
    )
    export_parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output file path"
    )
    export_parser.add_argument(
        "--format",
        choices=["graphml", "gexf", "json"],
        default="graphml",
        help="Output file format (default: graphml)"
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
    elif args.command == "export-graph":
        return cmd_export_graph(args)

    return 0


def cmd_scan(args):
    """Execute the 'scan' command.

    Args:
        args: Parsed arguments from argparse

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    repo_path = args.repo_path

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


def cmd_export_graph(args):
    """Execute the 'export-graph' command.

    Args:
        args: Parsed arguments from argparse

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    repo_path = args.repo
    output_file = args.out
    output_format = args.format

    # Verify repository exists
    if not repo_path.exists():
        print(f"Error: Repository path {repo_path} does not exist", file=sys.stderr)
        return 1

    # Process git objects and build graph
    try:
        print(f"Reading Git objects from {repo_path}...")
        objects = list(iter_objects(repo_path))
        print(f"Found {len(objects)} objects")

        print("Building commit graph...")
        graph = build_graph(objects)
        print(f"Graph built with {len(graph.nodes)} nodes and {len(graph.edges)} edges")

        # Export graph
        print(f"Exporting graph to {output_file}...")
        if output_format == "graphml":
            nx.write_graphml(graph, output_file)
        elif output_format == "gexf":
            nx.write_gexf(graph, output_file)
        elif output_format == "json":
            data = nx.node_link_data(graph)
            import json
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)

        print(f"Graph exported successfully to {output_file}")
        return 0

    except GitObjectError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
