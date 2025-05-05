"""Unit tests for the TUI module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from guardian.tui import RepoGuardianTUI, run_tui
from rich.console import Console


@pytest.fixture
def mock_repo_path():
    """Return a fake repository path for testing."""
    return Path("/fake/repo/path")


@pytest.fixture
def tui_instance(mock_repo_path):
    """Return a TUI instance for testing."""
    return RepoGuardianTUI(mock_repo_path)


def test_tui_init(tui_instance, mock_repo_path):
    """Test TUI initialization."""
    assert tui_instance.repo_path == mock_repo_path
    assert isinstance(tui_instance.console, Console)
    assert tui_instance.issues == []
    assert tui_instance.selected_issue_index == 0
    assert tui_instance.layout is not None
    assert tui_instance.running is True
    assert tui_instance.scanning is False
    assert tui_instance.scan_progress == 0.0
    assert tui_instance.scroll_offset == 0
    assert tui_instance.max_visible_issues == 10
    assert tui_instance.repair_in_progress is False
    assert tui_instance.status_message == ""


def test_create_layout(tui_instance):
    """Test layout creation."""
    layout = tui_instance._create_layout()
    assert layout.name == "root"
    assert layout.children[0].name == "header"
    assert layout.children[1].name == "body"
    assert layout.children[2].name == "footer"
    assert layout.children[1].children[0].name == "errors"
    assert layout.children[1].children[1].name == "commands"


def test_render_header(tui_instance):
    """Test header rendering."""
    panel = tui_instance._render_header()
    assert "REPO-GUARDIAN v0.9.0-beta" in panel.title
    assert panel.border_style == "blue"


def test_render_errors_panel_empty(tui_instance):
    """Test errors panel rendering with no issues."""
    panel = tui_instance._render_errors_panel()
    # Check that "No issues found" text is in the panel
    rendered_text = panel.renderable.plain
    assert "No issues found" in rendered_text
    assert panel.title == "ISSUES (0)"
    assert panel.border_style == "green"


def test_render_errors_panel_scanning(tui_instance):
    """Test errors panel rendering while scanning."""
    tui_instance.scanning = True
    panel = tui_instance._render_errors_panel()
    rendered_text = panel.renderable.plain
    assert "Scanning in progress" in rendered_text
    assert panel.border_style == "green"


@patch("rich.table.Table.add_row")
@patch("rich.text.Text")
def test_render_errors_panel_with_issues(mock_text, mock_add_row, tui_instance):
    """Test errors panel rendering with issues."""
    # Add a test issue
    tui_instance.add_issue(
        {
            "severity": "ERROR",
            "description": "Test error",
            "object_id": "test123",
            "metadata": {"test": "metadata"},
        }
    )

    # Call the method
    panel = tui_instance._render_errors_panel()

    # Verify the panel was created with correct title and style
    assert panel.title == "ISSUES (1)"
    assert panel.border_style == "red"

    # Verify add_row was called (at least once)
    mock_add_row.assert_called()


def test_render_commands_panel(tui_instance):
    """Test commands panel rendering."""
    panel = tui_instance._render_commands_panel()
    assert panel.title == "COMMANDS"
    assert panel.border_style == "blue"


def test_render_footer_no_issues(tui_instance):
    """Test footer rendering with no issues."""
    panel = tui_instance._render_footer()
    rendered_text = str(panel.renderable)
    assert "Repository healthy" in rendered_text
    assert panel.border_style == "green"


@patch("rich.text.Text.append")
def test_render_footer_with_issues(mock_append, tui_instance):
    """Test footer rendering with issues."""
    # Add test issues - only add ERROR to trigger red border
    tui_instance.add_issue(
        {
            "severity": "ERROR",
            "description": "Test error",
            "object_id": "test123",
        }
    )

    # Call the method
    panel = tui_instance._render_footer()

    # Verify the panel has the correct border style
    assert panel.border_style == "red"

    # Verify Text.append was called multiple times
    assert mock_append.call_count > 1


def test_add_issue(tui_instance):
    """Test adding issues."""
    # Add two issues
    tui_instance.add_issue(
        {
            "severity": "WARNING",
            "description": "Test warning",
            "object_id": "warn123",
        }
    )
    tui_instance.add_issue(
        {
            "severity": "ERROR",
            "description": "Test error",
            "object_id": "err123",
        }
    )

    # Should have 2 issues, sorted by severity (ERROR first)
    assert len(tui_instance.issues) == 2
    assert tui_instance.issues[0]["severity"] == "ERROR"
    assert tui_instance.issues[1]["severity"] == "WARNING"


def test_handle_key_navigation(tui_instance):
    """Test keyboard navigation handling."""
    # Add test issues
    for i in range(15):
        tui_instance.add_issue(
            {
                "severity": "ERROR" if i % 2 == 0 else "WARNING",
                "description": f"Test issue {i}",
                "object_id": f"test{i}",
            }
        )

    # Test navigation keys
    assert tui_instance.selected_issue_index == 0

    # Down key
    assert tui_instance.handle_key("KEY_DOWN") is True
    assert tui_instance.selected_issue_index == 1

    # Multiple down keys
    for _ in range(12):
        tui_instance.handle_key("KEY_DOWN")
    assert tui_instance.selected_issue_index > 10

    # Up key
    assert tui_instance.handle_key("KEY_UP") is True
    assert tui_instance.selected_issue_index < 14

    # Page keys
    assert tui_instance.handle_key("KEY_PPAGE") is True  # Page up
    assert tui_instance.handle_key("KEY_NPAGE") is True  # Page down


def test_handle_key_quit(tui_instance):
    """Test quit key handling."""
    assert tui_instance.handle_key("q") is False
    assert tui_instance.handle_key("Q") is False


def test_handle_key_actions(tui_instance):
    """Test action key handling."""
    # Add a test issue
    tui_instance.add_issue(
        {
            "severity": "ERROR",
            "description": "Test error",
            "object_id": "test123",
        }
    )

    # Mock threading to avoid actual thread creation
    with patch("threading.Thread") as mock_thread:
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Test repair keys
        assert tui_instance.handle_key("r") is True
        assert tui_instance.repair_in_progress is True
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

        # Reset and test fix selected
        mock_thread.reset_mock()
        mock_thread_instance.reset_mock()
        tui_instance.repair_in_progress = False

        assert tui_instance.handle_key("f") is True
        assert tui_instance.repair_in_progress is True
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()


def test_start_repair(tui_instance):
    """Test repair process."""
    # Add a test issue
    tui_instance.add_issue(
        {
            "severity": "ERROR",
            "description": "Test error",
            "object_id": "test123",
        }
    )

    # Mock threading.Thread to prevent actual thread creation
    with patch("threading.Thread") as mock_thread:
        # Test repair all
        tui_instance.start_repair(repair_all=True)
        assert tui_instance.repair_in_progress is True
        assert "Repairing all issues" in tui_instance.status_message
        mock_thread.assert_called_once()

        # Reset mocks
        mock_thread.reset_mock()
        tui_instance.repair_in_progress = False

        # Test fix selected
        tui_instance.start_repair(repair_all=False)
        assert tui_instance.repair_in_progress is True
        assert "Repairing" in tui_instance.status_message
        mock_thread.assert_called_once()


def test_run_tui_demo_mode():
    """Test running TUI in demo mode."""
    repo_path = Path("/test/repo")

    # Mock RepoGuardianTUI
    with patch("guardian.tui.RepoGuardianTUI") as mock_tui_cls:
        mock_tui = mock_tui_cls.return_value

        # Run in demo mode
        run_tui(repo_path, demo_mode=True)

        # Verify demo mode was used
        mock_tui_cls.assert_called_once_with(repo_path)
        mock_tui.run_demo.assert_called_once()


def test_run_tui_interactive():
    """Test running TUI in interactive mode."""
    repo_path = Path("/test/repo")

    # Mock RepoGuardianTUI and os.environ
    with patch("guardian.tui.RepoGuardianTUI") as mock_tui_cls, patch.dict(
        "os.environ", {}, clear=True
    ):
        mock_tui = mock_tui_cls.return_value

        # Run in interactive mode
        run_tui(repo_path, demo_mode=False)

        # Verify interactive mode was used
        mock_tui_cls.assert_called_once_with(repo_path)
        mock_tui.run.assert_called_once()


def test_scan_repository(tui_instance):
    """Test repository scanning."""
    # Mock threading to avoid actual thread creation
    with patch("threading.Thread") as mock_thread:
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Call scan_repository
        tui_instance.scan_repository()

        # Verify a thread was created and started
        assert tui_instance.scanning is True
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()


def test_run_with_curses(tui_instance):
    """Test run method with curses available."""
    # Mock scan_repository to prevent actual scanning
    with patch.object(tui_instance, "scan_repository") as mock_scan:
        # Mock curses
        mock_curses = MagicMock()
        mock_stdscr = MagicMock()

        # Configure mock to simulate key events
        def wrapper_side_effect(func):
            # Call the wrapped function with mock stdscr
            func(mock_stdscr)
            return 0

        mock_curses.wrapper.side_effect = wrapper_side_effect

        # Configure stdscr to return 'q' on first getkey call
        mock_stdscr.getkey.return_value = "q"

        # Run with mocked curses
        with patch.dict("sys.modules", {"curses": mock_curses}):
            tui_instance.run()

        # Verify scanning was started
        mock_scan.assert_called_once()

        # Verify wrapper was called
        mock_curses.wrapper.assert_called_once()


def test_run_without_curses(tui_instance):
    """Test run method when curses is not available."""
    # Mock scan_repository and run_demo to prevent actual execution
    with patch.object(tui_instance, "scan_repository") as mock_scan, patch.object(
        tui_instance, "run_demo"
    ) as mock_run_demo:
        # Run with curses import error
        with patch.dict("sys.modules", {"curses": None}), patch(
            "builtins.__import__", side_effect=ImportError
        ), patch.object(tui_instance.console, "print"):
            tui_instance.run()

        # Verify scanning was started and demo mode was used as fallback
        mock_scan.assert_called_once()
        mock_run_demo.assert_called_once()


def test_run_demo_with_console_input(tui_instance):
    """Test demo mode with console input."""
    # Mock scan_repository to prevent actual scanning
    with patch.object(tui_instance, "scan_repository") as mock_scan:
        # Mock time.time and sleep to control demo duration
        with patch("time.time") as mock_time, patch(
            "time.sleep"
        ), patch.dict("os.environ", {}, clear=True), patch.object(
            tui_instance.console, "clear"
        ), patch.object(tui_instance.console, "print"), patch.object(
            tui_instance.console, "input"
        ) as mock_input, patch.object(tui_instance, "render"):
            # First call returns start time, second call is for the loop check
            mock_time.side_effect = [100, 111]  # 11 seconds elapsed

            # Run demo with wait for input
            tui_instance.run_demo(wait_for_input=True)

            # Verify scan was started
            mock_scan.assert_called_once()

            # Verify input was waited for
            mock_input.assert_called_once()


def test_run_demo_in_test_environment(tui_instance):
    """Test demo mode in test environment."""
    # Mock scan_repository to prevent actual scanning
    with patch.object(tui_instance, "scan_repository") as mock_scan:
        # Mock time.time and sleep to control demo duration
        with patch("time.time") as mock_time, patch(
            "time.sleep"
        ), patch.dict(
            "os.environ", {"PYTEST_CURRENT_TEST": "yes"}, clear=False
        ), patch.object(tui_instance.console, "clear"), patch.object(
            tui_instance.console, "print"
        ), patch.object(tui_instance.console, "input") as mock_input, patch.object(
            tui_instance, "render"
        ):
            # First call returns start time, second call is for the loop check
            mock_time.side_effect = [100, 111]  # 11 seconds elapsed

            # Run demo without waiting for input due to test environment
            tui_instance.run_demo(wait_for_input=True)

            # Verify scan was started
            mock_scan.assert_called_once()

            # Verify input was not waited for in test environment
            mock_input.assert_not_called()
