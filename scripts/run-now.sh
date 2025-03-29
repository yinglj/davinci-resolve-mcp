#!/bin/bash
# Quick setup script to get DaVinci Resolve MCP Server running

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"
VENV_DIR="$ROOT_DIR/venv"
SERVER_PATH="$ROOT_DIR/src/resolve_mcp_server.py"

echo -e "${GREEN}Setting up DaVinci Resolve MCP Server with virtual environment...${NC}"

# Create and activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# Install MCP SDK in the virtual environment with CLI support
echo -e "${YELLOW}Installing MCP SDK with CLI support in virtual environment...${NC}"
"$VENV_DIR/bin/pip" install "mcp[cli]"

# Source environment variables from .zshrc if they exist
if grep -q "RESOLVE_SCRIPT_API" "$HOME/.zshrc"; then
    echo -e "${YELLOW}Sourcing environment variables from .zshrc...${NC}"
    source "$HOME/.zshrc"
else
    echo -e "${YELLOW}Setting environment variables...${NC}"
    export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
fi

# Make the server script executable
chmod +x "$SERVER_PATH"

# Check if DaVinci Resolve is running
if ps -ef | grep -i "[D]aVinci Resolve" > /dev/null; then
    echo -e "${GREEN}✓ DaVinci Resolve is running${NC}"
else
    echo -e "${RED}✗ DaVinci Resolve is not running${NC}"
    echo -e "${YELLOW}Please start DaVinci Resolve before continuing${NC}"
    echo -e "${YELLOW}Waiting 10 seconds for you to start DaVinci Resolve...${NC}"
    sleep 10
    if ! ps -ef | grep -i "[D]aVinci Resolve" > /dev/null; then
        echo -e "${RED}DaVinci Resolve still not running. Please start it manually.${NC}"
        echo -e "${YELLOW}You can run this script again after starting DaVinci Resolve.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ DaVinci Resolve is now running${NC}"
fi

# Run the server with the virtual environment's Python
echo -e "${GREEN}Starting DaVinci Resolve MCP Server...${NC}"
echo ""

"$VENV_DIR/bin/mcp" dev "$SERVER_PATH" 