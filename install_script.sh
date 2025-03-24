#!/bin/bash

# Colors for better visibility
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting llama-cpp-python CPU installation fix...${NC}"

# Install required build tools with specific gcc versions
echo -e "${GREEN}Installing build essentials and CMake...${NC}"
apt-get update
apt-get install -y \
    build-essential \
    cmake \
    gcc-11 \
    g++-11 \
    python3-dev \
    python3-pip \
    ninja-build

# Set gcc-11 as the default compiler
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100
update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100

# Verify compiler installation explicitly
echo -e "${GREEN}Verifying compiler installation...${NC}"
GCC_PATH=$(which gcc-11)
GPP_PATH=$(which g++-11)

if [[ -z "$GCC_PATH" ]] || [[ -z "$GPP_PATH" ]]; then
    echo -e "${RED}Error: GCC-11 or G++-11 not found. Installation failed.${NC}"
    exit 1
else
    echo -e "${GREEN}gcc-11 found at: $GCC_PATH${NC}"
    echo -e "${GREEN}g++-11 found at: $GPP_PATH${NC}"
fi

# Export compiler paths explicitly
export CC="$GCC_PATH"
export CXX="$GPP_PATH"
export CMAKE_C_COMPILER="$GCC_PATH"
export CMAKE_CXX_COMPILER="$GPP_PATH"

# Print compiler versions
echo -e "${GREEN}Compiler versions:${NC}"
$CC --version
$CXX --version

# Upgrade Python package management tools
python3 -m pip install --upgrade pip setuptools wheel cmake scikit-build-core

# Clear any previous failed installations
python3 -m pip uninstall -y llama-cpp-python

# Attempt installation with pre-built wheel first
echo -e "${GREEN}Attempting to install pre-built llama-cpp-python wheel...${NC}"
if python3 -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu; then
    echo -e "${GREEN}Successfully installed llama-cpp-python using pre-built wheel!${NC}"
else
    echo -e "${RED}Pre-built wheel installation failed, attempting to build from source...${NC}"
    # Install from source with verbose debugging and explicit compiler settings
    if CMAKE_ARGS="-DCMAKE_C_COMPILER=$CC -DCMAKE_CXX_COMPILER=$CXX" \
       python3 -m pip install --verbose --force-reinstall --no-cache-dir llama-cpp-python; then
        echo -e "${GREEN}Successfully installed llama-cpp-python from source!${NC}"
    else
        echo -e "${RED}Installation from source failed. Please check the logs above carefully.${NC}"
        exit 1
    fi
fi

# Verify installation explicitly
echo -e "${GREEN}Verifying llama-cpp-python installation...${NC}"
if python3 -c "import llama_cpp; print(f'llama-cpp-python version: {llama_cpp.__version__}')"; then
    echo -e "${GREEN}Installation verified successfully!${NC}"
else
    echo -e "${RED}Verification failed. llama-cpp-python is not properly installed.${NC}"
    exit 1
fi
