import os
import tempfile
from pathlib import Path
from unittest import mock

import networkx as nx
import pytest
from guardian.cli import cmd_demo, cmd_export_graph, cmd_scan, cmd_stats, main
from guardian.object_scanner import GitObjectError


@pytest.fixture
def temp_repo():
    """Create a temporary directory to simulate a Git repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create minimal .git structure
        git_dir = Path(temp_dir) / ".git"
        objects_dir = git_dir / "objects"
        pack_dir = objects_dir / "pack"

        os.makedirs(pack_dir, exist_ok=True)

        # Create an empty file to simulate a pack file
        (pack_dir / "pack-test.pack").touch()
        (pack_dir / "pack-test.idx").touch()

        yield Path(temp_dir)


class TestCLIMain:
    def test_main_no_args(self):
        """Test running main with no arguments."""
        with mock.patch("sys.stdout"):
            assert main([]) == 0

    def test_main_help(self):
        """Test running main with --help."""
        with pytest.raises(SystemExit):
            with mock.patch("sys.stdout"):
                main(["--help"])

    def test_main_scan(self):
        """Test running main with scan command."""
        with mock.patch("guardian.cli.cmd_scan") as mock_cmd:
            mock_cmd.return_value = 0
            assert main(["scan", "test_repo"]) == 0
            mock_cmd.assert_called_once()

    def test_main_export_graph(self):
        """Test running main with export-graph command."""
        with mock.patch("guardian.cli.cmd_export_graph") as mock_cmd:
            mock_cmd.return_value = 0
            assert (
                main(["export-graph", "--repo", "test_repo", "--out", "graph.xml"]) == 0
            )
            mock_cmd.assert_called_once()

    def test_main_stats(self):
        """Test running main with stats command."""
        with mock.patch("guardian.cli.cmd_stats") as mock_cmd:
            mock_cmd.return_value = 0
            assert main(["stats", "test_repo"]) == 0
            mock_cmd.assert_called_once()

    def test_main_demo(self):
        """Test running main with demo command."""
        with mock.patch("guardian.cli.cmd_demo") as mock_cmd:
            mock_cmd.return_value = 0
            assert main(["demo"]) == 0
            mock_cmd.assert_called_once()

    def test_main_invalid_command(self):
        """Test running main with an invalid command."""
        with mock.patch("sys.stderr"), mock.patch("sys.stdout"):
            # Since argparse will call sys.exit, we need to catch it
            with pytest.raises(SystemExit):
                main(["invalid_command"])


class TestScanCommand:
    def test_scan_nonexistent_repo(self):
        """Test scanning a non-existent repository."""
        args = mock.MagicMock()
        args.repo_path = mock.MagicMock()
        args.repo_path.exists.return_value = False

        with mock.patch("sys.stderr"):
            assert cmd_scan(args) == 1

    def test_scan_no_packfiles(self, temp_repo):
        """Test scanning a repository with no packfiles."""
        # Remove packfiles for this test
        pack_dir = temp_repo / ".git" / "objects" / "pack"
        for f in pack_dir.glob("*.pack"):
            f.unlink()

        args = mock.MagicMock()
        args.repo_path = temp_repo

        with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
            assert cmd_scan(args) == 0

    def test_scan_with_packfiles(self, temp_repo):
        """Test scanning a repository with packfiles."""
        args = mock.MagicMock()
        args.repo_path = temp_repo

        # Create a real mock path that exists() will return True for
        pack_dir = mock.MagicMock()
        pack_dir.exists.return_value = True
        pack_dir.is_dir.return_value = True

        # Set up the path structure in a way that matches the implementation
        with mock.patch.object(Path, "exists", return_value=True):
            with mock.patch.object(Path, "is_dir", return_value=True):
                with mock.patch.object(Path, "glob") as mock_glob:
                    # Return our mock pack file
                    mock_pack_path = temp_repo / ".git" / "objects" / "pack"
                    mock_glob.return_value = [mock_pack_path / "pack-test.pack"]

                    # Now patch the actual scan_packfile import
                    with mock.patch("guardian.cli.scan_packfile") as mock_scan:
                        mock_scan.return_value = [{"sha": "1234", "type": "commit"}]

                        with mock.patch("sys.stdout"):
                            assert cmd_scan(args) == 0
                            # Verify scan_packfile was called once
                            mock_scan.assert_called_once()

    def test_scan_with_packfile_error(self, temp_repo):
        """Test scanning a repository with a corrupt packfile."""
        args = mock.MagicMock()
        args.repo_path = temp_repo

        # Create a real mock path that exists() will return True for
        pack_dir = mock.MagicMock()
        pack_dir.exists.return_value = True
        pack_dir.is_dir.return_value = True

        # Set up the path structure in a way that matches the implementation
        with mock.patch.object(Path, "exists", return_value=True):
            with mock.patch.object(Path, "is_dir", return_value=True):
                with mock.patch.object(Path, "glob") as mock_glob:
                    # Return our mock pack file
                    mock_pack_path = temp_repo / ".git" / "objects" / "pack"
                    mock_glob.return_value = [mock_pack_path / "pack-test.pack"]

                    # Now patch the actual scan_packfile import
                    with mock.patch("guardian.cli.scan_packfile") as mock_scan:
                        # This should trigger the except GitObjectError block
                        mock_scan.side_effect = GitObjectError("Invalid packfile")

                        with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
                            assert cmd_scan(args) == 1
                            # Verify scan_packfile was called once
                            mock_scan.assert_called_once()


class TestExportGraphCommand:
    def test_export_nonexistent_repo(self):
        """Test exporting graph from a non-existent repository."""
        args = mock.MagicMock()
        args.repo = mock.MagicMock()
        args.repo.exists.return_value = False
        args.out = "graph.xml"
        args.format = "graphml"

        with mock.patch("sys.stderr"):
            assert cmd_export_graph(args) == 1

    def test_export_graphml(self, temp_repo):
        """Test exporting graph in GraphML format."""
        args = mock.MagicMock()
        args.repo = temp_repo
        args.out = "graph.xml"
        args.format = "graphml"

        with mock.patch("guardian.cli.iter_objects") as mock_iter:
            mock_iter.return_value = [{"sha": "1234", "type": "commit"}]
            with mock.patch("guardian.cli.build_graph") as mock_build:
                mock_graph = mock.MagicMock(spec=nx.DiGraph)
                mock_graph.nodes = {"1234": {"type": "commit"}}
                mock_graph.edges = [("1234", "5678")]
                mock_build.return_value = mock_graph
                with mock.patch("networkx.write_graphml") as mock_write:
                    with mock.patch("sys.stdout"):
                        assert cmd_export_graph(args) == 0
                    mock_write.assert_called_once()

    def test_export_with_object_error(self, temp_repo):
        """Test exporting graph with a Git object error."""
        args = mock.MagicMock()
        args.repo = temp_repo
        args.out = "graph.xml"
        args.format = "graphml"

        with mock.patch("guardian.cli.iter_objects") as mock_iter:
            mock_iter.side_effect = GitObjectError("Invalid object")
            with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
                assert cmd_export_graph(args) == 2


class TestStatsCommand:
    def test_stats_nonexistent_repo(self):
        """Test getting stats for a non-existent repository."""
        args = mock.MagicMock()
        args.repo_path = mock.MagicMock()
        args.repo_path.exists.return_value = False
        args.detailed = False

        with mock.patch("sys.stderr"):
            assert cmd_stats(args) == 1

    def test_stats_basic(self, temp_repo):
        """Test getting basic repository stats."""
        args = mock.MagicMock()
        args.repo_path = temp_repo
        args.detailed = False

        with mock.patch("guardian.cli.iter_objects") as mock_iter:
            mock_iter.return_value = [
                {"sha": "1234", "type": "commit"},
                {"sha": "5678", "type": "tree"},
                {"sha": "abcd", "type": "blob"},
            ]
            with mock.patch("sys.stdout"):
                assert cmd_stats(args) == 0

    def test_stats_with_object_error(self, temp_repo):
        """Test getting stats with a Git object error."""
        args = mock.MagicMock()
        args.repo_path = temp_repo
        args.detailed = False

        with mock.patch("guardian.cli.iter_objects") as mock_iter:
            mock_iter.side_effect = GitObjectError("Invalid object")
            with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
                assert cmd_stats(args) == 2


class TestDemoCommand:
    def test_demo_nonexistent_repo(self):
        """Test running demo with a non-existent repository."""
        args = mock.MagicMock()
        args.repo = mock.MagicMock()
        args.repo.exists.return_value = False

        with mock.patch("sys.stderr"):
            assert cmd_demo(args) == 1

    def test_demo_with_repo(self, temp_repo):
        """Test running demo with a valid repository."""
        args = mock.MagicMock()
        args.repo = temp_repo

        with mock.patch("guardian.cli.run_tui") as mock_tui:
            assert cmd_demo(args) == 0
            mock_tui.assert_called_once_with(temp_repo, demo_mode=True)
