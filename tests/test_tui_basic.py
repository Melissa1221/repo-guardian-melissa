import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from guardian.tui import RepoGuardianTUI, run_tui
from rich.console import Console
from rich.panel import Panel


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


@pytest.fixture
def tui_instance(temp_repo):
    """Return a TUI instance for testing."""
    return RepoGuardianTUI(temp_repo)


class TestTUIBasic:
    def test_init(self, tui_instance, temp_repo):
        """Test TUI initialization."""
        assert tui_instance.repo_path == temp_repo
        assert isinstance(tui_instance.console, Console)
        assert tui_instance.issues == []
        assert tui_instance.selected_issue_index == 0
        assert tui_instance.layout is not None

    def test_create_layout(self, tui_instance):
        """Test layout creation."""
        layout = tui_instance._create_layout()
        assert layout.name == "root"
        assert layout.children[0].name == "header"
        assert layout.children[1].name == "body"
        assert layout.children[2].name == "footer"
        assert layout.children[1].children[0].name == "errors"
        assert layout.children[1].children[1].name == "commands"

    def test_render_header(self, tui_instance):
        """Test header rendering."""
        panel = tui_instance._render_header()
        assert isinstance(panel, Panel)
        assert "REPO-GUARDIAN" in panel.title

    def test_render_errors_panel_empty(self, tui_instance):
        """Test rendering errors panel with no issues."""
        panel = tui_instance._render_errors_panel()
        assert isinstance(panel, Panel)
        assert "ERRORS (0)" in panel.title

    def test_render_errors_panel_with_issues(self, tui_instance):
        """Test rendering errors panel with issues."""
        # Add a test issue
        tui_instance.add_issue(
            {
                "severity": "ERROR",
                "description": "Test error",
                "object_id": "test123",
            }
        )

        panel = tui_instance._render_errors_panel()
        assert "ERRORS (1)" in panel.title

    def test_render_commands_panel(self, tui_instance):
        """Test rendering commands panel."""
        panel = tui_instance._render_commands_panel()
        assert isinstance(panel, Panel)
        assert "COMMANDS" in panel.title

    def test_render_footer(self, tui_instance):
        """Test rendering footer panel."""
        panel = tui_instance._render_footer()
        assert isinstance(panel, Panel)
        assert "No issues found" in str(panel.renderable)

    def test_add_issue(self, tui_instance):
        """Test adding an issue."""
        issue = {
            "severity": "ERROR",
            "description": "Test error",
            "object_id": "test123",
        }
        tui_instance.add_issue(issue)

        assert len(tui_instance.issues) == 1
        assert tui_instance.issues[0] == issue

    @mock.patch("os.environ", {})
    @mock.patch("rich.console.Console.input")
    @mock.patch("rich.console.Console.print")
    @mock.patch("rich.console.Console.clear")
    def test_run_demo(self, mock_clear, mock_print, mock_input, tui_instance):
        """Test running demo mode."""
        tui_instance.run_demo()

        # Verify console methods were called
        mock_clear.assert_called_once()
        assert mock_print.call_count > 0
        mock_input.assert_called_once()

        # Verify issues were added
        assert len(tui_instance.issues) >= 2

    @mock.patch("guardian.tui.RepoGuardianTUI")
    def test_run_tui(self, mock_tui_class, temp_repo):
        """Test the run_tui function."""
        mock_tui_instance = mock.MagicMock()
        mock_tui_class.return_value = mock_tui_instance

        # Test with demo mode = True
        run_tui(temp_repo, demo_mode=True)
        mock_tui_class.assert_called_once_with(temp_repo)
        mock_tui_instance.run_demo.assert_called_once()

        # Reset mocks and test with demo mode = False
        mock_tui_class.reset_mock()
        mock_tui_instance.reset_mock()

        run_tui(temp_repo, demo_mode=False)
        mock_tui_class.assert_called_once_with(temp_repo)
        mock_tui_instance.run_demo.assert_called_once()
