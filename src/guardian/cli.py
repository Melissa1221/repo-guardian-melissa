"""Command Line Interface for Repo-Guardian.

This module provides the CLI functionality for scanning and repairing Git repositories.
"""

import argparse
import sys
from pathlib import Path

import networkx as nx

from guardian.dag_builder import build_graph
from guardian.object_scanner import GitObjectError, iter_objects, scan_packfile
from guardian.tui import run_tui


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Repo-Guardian: Git repository auditing and repair tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Configure 'scan' subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan repository for issues")
    scan_parser.add_argument(
        "repo_path", type=Path, help="Path to the Git repository to scan"
    )
    scan_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    scan_parser.add_argument(
        "--repair",
        action="store_true",
        help="Attempt to repair issues found during scan",
    )
    scan_parser.add_argument(
        "--tui",
        action="store_true",
        help="Use the Terminal User Interface for interactive scanning",
    )
    scan_parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of threads to use for scanning (default: 1)",
    )

    # Configure 'export-graph' subcommand
    export_parser = subparsers.add_parser(
        "export-graph", help="Export repository graph to file"
    )
    export_parser.add_argument(
        "--repo",
        type=Path,
        default=".",
        help="Path to the Git repository (default: current directory)",
    )
    export_parser.add_argument(
        "--out", type=Path, required=True, help="Output file path"
    )
    export_parser.add_argument(
        "--format",
        choices=["graphml", "gexf", "json", "dot"],
        default="graphml",
        help="Output file format (default: graphml)",
    )

    # Configure 'stats' subcommand
    stats_parser = subparsers.add_parser("stats", help="Show repository statistics")
    stats_parser.add_argument(
        "repo_path", type=Path, help="Path to the Git repository to analyze"
    )
    stats_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed statistics"
    )

    # Configure 'demo' subcommand (for development purposes)
    demo_parser = subparsers.add_parser("demo", help="Run the TUI in demo mode")
    demo_parser.add_argument(
        "--repo",
        type=Path,
        default=".",
        help="Path to the Git repository (default: current directory)",
    )

    # Parse arguments
    args = parser.parse_args()

    # If no command was specified, show help
    if args.command is None:
        parser.print_help()
        return 0

    # Execute the appropriate command
    if args.command == "scan":
        if hasattr(args, "tui") and args.tui:
            return cmd_scan_tui(args)
        else:
            return cmd_scan(args)
    elif args.command == "export-graph":
        return cmd_export_graph(args)
    elif args.command == "stats":
        return cmd_stats(args)
    elif args.command == "demo":
        return cmd_demo(args)

    return 0


def cmd_scan(args):
    """Execute the 'scan' command in CLI mode.

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


def cmd_scan_tui(args):
    """Execute the 'scan' command with TUI.

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

    # Run the TUI with actual scanning
    run_tui(repo_path, demo_mode=False)

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

            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
        elif output_format == "dot":
            from networkx.drawing.nx_agraph import write_dot

            write_dot(graph, output_file)

        print(f"Graph exported successfully to {output_file}")
        return 0

    except GitObjectError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 3


def cmd_stats(args):
    """Execute the 'stats' command.

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

    try:
        print(f"Analyzing repository at {repo_path}...")
        objects = list(iter_objects(repo_path))

        # Basic statistics
        object_count = len(objects)
        object_types = {}

        for obj in objects:
            obj_type = obj.get("type", "unknown")
            object_types[obj_type] = object_types.get(obj_type, 0) + 1

        print("\nRepository Statistics:")
        print(f"Total objects: {object_count}")
        print("Object types:")
        for obj_type, count in object_types.items():
            print(f"  - {obj_type}: {count}")

        # Build and analyze graph if detailed statistics requested
        if args.detailed:
            print("\nBuilding commit graph for detailed analysis...")
            graph = build_graph(objects)

            # Calculate additional statistics
            commit_count = len(
                [n for n in graph.nodes if graph.nodes[n].get("type") == "commit"]
            )
            root_nodes = [n for n in graph.nodes if graph.in_degree(n) == 0]
            max_gen = max(graph.nodes[n].get("generation", 0) for n in graph.nodes)

            print("\nDetailed Statistics:")
            print(f"Commit count: {commit_count}")
            print(f"Root commits: {len(root_nodes)}")
            print(f"Maximum generation: {max_gen}")
            print(f"Graph edges: {len(graph.edges)}")

            # Additional checks that might indicate issues
            if len(root_nodes) > 1:
                print("\nPotential Issues:")
                print(f"Multiple root commits detected ({len(root_nodes)})")

        return 0

    except GitObjectError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 3


def cmd_demo(args):
    """Execute the 'demo' command to show TUI demo.

    Args:
        args: Parsed arguments from argparse

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    repo_path = args.repo

    # Verify repository exists
    if not repo_path.exists():
        print(f"Error: Repository path {repo_path} does not exist", file=sys.stderr)
        return 1

    # Run the TUI in demo mode
    run_tui(repo_path, demo_mode=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
