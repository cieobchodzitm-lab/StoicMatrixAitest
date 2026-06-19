#!/bin/bash

# HuggingFace Token Secure Setup Script
# This script securely configures HF tokens for deployment

set -euo pipefail

echo "🔐 HuggingFace Token Setup"
echo "========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q cryptography 2>/dev/null || {
    echo -e "${RED}❌ Failed to install cryptography${NC}"
    exit 1
}
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Make token manager executable
echo ""
echo "🔧 Setting up token manager..."
chmod +x scripts/hf_token_manager.py
echo -e "${GREEN}✓ Token manager ready${NC}"

# Prompt for token
echo ""
echo "🔑 Enter your HuggingFace token (starts with 'hf_'):"
read -r -s HF_TOKEN
echo ""

# Validate token format
if [[ ! $HF_TOKEN =~ ^hf_ ]]; then
    echo -e "${RED}❌ Invalid token format (must start with 'hf_')${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Token format valid${NC}"

# Ask for token name
echo ""
echo "📝 Enter a name for this token (e.g., 'production', 'staging'):"
read -r TOKEN_NAME

if [ -z "$TOKEN_NAME" ]; then
    TOKEN_NAME="default"
fi

# Add token
echo ""
echo "🔐 Encrypting and storing token..."
python3 scripts/hf_token_manager.py add "$TOKEN_NAME" "$HF_TOKEN" "HF token for $TOKEN_NAME environment"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Token stored securely${NC}"
else
    echo -e "${RED}❌ Failed to store token${NC}"
    exit 1
fi

# List tokens
echo ""
echo "📋 Stored tokens:"
python3 scripts/hf_token_manager.py list

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Export token: python3 scripts/hf_token_manager.py export $TOKEN_NAME"
echo "  2. Deploy: ./deploy_to_hf.sh cieobchodzitm l7-cnota-dashboard"
echo ""
echo "For more info: python3 scripts/hf_token_manager.py --help"
