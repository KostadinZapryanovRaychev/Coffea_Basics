#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up NAOD_TAU venv...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Install Python 3.8+"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
VENV_DIR="${PROJECT_ROOT}/.venv_local"

python3 -m venv "$VENV_DIR"
cd "$PROJECT_ROOT"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel
pip install -r "${SCRIPT_DIR}/requirements.txt"

python3 -c "from coffea.nanoevents import NanoEventsFactory; print('✓ All packages installed')"

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Activate with: source .venv_local/bin/activate"
echo "Run: python NAOD_TAU/read_nanoaodsim_analysis.py"
echo ""
