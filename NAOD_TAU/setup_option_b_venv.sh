#!/bin/bash

################################################################################
# SETUP OPTION B: Local Virtual Environment Setup (venv)
#
# This script creates a local Python virtual environment and installs all
# required packages for NAOD_TAU. Use this if CERN's LCG environment doesn't work.
#
# USAGE:
#   bash setup_option_b_venv.sh
#
# This will:
#   1. Create a local venv at ./.venv_local
#   2. Install all required packages (numpy, awkward, matplotlib, uproot, coffea)
#   3. Provide instructions on how to activate/use the environment
#
################################################################################

set -e  # Exit on first error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}NAOD_TAU Setup Option B: venv${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Error: python3 not found${NC}"
    echo "Please install Python 3.8+ before running this script"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
echo ""

# Set venv path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
VENV_DIR="${PROJECT_ROOT}/.venv_local"

echo -e "${BLUE}Creating virtual environment at: ${VENV_DIR}${NC}"

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi

echo ""
echo -e "${BLUE}Activating virtual environment...${NC}"
cd "$PROJECT_ROOT"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install requirements
echo ""
echo -e "${BLUE}Installing required packages...${NC}"
echo "This may take a few minutes..."
echo ""

pip install -r "${SCRIPT_DIR}/requirements.txt"

echo ""
echo -e "${GREEN}✓ All packages installed successfully${NC}"
echo ""

# Verify installation
echo -e "${BLUE}Verifying installation...${NC}"
python3 -c "
import sys
import numpy, awkward, matplotlib, uproot
try:
    from coffea.nanoevents import NanoEventsFactory
    print('✓ All core packages verified')
except ImportError as e:
    print(f'⚠ Warning: {e}')
    sys.exit(1)
"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. Activate the environment in your shell:"
echo -e "   ${BLUE}source .venv_local/bin/activate${NC}"
echo ""
echo "2. Verify it's working by running the analysis:"
echo -e "   ${BLUE}python NAOD_TAU/read_nanoaodsim_analysis.py${NC}"
echo ""
echo "3. To deactivate the environment, run:"
echo -e "   ${BLUE}deactivate${NC}"
echo ""
echo -e "${YELLOW}SWITCHING BETWEEN SETUPS:${NC}"
echo ""
echo "Option A (CERN LCG):"
echo -e "  ${BLUE}source NAOD_TAU/setup.sh${NC}"
echo ""
echo "Option B (Local venv):"
echo -e "  ${BLUE}source .venv_local/bin/activate${NC}"
echo ""
