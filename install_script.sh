#!/bin/bash

# Colors for better visibility
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting llama-cpp-python CPU installation fix..."

# Install required build tools
echo "Installing build essentials and CMake..."
sudo apt-get update
sudo apt-get install -y build-essential cmake python3-dev

# Verify compiler installation
echo "Verifying compiler installation..."
if ! command -v gcc >/dev/null 2>&1 || ! command -v g++ >/dev/null 2>&1; then
    echo -e "${RED}Error: GCC or G++ not found. Installation failed.${NC}"
    exit 1
fi

# Set compiler environment variables
export CC=gcc
export CXX=g++

# Install llama-cpp-python with CPU support
echo "Installing llama-cpp-python with CPU support..."
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools wheel

# Try the pre-built wheel first (faster and usually works)
echo "Attempting to install pre-built wheel..."
if python3 -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu; then
    echo -e "${GREEN}Successfully installed llama-cpp-python using pre-built wheel!${NC}"
else
    echo "Pre-built wheel installation failed, attempting to build from source..."
    # If pre-built wheel fails, try building from source
    if python3 -m pip install --verbose --force-reinstall --no-cache-dir llama-cpp-python; then
        echo -e "${GREEN}Successfully installed llama-cpp-python from source!${NC}"
    else
        echo -e "${RED}Installation failed. Please check the error messages above.${NC}"
        exit 1
    fi
fi

# Verify installation
echo "Verifying installation..."
if python3 -c "import llama_cpp" 2>/dev/null; then
    echo -e "${GREEN}Installation verified successfully!${NC}"
else
    echo -e "${RED}Verification failed. The package is not properly installed.${NC}"
    exit 1
fi
