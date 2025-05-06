# Installation

This guide covers how to install Repo-Guardian on different operating systems.

## Prerequisites

Repo-Guardian requires:

- Python 3.8 or higher
- Git 2.25 or higher
- pip (Python package manager)

## From PyPI (Recommended)

The simplest way to install Repo-Guardian is using pip:

```bash
pip install repo-guardian
```

This will install Repo-Guardian and all its dependencies.

## From Source

For the latest development version or to contribute to the project, you can install from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/repo-guardian.git
   cd repo-guardian
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # Create a new environment
   python -m venv venv

   # Activate (Linux/macOS)
   source venv/bin/activate

   # Activate (Windows)
   venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Verifying Installation

To verify that Repo-Guardian is installed correctly:

```bash
guardian --version
```

You should see the current version number of Repo-Guardian displayed.

## Installing Git Hooks

To automatically scan repositories after merges, you can install the post-merge hook:

```bash
guardian install-hook
```

This will install the hook in the current repository's `.git/hooks` directory.

## Dependencies

The main dependencies of Repo-Guardian are:

- **networkx**: For graph operations
- **rich**: For terminal user interface
- **matplotlib**: For graph visualization
- **pandas**: For data manipulation
- **argcomplete**: For command auto-completion

These are automatically installed when you install Repo-Guardian.
