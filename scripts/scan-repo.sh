#!/usr/bin/env bash
set -euo pipefail

THREADS=1
REPAIR=0
EXPORT=0

function usage() {
  echo "Usage: $0 <repo_path> [options]"
  echo "Options:"
  echo "  --threads N   Use N threads for scanning (default: 1)"
  echo "  --repair      Attempt to repair issues"
  echo "  --export      Export repository graph"
  exit 1
}

# Parse arguments
REPO_PATH=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --threads)
      THREADS="$2"
      shift 2
      ;;
    --repair)
      REPAIR=1
      shift
      ;;
    --export)
      EXPORT=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      if [[ -z "$REPO_PATH" ]]; then
        REPO_PATH="$1"
        shift
      else
        echo "Unknown option: $1"
        usage
      fi
      ;;
  esac
done

if [[ -z "$REPO_PATH" ]]; then
  echo "Error: Repository path is required"
  usage
fi

# Build command
CMD="guardian scan $REPO_PATH --threads $THREADS --tui"
if [[ $REPAIR -eq 1 ]]; then
  CMD="$CMD --repair"
fi

if [[ $EXPORT -eq 1 ]]; then
  # Export after scanning
  echo "Will export repository graph after scanning"
  EXPORT_FILE="${REPO_PATH//\//_}_$(date +%Y%m%d%H%M%S).graphml"

  # Run scan first, then export if scan succeeds
  echo "Running: $CMD"
  if $CMD; then
    echo "Exporting graph to $EXPORT_FILE"
    guardian export-graph --repo "$REPO_PATH" --out "$EXPORT_FILE" --format graphml
  fi
else
  # Just run the scan command
  echo "Running: $CMD"
  exec $CMD
fi
