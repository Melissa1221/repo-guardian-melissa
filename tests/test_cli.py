"""Unit tests for the CLI module."""

from pathlib import Path
from unittest.mock import patch

from guardian.cli import cmd_scan, main


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

            # Mock cmd_scan to return a specific value
            with patch("guardian.cli.cmd_scan", return_value=42) as mock_cmd_scan:
                # When running the main function
                with patch("sys.argv", ["guardian", "scan", "/path/to/repo"]):
                    result = main()

                # Then it should call cmd_scan and return its value
                assert result == 42
                mock_cmd_scan.assert_called_once_with(mock_args)

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
