"""Terminal User Interface for Repo-Guardian.

This module provides the TUI functionality for interacting with Repo-Guardian.
"""

import os
from pathlib import Path
from typing import Dict, List

from rich.console import Console
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

    def _render_header(self, progress_value: float = 0.0) -> Panel:
        progress = Progress(
            TextColumn("[bold blue]Scanning Repository"),
            BarColumn(),
            TaskProgressColumn(),
            expand=True,
        )

        return Panel(progress, title="REPO-GUARDIAN v0.1.0")

    def _render_errors_panel(self) -> Panel:
        if not self.issues:
            return Panel(Text("No issues found", style="green"), title="ERRORS (0)")

        table = Table(show_header=False, expand=True)
        table.add_column("Issues", ratio=1)

        for i, issue in enumerate(self.issues):
            severity = issue.get("severity", "ERROR")
            style = "red" if severity == "ERROR" else "yellow"
            description = issue.get("description", "Unknown issue")
            object_id = issue.get("object_id", "")

            row_text = Text()
            row_text.append(f"[{severity}] ", style=style)
            row_text.append(f"{description}\n")
            row_text.append(f"{object_id}\n")

            if "metadata" in issue:
                for key, value in issue["metadata"].items():
                    row_text.append(f"{key}: {value}\n")

            # Highlight selected row by setting its style directly
            if i == self.selected_issue_index:
                row_text.stylize("reverse")
                table.add_row(row_text)
            else:
                table.add_row(row_text)

        return Panel(table, title=f"ERRORS ({len(self.issues)})")

    def _render_commands_panel(self) -> Panel:
        table = Table(show_header=False, expand=True)
        table.add_column("Command", ratio=1)

        commands = [
            ("[R]", "Repair All"),
            ("[F]", "Fix Selected"),
            ("[E]", "Export Graph"),
            ("[S]", "Show Stats"),
            ("[D]", "Detailed View"),
            ("[Q]", "Quit"),
        ]

        for key, description in commands:
            text = Text()
            text.append(key, style="bold")
            text.append(f" {description}")
            table.add_row(text)

        return Panel(table, title="COMMANDS")

    def _render_footer(self) -> Panel:
        error_count = sum(
            1 for issue in self.issues if issue.get("severity") == "ERROR"
        )
        warning_count = sum(
            1 for issue in self.issues if issue.get("severity") == "WARNING"
        )

        status_text = Text()
        status_text.append("STATUS: ")
        if self.issues:
            status_text.append(
                f"{len(self.issues)} issues found "
                f"({error_count} critical, {warning_count} warning)"
            )
        else:
            status_text.append("No issues found", style="green")

        status_text.append(" " * 20 + "[ESC] to exit", style="dim")

        return Panel(status_text)

    def render(self, progress_value: float = 1.0):
        self.layout["header"].update(self._render_header(progress_value))
        self.layout["errors"].update(self._render_errors_panel())
        self.layout["commands"].update(self._render_commands_panel())
        self.layout["footer"].update(self._render_footer())

        self.console.print(self.layout)

    def add_issue(self, issue: Dict):
        self.issues.append(issue)

    def run_demo(self, wait_for_input: bool = True):
        self.console.clear()

        with Progress() as progress:
            scan_task = progress.add_task("[green]Scanning repository...", total=100)

            # Simulate work and add sample issues
            for i in range(0, 101, 25):
                progress.update(scan_task, completed=i)

                if i == 25:
                    self.add_issue(
                        {
                            "severity": "ERROR",
                            "description": "Invalid checksum in object",
                            "object_id": "d8e8fca2dc0f896fd7cb4cb0031ba249",
                            "metadata": {"Type": "commit"},
                        }
                    )

                if i == 75:
                    self.add_issue(
                        {
                            "severity": "WARNING",
                            "description": "Potential rewritten history",
                            "object_id": "between 8af5cb2 and d95679c",
                            "metadata": {"Similarity": "0.92"},
                        }
                    )

                # Render the progress
                self.render(progress_value=i / 100)

        # Final render with completed progress
        self.render(progress_value=1.0)

        # Only wait for input if not running in a test environment
        if wait_for_input:
            self.console.input("Press Enter to exit...")


def run_tui(repo_path: Path, demo_mode: bool = False):
    tui = RepoGuardianTUI(repo_path)

    # Detect if running in a test environment
    in_test = "PYTEST_CURRENT_TEST" in os.environ

    if demo_mode:
        tui.run_demo(wait_for_input=not in_test)
    else:
        # Real implementation would perform actual repository scanning here
        tui.run_demo(wait_for_input=not in_test)  # Temporary fallback to demo mode
