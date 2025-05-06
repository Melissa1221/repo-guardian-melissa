# Contributing to Repo-Guardian

Thank you for your interest in contributing to Repo-Guardian! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others when participating in discussions, submitting code, or reporting issues.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** to your local machine.
3. **Set up the development environment** following the instructions in the [Installation guide](user-guide/installation.md).

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/XXX` for new features
- `bugfix/XXX` for bug fixes
- `docs/XXX` for documentation changes
- `refactor/XXX` for code refactoring

### 2. Make Your Changes

- Write your code following the coding standards (outlined below).
- Add or update tests as necessary.
- Add or update documentation as necessary.

### 3. Run Tests and Linting

Before submitting your changes, make sure all tests pass and the code passes linting:

```bash
# Run tests
pytest

# Run linter
ruff src tests

# Format code
ruff format src tests
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Add feature X"
```

Please follow these commit message guidelines:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and pull requests liberally after the first line

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Submit a Pull Request

Go to the GitHub page of your fork, and submit a pull request to the main repository's `main` branch.

## Coding Standards

- Follow PEP 8 style guide for Python code.
- Use type hints for function parameters and return values.
- Document all public functions, classes, and methods with docstrings in Google style.
- Keep functions focused on a single responsibility.
- Write descriptive variable and function names.

## Testing

- Write unit tests for all new functionality.
- Aim for at least 80% test coverage.
- Consider adding BDD scenarios for major features.

## Documentation

- Update the documentation for any changes to user-facing functionality.
- Add docstrings to all public functions, classes, and methods.
- Keep the README and other documentation up-to-date.

## Issue Reporting

- Use the issue tracker to report bugs or suggest features.
- Check existing issues before opening a new one.
- Provide detailed steps to reproduce bugs.
- Include your environment information (OS, Python version, etc.).

Thank you for contributing to Repo-Guardian!
