"""Terminal User Interface for Repo-Guardian.

This module provides the TUI functionality for interacting with Repo-Guardian.
"""

import os
import threading
import time
from pathlib import Path
from typing import Dict, List

from rich import box
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text


class RepoGuardianTUI:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.console = Console()
        self.issues: List[Dict] = []
        self.selected_issue_index = 0
        self.layout = self._create_layout()
        self.running = True
        self.scanning = False
        self.scan_progress = 0.0
        self.scroll_offset = 0
        self.max_visible_issues = 10
        self.repair_in_progress = False
        self.status_message = ""

    def _create_layout(self) -> Layout:
        layout = Layout(name="root")

        layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=8),
            Layout(name="footer", size=3),
        )

        layout["body"].split_row(
            Layout(name="errors", ratio=2),
            Layout(name="commands", ratio=1),
        )

        return layout

    def _render_header(self) -> Panel:
        progress = Progress(
            TextColumn("[bold blue]Scanning Repository"),
            BarColumn(),
            TaskProgressColumn(),
            expand=True,
        )

        task_id = progress.add_task("", total=100)
        progress.update(task_id, completed=int(self.scan_progress * 100))

        return Panel(progress, title="REPO-GUARDIAN v0.9.0-beta", border_style="blue")

    def _render_errors_panel(self) -> Panel:
        if not self.issues:
            message = "Scanning in progress..." if self.scanning else "No issues found"
            style = "yellow" if self.scanning else "green"
            return Panel(
                Text(message, style=style), title="ISSUES (0)", border_style="green"
            )

        table = Table(show_header=True, expand=True, box=box.SIMPLE)
        table.add_column("Severity", width=10)
        table.add_column("Description", ratio=2)
        table.add_column("Object ID", ratio=1)

        # Calculate visible range with scrolling
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.max_visible_issues, len(self.issues))

        for i in range(start_idx, end_idx):
            issue = self.issues[i]
            severity = issue.get("severity", "ERROR")
            description = issue.get("description", "Unknown issue")
            object_id = issue.get("object_id", "")

            severity_style = "red bold" if severity == "ERROR" else "yellow"
            row_style = "reverse" if i == self.selected_issue_index else ""

            table.add_row(
                Text(severity, style=severity_style),
                Text(description, style=row_style),
                Text(object_id, style=row_style),
            )

        metadata = {}
        if self.issues and 0 <= self.selected_issue_index < len(self.issues):
            selected_issue = self.issues[self.selected_issue_index]
            metadata = selected_issue.get("metadata", {})

        metadata_text = "\n".join(f"{k}: {v}" for k, v in metadata.items())

        # Break long line
        scroll_text = f"[dim]Showing {start_idx+1}-{end_idx} "
        scroll_text += f"of {len(self.issues)}[/dim]"

        group = Group(
            table,
            Text("\nSelected Issue Details:", style="bold"),
            Text(metadata_text),
            Text(f"\n{scroll_text}", justify="right"),
        )

        title_style = (
            "red"
            if any(i.get("severity") == "ERROR" for i in self.issues)
            else "yellow"
        )
        title = f"ISSUES ({len(self.issues)})"

        return Panel(group, title=title, border_style=title_style)

    def _render_commands_panel(self) -> Panel:
        table = Table(show_header=False, expand=True, box=box.SIMPLE)
        table.add_column("Key", width=8)
        table.add_column("Command", ratio=1)

        commands = [
            ("↑/↓", "Navigate Issues"),
            ("R", "Repair All"),
            ("F", "Fix Selected"),
            ("E", "Export Graph"),
            ("S", "Show Stats"),
            ("PgUp/PgDn", "Scroll List"),
            ("Q", "Quit"),
        ]

        for key, description in commands:
            style = "" if not self.repair_in_progress else "dim"
            table.add_row(
                Text(key, style=f"bold {style}"), Text(description, style=style)
            )

        repair_status = ""
        if self.repair_in_progress:
            repair_status = "\n\n[bold yellow]Repair in progress...[/bold yellow]"

        help_text = (
            "\n\n[blue]Help:[/blue]\n"
            "Use arrow keys to navigate between issues.\n"
            "Press R to repair all issues at once.\n"
            "Press F to fix only the selected issue.\n"
        )

        content = Group(table, Text(repair_status + help_text))

        return Panel(content, title="COMMANDS", border_style="blue")

    def _render_footer(self) -> Panel:
        error_count = sum(
            1 for issue in self.issues if issue.get("severity") == "ERROR"
        )
        warning_count = sum(
            1 for issue in self.issues if issue.get("severity") == "WARNING"
        )

        status_text = Text()

        # Custom status message takes precedence if set
        if self.status_message:
            status_text.append(f"STATUS: {self.status_message}")
        elif self.scanning:
            status_text.append("STATUS: Scanning repository...", style="yellow")
        elif self.repair_in_progress:
            status_text.append("STATUS: Repairing issues...", style="yellow")
        elif self.issues:
            status = "CRITICAL" if error_count > 0 else "WARNING"
            status_style = "red bold" if status == "CRITICAL" else "yellow"
            status_text.append("STATUS: ", style="bold")
            status_text.append(status, style=status_style)
            status_text.append(
                f" - {len(self.issues)} issues found "
                f"({error_count} critical, {warning_count} warning)"
            )
        else:
            status_text.append("STATUS: Repository healthy", style="green bold")

        # Add key hints
        status_text.append(" " * 10 + "Press [Q] to quit, [?] for help", style="dim")

        # Set footer style based on the severity of issues
        if error_count > 0:
            footer_style = "red"
        elif warning_count > 0:
            footer_style = "yellow"
        else:
            footer_style = "green"

        return Panel(status_text, border_style=footer_style)

    def render(self):
        self.layout["header"].update(self._render_header())
        self.layout["errors"].update(self._render_errors_panel())
        self.layout["commands"].update(self._render_commands_panel())
        self.layout["footer"].update(self._render_footer())

        self.console.print(self.layout)

    def add_issue(self, issue: Dict):
        self.issues.append(issue)
        # Auto-sort issues by severity (errors first)
        self.issues.sort(key=lambda x: 0 if x.get("severity") == "ERROR" else 1)

    def handle_key(self, key: str) -> bool:
        if key.lower() == "q":
            return False

        if self.repair_in_progress:
            return True

        if key == "KEY_UP" and self.selected_issue_index > 0:
            self.selected_issue_index -= 1
            # Auto-scroll if necessary
            if self.selected_issue_index < self.scroll_offset:
                self.scroll_offset = self.selected_issue_index
        elif key == "KEY_DOWN" and self.selected_issue_index < len(self.issues) - 1:
            self.selected_issue_index += 1
            # Auto-scroll if necessary
            visible_threshold = self.scroll_offset + self.max_visible_issues
            if self.selected_issue_index >= visible_threshold:
                self.scroll_offset += 1
        elif key == "KEY_PPAGE":  # Page Up
            self.scroll_offset = max(0, self.scroll_offset - self.max_visible_issues)
        elif key == "KEY_NPAGE":  # Page Down
            max_offset = max(0, len(self.issues) - self.max_visible_issues)
            new_offset = self.scroll_offset + self.max_visible_issues
            self.scroll_offset = min(max_offset, new_offset)
        elif key.lower() == "r" and self.issues:
            self.start_repair(repair_all=True)
        elif key.lower() == "f" and self.issues:
            self.start_repair(repair_all=False)
        elif key.lower() == "e":
            self.status_message = "Exporting graph to graphml..."
            # In a real implementation, this would call export functionality
            time.sleep(1)
            self.status_message = "Graph exported successfully"
        elif key.lower() == "s":
            self.status_message = "Generating statistics..."
            # In a real implementation, this would display stats
            time.sleep(1)
            repo_stats = "Repository contains 245 commits, 1023 objects"
            self.status_message = repo_stats

        return True

    def start_repair(self, repair_all: bool = False):
        """Start repair process in a separate thread."""
        self.repair_in_progress = True

        if repair_all:
            self.status_message = "Repairing all issues..."
        else:
            issue = self.issues[self.selected_issue_index]
            object_id = issue.get("object_id", "")
            self.status_message = f"Repairing {object_id}..."

        # Simulate repair in a real implementation
        def repair_task():
            time.sleep(2)

            if repair_all:
                self.issues = []
                self.status_message = "All issues repaired successfully"
            else:
                # Remove the selected issue
                del self.issues[self.selected_issue_index]
                max_idx = max(0, len(self.issues) - 1)
                self.selected_issue_index = min(self.selected_issue_index, max_idx)
                self.status_message = "Issue repaired successfully"

            self.repair_in_progress = False

        threading.Thread(target=repair_task).start()

    def scan_repository(self):
        """Scan repository for issues in a separate thread."""
        self.scanning = True

        def scan_task():
            # Simulate scanning
            for progress in range(0, 101, 5):
                self.scan_progress = progress / 100.0
                time.sleep(0.2)

                # Simulate finding issues at certain points
                if progress == 30:
                    self.add_issue(
                        {
                            "severity": "ERROR",
                            "description": "Invalid checksum in object",
                            "object_id": "d8e8fca2dc0f896fd7cb4cb0031ba249",
                            "metadata": {
                                "Type": "commit",
                                "Path": (
                                    f"{self.repo_path}/.git/objects/"
                                    f"d8/e8fca2dc0f896fd7cb4cb0031ba249"
                                ),
                                "Error": "Checksum mismatch",
                            },
                        }
                    )

                if progress == 60:
                    self.add_issue(
                        {
                            "severity": "WARNING",
                            "description": "Potential rewritten history",
                            "object_id": "between 8af5cb2 and d95679c",
                            "metadata": {
                                "Similarity": "0.92",
                                "Branch": "feature/login",
                                "Base Branch": "main",
                            },
                        }
                    )

                if progress == 80:
                    self.add_issue(
                        {
                            "severity": "ERROR",
                            "description": "Packfile corruption detected",
                            "object_id": "pack-f34be692a.pack",
                            "metadata": {
                                "Size": "4.2MB",
                                "Objects": "182",
                                "Error": "Truncated file",
                            },
                        }
                    )

            self.scanning = False

        threading.Thread(target=scan_task).start()

    def run(self, demo_mode: bool = False):
        """Run the TUI in interactive mode."""
        # Start scanning
        self.scan_repository()

        try:
            import curses

            def _input_loop(stdscr):
                curses.curs_set(0)  # Hide cursor
                stdscr.timeout(100)  # Non-blocking input with 100ms timeout

                while self.running:
                    self.console.clear()
                    self.render()

                    try:
                        key = stdscr.getkey()
                        self.running = self.handle_key(key)
                    except curses.error:
                        # No input available, just continue
                        pass

            curses.wrapper(_input_loop)

        except ImportError:
            # Fallback for environments without curses
            self.console.print(
                "[yellow]Curses not available, running in demo mode[/yellow]"
            )
            self.run_demo()

    def run_demo(self, wait_for_input: bool = True):
        """Run the TUI in demo mode without keyboard input."""
        self.console.clear()
        self.scan_repository()

        # Just render updates in a loop
        start_time = time.time()
        while self.scanning or self.repair_in_progress or time.time() - start_time < 10:
            self.console.clear()
            self.render()
            time.sleep(0.2)

        # Final render
        self.console.clear()
        self.render()

        # Only wait for input if not running in a test environment
        if wait_for_input and "PYTEST_CURRENT_TEST" not in os.environ:
            self.console.input("Press Enter to exit...")


def run_tui(repo_path: Path, demo_mode: bool = False):
    """Run the Terminal User Interface.

    Args:
        repo_path: Path to the Git repository
        demo_mode: Whether to run in demo mode without actual scanning

    Returns:
        None
    """
    tui = RepoGuardianTUI(repo_path)

    # Detect if running in a test environment
    in_test = "PYTEST_CURRENT_TEST" in os.environ

    if demo_mode or in_test:
        tui.run_demo(wait_for_input=not in_test)
    else:
        tui.run()
