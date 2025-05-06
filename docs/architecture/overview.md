# Architecture Overview

Repo-Guardian is built with a modular architecture that separates concerns into distinct components. This page provides a high-level overview of the system architecture.

## Component Architecture

The main components of Repo-Guardian are:

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  Command Line     │     │  Terminal User    │     │  Git Hook         │
│  Interface (CLI)  │     │  Interface (TUI)  │     │  Integration      │
│                   │     │                   │     │                   │
└─────────┬─────────┘     └─────────┬─────────┘     └─────────┬─────────┘
          │                         │                         │
          │                         │                         │
          │                         │                         │
          │                         ▼                         │
          │               ┌───────────────────┐               │
          └───────────────►                   ◄───────────────┘
                          │  Core Services    │
                          │                   │
                          └─────────┬─────────┘
                                    │
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  Object Scanner   │     │  DAG Builder      │     │  JW Detector      │
│                   │     │                   │     │                   │
└─────────┬─────────┘     └─────────┬─────────┘     └─────────┬─────────┘
          │                         │                         │
          │                         │                         │
          ▼                         ▼                         ▼
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  Git Objects      │     │  Repository Graph │     │  History Analysis │
│                   │     │                   │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

## Main Modules

### 1. User Interfaces

- **CLI (`cli.py`)**: Command-line interface for all Repo-Guardian functions
- **TUI (`tui.py`)**: Interactive terminal user interface for browsing repositories
- **Git Hook Integration**: Scripts for automating Repo-Guardian in Git workflows

### 2. Core Services

- **Object Scanner (`object_scanner.py`)**: Detects corrupted Git objects
- **DAG Builder (`dag_builder.py`)**: Creates and analyzes commit graphs
- **Jaro-Winkler Detector (`jw_detector.py`)**: Identifies history rewrites
- **Repair (`repair.py`)**: Attempts to repair corrupted Git objects

### 3. Supporting Modules

- **Utils (`utils.py`)**: Shared utility functions
- **Benchmarking (`bench.py`)**: Performance measurement tools

## Data Flow

1. User input is received through the CLI, TUI, or Git hooks
2. The request is processed by the appropriate core service
3. Core services interact with the Git repository to fetch objects
4. Results are processed and returned to the user interface

## Design Principles

Repo-Guardian follows these key design principles:

1. **Modularity**: Components are loosely coupled and independently testable
2. **Extensibility**: New features can be added without modifying existing code
3. **Efficiency**: Performance is optimized for handling large repositories
4. **Robustness**: Error handling is comprehensive to deal with corrupt repositories
5. **Usability**: User interfaces are designed for clarity and ease of use
