#!/bin/bash

################################################################################
# SETUP OPTION B: Conda Virtual Environment Setup
#
# This script creates a conda environment and installs all required packages
# for NAOD_TAU. Use this if you have conda/mamba installed.
#
# USAGE:
#   bash setup_option_b_conda.sh
#
# This will:
#   1. Create a conda environment named 'naod-tau'
#   2. Install all required packages via conda
#   3. Provide instructions on how to activate/use the environment
#
# REQUIREMENTS:
#   - conda or mamba must be installed
#   - Internet connection for downloading packages
#
################################################################################

set -e  # Exit on first error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}NAOD_TAU Setup Option B: Conda${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if conda or mamba is available
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
    echo -e "${GREEN}✓ Mamba found (faster than conda)${NC}"
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
    echo -e "${GREEN}✓ Conda found${NC}"
else
    echo -e "${RED}Error: conda or mamba not found${NC}"
    echo ""
    echo "Please install Miniconda or Mambaforge:"
    echo "  - Miniconda: https://docs.conda.io/en/latest/miniconda.html"
    echo "  - Mambaforge: https://github.com/conda-forge/mambaforge"
    exit 1
fi

ENV_NAME="naod-tau"
PYTHON_VERSION="3.9"

echo ""
echo -e "${BLUE}Creating conda environment: ${ENV_NAME}${NC}"
echo "Python version: ${PYTHON_VERSION}"
echo ""

# Create conda environment with base packages
$CONDA_CMD create -y -n "$ENV_NAME" python=${PYTHON_VERSION} pip

echo ""
echo -e "${GREEN}✓ Conda environment created${NC}"
echo ""

# Get the shell initialization
echo -e "${BLUE}Initializing conda for your shell...${NC}"
$CONDA_CMD init

echo ""
echo -e "${BLUE}Installing required packages...${NC}"
echo "This may take a few minutes..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"

# Install packages via conda (faster than pip for some packages)
$CONDA_CMD install -y -n "$ENV_NAME" \
    numpy \
    matplotlib \
    pytest

# Activate the environment for pip install
source "$($CONDA_CMD info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"
cd "$PROJECT_ROOT"

# Install remaining packages via pip
echo ""
echo -e "${BLUE}Installing remaining packages via pip...${NC}"
pip install --upgrade pip
pip install awkward uproot coffea

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
echo "1. Activate the environment:"
echo -e "   ${BLUE}conda activate ${ENV_NAME}${NC}"
echo ""
echo "2. Verify it's working by running the analysis:"
echo -e "   ${BLUE}python NAOD_TAU/read_nanoaodsim_analysis.py${NC}"
echo ""
echo "3. To deactivate the environment, run:"
echo -e "   ${BLUE}conda deactivate${NC}"
echo ""
echo -e "${YELLOW}SWITCHING BETWEEN SETUPS:${NC}"
echo ""
echo "Option A (CERN LCG):"
echo -e "  ${BLUE}source NAOD_TAU/setup.sh${NC}"
echo ""
echo "Option B (Conda environment):"
echo -e "  ${BLUE}conda activate ${ENV_NAME}${NC}"
echo ""
echo -e "${YELLOW}USEFUL CONDA COMMANDS:${NC}"
echo ""
echo "  List all environments:"
echo -e "    ${BLUE}conda env list${NC}"
echo ""
echo "  Remove this environment:"
echo -e "    ${BLUE}conda env remove -n ${ENV_NAME}${NC}"
echo ""
echo "  Update packages:"
echo -e "    ${BLUE}conda update -n ${ENV_NAME} --all${NC}"
echo ""
