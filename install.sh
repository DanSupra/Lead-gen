#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Facebook Page Scraper - Installation Guide${NC}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
    echo -e "${RED}⚠️  Please update .env with your Facebook credentials${NC}\n"
else
    echo -e "${GREEN}✓ .env file already exists${NC}\n"
fi

# Check for Node.js
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
    
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Node.js dependencies installed${NC}\n"
    else
        echo -e "${RED}✗ Failed to install Node.js dependencies${NC}\n"
    fi
else
    echo -e "${YELLOW}ℹ Node.js not found (optional)${NC}\n"
fi

# Check for Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"
    
    # Check if venv exists
    if [ ! -d venv ]; then
        echo -e "${YELLOW}Creating Python virtual environment...${NC}"
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    fi
    
    # Activate venv and install dependencies
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python dependencies installed${NC}\n"
    else
        echo -e "${RED}✗ Failed to install Python dependencies${NC}\n"
    fi
else
    echo -e "${YELLOW}ℹ Python not found (optional)${NC}\n"
fi

# Create output directory
mkdir -p output
echo -e "${GREEN}✓ Output directory ready${NC}\n"

echo -e "${GREEN}Installation complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Edit .env and add your Facebook credentials"
echo "2. Run: node scraper.js (Node.js) or python scraper.py (Python)"
echo "3. Check output/ directory for results\n"
echo "For more details, see SETUP.md"
