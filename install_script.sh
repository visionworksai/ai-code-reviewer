#!/bin/bash

# Terminal colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting llama-cpp-python installation script...${NC}"

# Step 1: Install required build tools and dependencies
echo -e "${GREEN}Step 1: Installing required build tools and dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y build-essential cmake python3-dev

# Step 2: Verify compiler installation
echo -e "${GREEN}Step 2: Verifying compiler installation...${NC}"
if command -v gcc >/dev/null 2>&1 && command -v g++ >/dev/null 2>&1; then
    echo -e "${GREEN}✓ GCC and G++ are installed:${NC}"
    gcc --version | head -n 1
    g++ --version | head -n 1
else
    echo -e "${RED}✗ Compilers are not properly installed. Please check your system.${NC}"
    exit 1
fi

# Step 3: Create a Python virtual environment (optional but recommended)
echo -e "${GREEN}Step 3: Creating Python virtual environment (optional)...${NC}"
echo -e "${YELLOW}Do you want to create a virtual environment? (y/n)${NC}"
read create_venv

if [[ "$create_venv" == "y" || "$create_venv" == "Y" ]]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m pip install --upgrade pip
    python3 -m pip install virtualenv
    python3 -m virtualenv llama_env
    source llama_env/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}Skipping virtual environment creation${NC}"
fi

# Step 4: Set compiler environment variables explicitly
echo -e "${GREEN}Step 4: Setting compiler environment variables...${NC}"
export CC=gcc
export CXX=g++

# Step 5: Install llama-cpp-python
echo -e "${GREEN}Step 5: Installing llama-cpp-python...${NC}"
echo -e "${YELLOW}Select installation method:${NC}"
echo "1. Build from source (may be slow but customizable)"
echo "2. Use pre-built wheel (faster, no optimizations)"
read install_method

if [[ "$install_method" == "1" ]]; then
    echo -e "${GREEN}Building from source...${NC}"
    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade setuptools wheel
    python3 -m pip install llama-cpp-python --verbose
elif [[ "$install_method" == "2" ]]; then
    echo -e "${GREEN}Installing pre-built wheel...${NC}"
    python3 -m pip install --upgrade pip
    python3 -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
else
    echo -e "${RED}Invalid selection. Exiting.${NC}"
    exit 1
fi

# Step 6: Verify installation
echo -e "${GREEN}Step 6: Verifying installation...${NC}"
if python3 -c "import llama_cpp; print(f'llama-cpp-python {llama_cpp.__version__} installed successfully!')" 2>/dev/null; then
    echo -e "${GREEN}✓ Installation successful!${NC}"
else
    echo -e "${RED}✗ Installation verification failed. Please check for errors above.${NC}"
    exit 1
fi

echo -e "${GREEN}Installation process completed.${NC}"
