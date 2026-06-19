#!/bin/bash

# 📄 Deployment pre-flight checklist

echo "📋 StoicMatrix Deployment Checklist"
echo "==================================="
echo ""

check_item() {
    local item="$1"
    local status="$2"
    if [ "$status" = "true" ]; then
        echo -e "\033[0;32m✓\033[0m $item"
    else
        echo -e "\033[0;31m❌\033[0m $item"
    fi
}

echo "Prerequisites:"
check_item "Git installed" $(command -v git &> /dev/null && echo true || echo false)
check_item "Python 3 installed" $(command -v python3 &> /dev/null && echo true || echo false)
check_item "Docker installed" $(command -v docker &> /dev/null && echo true || echo false)
check_item "Token manager exists" $([[ -f scripts/hf_token_manager.py ]] && echo true || echo false)

echo ""
echo "Repository Files:"
check_item "Dockerfile exists" $([[ -f Dockerfile ]] && echo true || echo false)
check_item "docker-compose.yml exists" $([[ -f docker-compose.yml ]] && echo true || echo false)
check_item "README.md exists" $([[ -f README.md ]] && echo true || echo false)
check_item "backend/ directory exists" $([[ -d backend ]] && echo true || echo false)
check_item "frontend/ directory exists" $([[ -d frontend ]] && echo true || echo false)

echo ""
echo "Optimization Files:"
check_item "config.py exists" $([[ -f backend/config.py ]] && echo true || echo false)
check_item "cache.py exists" $([[ -f backend/cache.py ]] && echo true || echo false)
check_item "monitoring.py exists" $([[ -f backend/monitoring.py ]] && echo true || echo false)
check_item "optimization_guide.md exists" $([[ -f performance/optimization_guide.md ]] && echo true || echo false)
check_item "benchmark_suite.py exists" $([[ -f performance/benchmark_suite.py ]] && echo true || echo false)

echo ""
echo "Monitoring & Deployment:"
check_item "prometheus.yml exists" $([[ -f monitoring/prometheus.yml ]] && echo true || echo false)
check_item "alert_rules.yml exists" $([[ -f monitoring/alert_rules.yml ]] && echo true || echo false)
check_item "deploy_hf_complete.sh exists" $([[ -f scripts/deploy_hf_complete.sh ]] && echo true || echo false)

echo ""
echo "📄 Deployment Checklist"
echo ""
echo "Before deploying, ensure:"
echo "  [ ] HF token is saved in token manager"
echo "  [ ] All services are configured (PostgreSQL, Redis, etc.)"
echo "  [ ] Environment variables are set"
echo "  [ ] Git is configured with credentials"
echo "  [ ] Monitoring is enabled"
echo "  [ ] Backup is created (optional)"
echo ""
echo "Ready to deploy? Run:"
echo "  bash scripts/deploy_hf_complete.sh -u <username> -r <repo> -t production --optimize --backup"
echo ""
