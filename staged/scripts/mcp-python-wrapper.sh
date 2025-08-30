#!/bin/bash

# MCP Python Wrapper Script for Syn OS
# This script ensures MCP servers run with the correct Python environment

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Path to MCP virtual environment
MCP_VENV_PATH="$PROJECT_ROOT/venv_mcp"

# Check if virtual environment exists
if [ ! -d "$MCP_VENV_PATH" ]; then
    echo "Error: MCP virtual environment not found at $MCP_VENV_PATH" >&2
    exit 1
fi

# Activate virtual environment and run the MCP server
source "$MCP_VENV_PATH/bin/activate"

# Run the Python script passed as argument
exec python3 "$@"