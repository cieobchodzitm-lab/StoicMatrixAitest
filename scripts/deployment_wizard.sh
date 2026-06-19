#!/bin/bash

# 👋 Interactive Deployment Wizard

set -euo pipefail

echo "🚀 StoicMatrix HuggingFace Deployment Wizard"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "This wizard will guide you through the deployment process."
echo ""

# Step 1: Token Setup
echo -e "${BLUE}Step 1: HuggingFace Token Setup${NC}"
echo "Do you have a HuggingFace token? (y/n)"
read -r has_token

if [[ $has_token =~ ^[Yy]$ ]]; then
    echo "Enter your HuggingFace token (starts with 'hf_'):"
    read -rs hf_token
    echo ""
    
    echo "Enter a name for this token (e.g., 'production'):"
    read -r token_name
    
    echo "Adding token..."
    python3 scripts/hf_token_manager.py add "$token_name" "$hf_token" "HF deployment token" || {
        echo "Error adding token"
        exit 1
    }
    echo -e "${GREEN}✓ Token added successfully${NC}"
else
    echo "Please create a token at: https://huggingface.co/settings/tokens"
    echo "Then run this wizard again."
    exit 1
fi

echo ""

# Step 2: HuggingFace Configuration
echo -e "${BLUE}Step 2: HuggingFace Space Configuration${NC}"
echo "Enter your HuggingFace username:"
read -r hf_username

echo "Enter the repository name on HuggingFace:"
read -r hf_repo

echo ""

# Step 3: Deployment Options
echo -e "${BLUE}Step 3: Deployment Options${NC}"
echo "Apply performance optimizations? (y/n)"
read -r apply_optimize

echo "Create backup before deployment? (y/n)"
read -r create_backup

echo "Enable monitoring? (y/n)"
read -r enable_monitor

echo "Dry-run mode? (y/n)"
read -r dry_run_mode

echo ""

# Step 4: Review and Confirm
echo -e "${BLUE}Step 4: Review Configuration${NC}"
echo ""
echo "Configuration Summary:"
echo "  HuggingFace Username: $hf_username"
echo "  Repository Name: $hf_repo"
echo "  Token Name: $token_name"
echo "  Optimize: $apply_optimize"
echo "  Backup: $create_backup"
echo "  Monitor: $enable_monitor"
echo "  Dry-run: $dry_run_mode"
echo ""
echo "Continue with deployment? (y/n)"
read -r confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""

# Build command
CMD="bash scripts/deploy_hf_complete.sh -u $hf_username -r $hf_repo -t $token_name"

if [[ $apply_optimize =~ ^[Yy]$ ]]; then
    CMD="$CMD --optimize"
fi

if [[ $create_backup =~ ^[Yy]$ ]]; then
    CMD="$CMD --backup"
fi

if [[ $enable_monitor =~ ^[Yy]$ ]]; then
    CMD="$CMD --monitor"
fi

if [[ $dry_run_mode =~ ^[Yy]$ ]]; then
    CMD="$CMD --dry-run"
fi

echo -e "${GREEN}Starting deployment...${NC}"
echo ""

# Execute deployment
eval "$CMD"
