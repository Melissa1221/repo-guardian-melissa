# Quick Start

This guide will help you get started with Repo-Guardian quickly.

## Basic Usage

After [installing](installation.md) Repo-Guardian, you can start using it with these simple commands:

### Scanning a Repository

The most basic operation is scanning a repository for corrupted objects:

```bash
guardian scan /path/to/repository
```

This will scan the repository at the specified path and report any issues found.

### Using the Terminal UI

For a more interactive experience, you can use the terminal UI:

```bash
guardian tui /path/to/repository
```

This will open an interactive terminal interface that allows you to navigate through the repository structure and examine issues in detail.

## Exporting Repository Graphs

Repo-Guardian can export the commit graph of a repository:

```bash
guardian export-graph --repo /path/to/repository --out graph.graphml
```

Supported formats include:
- GraphML (default): `--format graphml`
- GEXF: `--format gexf`
- JSON: `--format json`

These files can be opened in graph visualization tools like Gephi or Cytoscape.

## Using the Wrapper Script

For convenience, you can use the wrapper script:

```bash
./scripts/scan-repo.sh /path/to/repository
```

Options:
- `--threads N`: Use N threads for scanning
- `--repair`: Attempt to repair corrupted objects
- `--export`: Export the repository graph

## Detecting History Rewrites

To check if a repository might have had its history rewritten:

```bash
guardian detect-rewrites /path/to/repository
```

This uses the Jaro-Winkler algorithm to identify potential history rewrites.

## Automating with Git Hooks

To automatically scan your repository after merges:

```bash
guardian install-hook
```

This installs a post-merge hook that runs Repo-Guardian after each merge operation.

## Getting Help

For detailed information on any command:

```bash
guardian <command> --help
```

For general help:

```bash
guardian --help
```
