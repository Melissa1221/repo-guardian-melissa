"""Step implementations for object corruption detection features."""
import shlex
import subprocess
from pathlib import Path

from behave import given, then, when


@given('un repositorio con packfile "{path}"')
def step_repo_with_packfile(context, path):
    """Set up a repository with a packfile."""
    # Store the path for later use
    context.repo_path = path

    # Verify the fixture exists
    fixture_path = Path(path)
    assert fixture_path.exists(), f"Fixture path {path} does not exist"

    # Make sure this is a valid git repository path
    objects_dir = fixture_path / "objects"
    assert objects_dir.exists(), f"Not a valid git repository: {path}"

    # Make sure it has a pack directory
    pack_dir = objects_dir / "pack"
    assert pack_dir.exists(), f"Repository does not have a pack directory: {path}"

    # Verify at least one packfile exists
    pack_files = list(pack_dir.glob("*.pack"))
    assert len(pack_files) > 0, f"No packfiles found in {path}/objects/pack"


@when('ejecuto "{command}"')
def step_execute_command(context, command):
    """Execute a command and capture its output."""
    # Split the command into tokens
    cmd_tokens = shlex.split(command)

    # If the command starts with "guardian", use our script path
    if cmd_tokens[0] == "guardian":
        # Replace with full path to our script
        script_path = Path("scripts/guardian").absolute()
        cmd_tokens[0] = str(script_path)

    # Execute the command
    result = subprocess.run(
        cmd_tokens,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    # Store the result for later verification
    context.command_result = result


@then('el exit code es {code:d}')
def step_verify_exit_code(context, code):
    """Verify the exit code of the last command."""
    assert hasattr(context, "command_result"), "No command has been executed"
    assert context.command_result.returncode == code, (
        f"Expected exit code {code}, but got {context.command_result.returncode}"
    )


@then('la salida contiene "{text}"')
def step_verify_output_contains(context, text):
    """Verify the output of the last command contains the specified text."""
    assert hasattr(context, "command_result"), "No command has been executed"

    # Check both stdout and stderr
    output = context.command_result.stdout + context.command_result.stderr
    assert text in output, f"Expected output to contain '{text}', but it didn't"
