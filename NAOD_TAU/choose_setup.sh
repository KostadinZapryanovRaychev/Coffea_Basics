#!/bin/bash

################################################################################
# NAOD_TAU Interactive Setup Selector
#
# This script helps users choose between different setup options.
#
# USAGE:
#   bash setup.sh  (from any directory, it will guide you)
#
################################################################################

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${BLUE}NAOD_TAU Analysis Framework Setup${NC}${BLUE}              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}Choose your setup option:${NC}"
echo ""
echo -e "${GREEN}[A]${NC} CERN LCG Environment (Original - if available)"
echo -e "    → Uses /cvmfs/sft.cern.ch/lcg/ (requires CERN access)"
echo -e "    → Fastest if available"
echo ""
echo -e "${GREEN}[B1]${NC} Local Python venv (Recommended)"
echo -e "     → Creates .venv_local/ directory"
echo -e "     → Works on any system with Python 3.8+"
echo -e "     → Lightweight setup"
echo ""
echo -e "${GREEN}[B2]${NC} Conda Environment (Best for reproducibility)"
echo -e "     → Creates 'naod-tau' conda environment"
echo -e "     → Requires conda/mamba installed"
echo -e "     → Best dependency management"
echo ""
echo -e "${GREEN}[Q]${NC} Quit"
echo ""
echo -n "Enter your choice [A/B1/B2/Q]: "
read -r choice

case "$choice" in
    [Aa])
        echo ""
        echo -e "${BLUE}Loading CERN LCG environment...${NC}"
        echo ""
        source NAOD_TAU/setup.sh
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✓ CERN LCG environment loaded${NC}"
            echo ""
            echo -e "${YELLOW}Next step:${NC}"
            echo -e "  ${BLUE}python NAOD_TAU/read_nanoaodsim_analysis.py${NC}"
        else
            echo ""
            echo -e "${RED}✗ Failed to load LCG environment${NC}"
            echo -e "Try Option B1 or B2 instead"
        fi
        ;;
    [Bb]1)
        echo ""
        echo -e "${BLUE}Setting up local Python venv...${NC}"
        echo ""
        bash NAOD_TAU/setup_option_b_venv.sh
        ;;
    [Bb]2)
        echo ""
        echo -e "${BLUE}Setting up Conda environment...${NC}"
        echo ""
        bash NAOD_TAU/setup_option_b_conda.sh
        ;;
    [Qq])
        echo ""
        echo -e "${YELLOW}Setup cancelled${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Setup complete! Happy analyzing! 🎉${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""
