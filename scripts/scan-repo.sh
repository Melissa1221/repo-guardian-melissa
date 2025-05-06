#!/bin/bash
# Wrapper script for guardian scan command

# Check if a repository path is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <repository_path> [options]"
    exit 1
fi

# Pass all arguments to the guardian scan command
$(dirname "$0")/guardian scan "$@"
