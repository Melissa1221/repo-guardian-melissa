#!/bin/bash

# Install asciinema if not already installed
command -v asciinema >/dev/null 2>&1 || {
    echo "Installing asciinema..."
    pip install asciinema
}

# Set up output file
OUTPUT_DIR="docs/demo"
mkdir -p $OUTPUT_DIR
OUTPUT_FILE="$OUTPUT_DIR/tui_demo.cast"

# Record the demo
echo "Recording TUI demo to $OUTPUT_FILE..."
asciinema rec $OUTPUT_FILE -c "python -m guardian demo --repo ."

echo "Demo recorded to $OUTPUT_FILE"
echo "You can play it back with: asciinema play $OUTPUT_FILE"
echo "Or convert to GIF with: agg $OUTPUT_FILE demo.gif (requires agg tool)" 