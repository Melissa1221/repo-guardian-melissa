"""Unit tests for the CLI module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from guardian.cli import (
    cmd_demo,
    cmd_export_graph,
    cmd_scan,
    cmd_scan_tui,
    cmd_stats,
    main,
)


class TestCLI:
    """Test cases for the CLI module."""

    def test_main_no_args(self):
        """Test running the CLI with no arguments."""
        # Mock the argparse module
        with patch("guardian.cli.argparse.ArgumentParser") as mock_parser_cls:
            # Setup the mock parser
            mock_parser = mock_parser_cls.return_value
            mock_args = mock_parser.parse_args.return_value
            mock_args.command = None

            # When running the main function
            with patch("sys.argv", ["guardian"]):
                result = main()

            # Then it should show help and return 0
            assert result == 0
            mock_parser.print_help.assert_called_once()

    def test_main_scan_command(self):
        """Test running the CLI with the scan command."""
        # Mock the argparse module
        with patch("guardian.cli.argparse.ArgumentParser") as mock_parser_cls:
            # Setup the mock parser
            mock_parser = mock_parser_cls.return_value
            # Call add_subparsers but don't store the result
            mock_parser.add_subparsers.return_value

            # Setup mock args
            mock_args = mock_parser.parse_args.return_value
            mock_args.command = "scan"
            mock_args.tui = False  # Add tui attribute to ensure cmd_scan is called

            # Mock cmd_scan to return a specific value
            with patch("guardian.cli.cmd_scan", return_value=42) as mock_cmd_scan:
                # When running the main function
                with patch("sys.argv", ["guardian", "scan", "/path/to/repo"]):
                    result = main()

                # Then it should call cmd_scan and return its value
                assert result == 42
                mock_cmd_scan.assert_called_once_with(mock_args)

    def test_main_scan_tui_command(self):
        """Test running the CLI with the scan command and tui option."""
        # Mock the argparse module
        with patch("guardian.cli.argparse.ArgumentParser") as mock_parser_cls:
            # Setup the mock parser
            mock_parser = mock_parser_cls.return_value
            mock_parser.add_subparsers.return_value

            # Setup mock args
            mock_args = mock_parser.parse_args.return_value
            mock_args.command = "scan"
            mock_args.tui = True  # Use tui mode

            # Mock cmd_scan_tui to return a specific value
            with patch(
                "guardian.cli.cmd_scan_tui", return_value=43
            ) as mock_cmd_scan_tui:
                # When running the main function
                cmd_args = ["guardian", "scan", "/path/to/repo", "--tui"]
                with patch("sys.argv", cmd_args):
                    result = main()

                # Then it should call cmd_scan_tui and return its value
                assert result == 43
                mock_cmd_scan_tui.assert_called_once_with(mock_args)

    def test_main_export_graph_command(self):
        """Test running the CLI with the export-graph command."""
        # Mock the argparse module
        with patch("guardian.cli.argparse.ArgumentParser") as mock_parser_cls:
            # Setup the mock parser
            mock_parser = mock_parser_cls.return_value
            mock_parser.add_subparsers.return_value

            # Setup mock args
            mock_args = mock_parser.parse_args.return_value
            mock_args.command = "export-graph"

            # Mock cmd_export_graph to return a specific value
            with patch("guardian.cli.cmd_export_graph", return_value=44) as mock_cmd:
                # When running the main function
                cmd_args = ["guardian", "export-graph", "--out", "graph.xml"]
                with patch("sys.argv", cmd_args):
                    result = main()

                # Then it should call cmd_export_graph and return its value
                assert result == 44
                mock_cmd.assert_called_once_with(mock_args)

    def test_main_stats_command(self):
        """Test running the CLI with the stats command."""
        # Mock the argparse module
        with patch("guardian.cli.argparse.ArgumentParser") as mock_parser_cls:
            # Setup the mock parser
            mock_parser = mock_parser_cls.return_value
            mock_parser.add_subparsers.return_value

            # Setup mock args
            mock_args = mock_parser.parse_args.return_value
            mock_args.command = "stats"

            # Mock cmd_stats to return a specific value
            with patch("guardian.cli.cmd_stats", return_value=45) as mock_cmd:
                # When running the main function
                with patch("sys.argv", ["guardian", "stats", "/path/to/repo"]):
                    result = main()

                # Then it should call cmd_stats and return its value
                assert result == 45
                mock_cmd.assert_called_once_with(mock_args)

    def test_main_demo_command(self):
        """Test running the CLI with the demo command."""
        # Mock the argparse module
        with patch("guardian.cli.argparse.ArgumentParser") as mock_parser_cls:
            # Setup the mock parser
            mock_parser = mock_parser_cls.return_value
            mock_parser.add_subparsers.return_value

            # Setup mock args
            mock_args = mock_parser.parse_args.return_value
            mock_args.command = "demo"

            # Mock cmd_demo to return a specific value
            with patch("guardian.cli.cmd_demo", return_value=46) as mock_cmd:
                # When running the main function
                with patch("sys.argv", ["guardian", "demo"]):
                    result = main()

                # Then it should call cmd_demo and return its value
                assert result == 46
                mock_cmd.assert_called_once_with(mock_args)

    def test_cmd_scan_nonexistent_repo(self):
        """Test scanning a nonexistent repository."""

        # Create args with a nonexistent repo path
        class Args:
            repo_path = Path("/nonexistent/path")
            verbose = False

        args = Args()

        # When running cmd_scan
        with patch("sys.stderr"):  # Suppress error output
            result = cmd_scan(args)

        # Then it should return error code 1
        assert result == 1

    def test_cmd_scan_no_packfiles(self, tmp_path):
        """Test scanning a repository with no packfiles."""
        # Given a temp directory as repo
        repo_path = tmp_path

        # Create the objects/pack directory
        pack_dir = repo_path / "objects" / "pack"
        pack_dir.mkdir(parents=True)

        # And args pointing to it
        class Args:
            def __init__(self, path):
                self.repo_path = path
                self.verbose = False

        args = Args(repo_path)

        # When running cmd_scan
        with patch("sys.stderr"):  # Suppress error output
            with patch("builtins.print"):  # Suppress output
                result = cmd_scan(args)

        # Then it should return 0 (success)
        assert result == 0

    def test_cmd_scan_tui_nonexistent_repo(self):
        """Test scanning a nonexistent repository with TUI."""

        # Create args with a nonexistent repo path
        class Args:
            repo_path = Path("/nonexistent/path")

        args = Args()

        # When running cmd_scan_tui
        with patch("sys.stderr"):  # Suppress error output
            result = cmd_scan_tui(args)

        # Then it should return error code 1
        assert result == 1

    def test_cmd_scan_tui_existing_repo(self, tmp_path):
        """Test scanning an existing repository with TUI."""
        # Given a temp directory as repo
        repo_path = tmp_path

        # Create args with the repo path
        class Args:
            def __init__(self, path):
                self.repo_path = path

        args = Args(repo_path)

        # Mock run_tui to prevent actual TUI execution
        with patch("guardian.cli.run_tui") as mock_run_tui:
            # When running cmd_scan_tui
            result = cmd_scan_tui(args)

            # Then it should call run_tui and return 0
            assert result == 0
            mock_run_tui.assert_called_once_with(repo_path, demo_mode=False)

    def test_cmd_export_graph_nonexistent_repo(self):
        """Test exporting graph from a nonexistent repository."""

        # Create args with a nonexistent repo path
        class Args:
            repo = Path("/nonexistent/path")
            out = Path("graph.xml")
            format = "graphml"

        args = Args()

        # When running cmd_export_graph
        with patch("sys.stderr"):  # Suppress error output
            result = cmd_export_graph(args)

        # Then it should return error code 1
        assert result == 1

    def test_cmd_export_graph_object_error(self, tmp_path):
        """Test exporting graph with GitObjectError."""
        # Given a temp directory as repo
        repo_path = tmp_path

        # Create args with the repo path
        class Args:
            repo = repo_path
            out = Path("graph.xml")
            format = "graphml"

        args = Args()

        # Mock iter_objects to raise GitObjectError
        with patch("guardian.cli.iter_objects") as mock_iter_objects:
            mock_iter_objects.side_effect = Exception("Test error")

            # When running cmd_export_graph
            with patch("sys.stderr"):  # Suppress error output
                result = cmd_export_graph(args)

            # Then it should return error code 3
            assert result == 3

    def test_cmd_stats_nonexistent_repo(self):
        """Test getting stats from a nonexistent repository."""

        # Create args with a nonexistent repo path
        class Args:
            repo_path = Path("/nonexistent/path")
            detailed = False

        args = Args()

        # When running cmd_stats
        with patch("sys.stderr"):  # Suppress error output
            result = cmd_stats(args)

        # Then it should return error code 1
        assert result == 1

    def test_cmd_stats_with_error(self, tmp_path):
        """Test getting stats with an error."""
        # Given a temp directory as repo
        repo_path = tmp_path

        # Create args with the repo path
        class Args:
            def __init__(self):
                self.repo_path = repo_path
                self.detailed = False

        args = Args()

        # Mock iter_objects to raise Exception
        with patch("guardian.cli.iter_objects") as mock_iter_objects:
            mock_iter_objects.side_effect = Exception("Test error")

            # When running cmd_stats
            with patch("sys.stderr"):  # Suppress error output
                result = cmd_stats(args)

            # Then it should return error code 3
            assert result == 3

    def test_cmd_demo_nonexistent_repo(self):
        """Test running demo with a nonexistent repository."""

        # Create args with a nonexistent repo path
        class Args:
            repo = Path("/nonexistent/path")

        args = Args()

        # When running cmd_demo
        with patch("sys.stderr"):  # Suppress error output
            result = cmd_demo(args)

        # Then it should return error code 1
        assert result == 1

    def test_cmd_demo_existing_repo(self, tmp_path):
        """Test running demo with an existing repository."""
        # Given a temp directory as repo
        repo_path = tmp_path

        # Create args with the repo path
        class Args:
            repo = repo_path

        args = Args()

        # Mock run_tui to prevent actual TUI execution
        with patch("guardian.cli.run_tui") as mock_run_tui:
            # When running cmd_demo
            result = cmd_demo(args)

            # Then it should call run_tui and return 0
            assert result == 0
            mock_run_tui.assert_called_once_with(repo_path, demo_mode=True)

    def test_cmd_stats_with_detailed(self, tmp_path):
        """Test getting detailed stats."""
        # Given a temp directory as repo
        repo_path = tmp_path

        # Create the objects/pack directory
        pack_dir = repo_path / "objects" / "pack"
        pack_dir.mkdir(parents=True)

        # And args pointing to it with detailed=True
        class Args:
            def __init__(self):
                self.repo_path = repo_path
                self.detailed = True

        args = Args()

        # Mock iter_objects and build_graph
        with patch("guardian.cli.iter_objects") as mock_iter_objects, patch(
            "guardian.cli.build_graph"
        ) as mock_build_graph:
            # Return a list of mock objects
            mock_iter_objects.return_value = [
                {"type": "commit", "hash": "123"},
                {"type": "blob", "hash": "456"},
                {"type": "tree", "hash": "789"},
            ]

            # Mock graph with nodes
            mock_graph = MagicMock()
            mock_graph.nodes = {
                "123": {"type": "commit", "generation": 1},
                "456": {"type": "blob"},
                "789": {"type": "tree"},
            }
            mock_graph.in_degree.return_value = 0
            mock_graph.edges = []
            mock_build_graph.return_value = mock_graph

            # When running cmd_stats
            with patch("builtins.print"):  # Suppress output
                result = cmd_stats(args)

            # Then it should return 0 (success)
            assert result == 0
            # And build_graph should have been called
            mock_build_graph.assert_called_once()

    def test_cmd_scan_with_packfiles(self, tmp_path):
        """Test scanning a repository with packfiles."""
        # Given a temp directory as repo
        repo_path = tmp_path

        # Create the objects/pack directory and a mock packfile
        pack_dir = repo_path / "objects" / "pack"
        pack_dir.mkdir(parents=True)
        mock_packfile = pack_dir / "pack-123.pack"
        mock_packfile.touch()

        # And args pointing to it
        class Args:
            def __init__(self):
                self.repo_path = repo_path
                self.verbose = False

        args = Args()

        # Mock scan_packfile
        with patch("guardian.cli.scan_packfile") as mock_scan_packfile:
            # Return a list of mock objects
            mock_scan_packfile.return_value = [
                {"offset": 12, "type": 1, "data": b"test"},
                {"offset": 34, "type": 2, "data": b"test2"},
            ]

            # When running cmd_scan
            with patch("builtins.print"):  # Suppress output
                result = cmd_scan(args)

            # Then it should return 0 (success)
            assert result == 0
            # And scan_packfile should have been called
            mock_scan_packfile.assert_called_once()

    def test_cmd_scan_with_packfile_error(self, tmp_path):
        """Test scanning a repository with packfile errors."""
        # Given a temp directory as repo
        repo_path = tmp_path

        # Create the objects/pack directory and a mock packfile
        pack_dir = repo_path / "objects" / "pack"
        pack_dir.mkdir(parents=True)
        mock_packfile = pack_dir / "pack-123.pack"
        mock_packfile.touch()

        # And args pointing to it
        class Args:
            def __init__(self):
                self.repo_path = repo_path
                self.verbose = False

        args = Args()

        # Mock scan_packfile to raise an error
        with patch("guardian.cli.scan_packfile") as mock_scan_packfile:
            # Return a list of mock objects
            from guardian.object_scanner import GitObjectError

            mock_scan_packfile.side_effect = GitObjectError("Test error")

            # When running cmd_scan
            with patch("builtins.print"), patch("sys.stderr"):  # Suppress output
                result = cmd_scan(args)

            # Then it should return error code 2
            assert result == 2
            # And scan_packfile should have been called
            mock_scan_packfile.assert_called_once()
