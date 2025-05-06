# Repo-Guardian

![Repo-Guardian Logo](img/logo.png)

Welcome to the Repo-Guardian documentation!

## Overview

Repo-Guardian is a powerful tool for analyzing and repairing Git repositories. It specializes in:

- Detecting corrupted Git objects
- Analyzing repository structure with directed acyclic graphs (DAGs)
- Identifying history rewrites using the Jaro-Winkler algorithm
- Providing helpful visualization of repository data

## Key Features

- **Object Scanning**: Detect corruption in loose objects and packfiles
- **DAG Analysis**: Visualize the commit history as a graph
- **History Rewrite Detection**: Find potential history rewrites
- **Repository Repair**: Fix corrupted objects when possible
- **Graph Export**: Export repository graphs in various formats
- **Git Integration**: Post-merge hooks for automated checks

## Why Repo-Guardian?

While Git provides tools like `git fsck` for checking repository integrity, Repo-Guardian offers advanced features for deeper analysis and visualization. It helps repository maintainers identify issues that standard Git tools might miss.

## Getting Started

Check out the [Quick Start](user-guide/quick-start.md) guide to begin using Repo-Guardian, or read the [Installation](user-guide/installation.md) instructions for detailed setup information.

## License

Repo-Guardian is released under the MIT License. See the [LICENSE](https://github.com/yourusername/repo-guardian/blob/main/LICENSE) file for details.
