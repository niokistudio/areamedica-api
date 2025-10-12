#!/bin/bash
# Deployment Readiness Check
# Validates that all necessary files and configurations are ready for deployment

set -e

echo "🔍 AreaMédica API - Deployment Readiness Check"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to print check result
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

echo "📋 Checking required files..."
echo ""

# Check Dockerfile
if [ -f "docker/Dockerfile" ]; then
    check_pass "docker/Dockerfile exists"
else
    check_fail "docker/Dockerfile missing"
fi

# Check render.yaml
if [ -f "render.yaml" ]; then
    check_pass "render.yaml exists"
    
    # Validate render.yaml syntax
    if command -v python3 &> /dev/null; then
        if python3 -c "import yaml; yaml.safe_load(open('render.yaml'))" 2>/dev/null; then
            check_pass "render.yaml syntax is valid"
        else
            check_fail "render.yaml has syntax errors"
        fi
    fi
else
    check_warn "render.yaml missing (only needed for Render deployment)"
fi

# Check requirements files
if [ -f "requirements/prod.txt" ]; then
    check_pass "requirements/prod.txt exists"
else
    check_fail "requirements/prod.txt missing"
fi

# Check alembic configuration
if [ -f "alembic.ini" ]; then
    check_pass "alembic.ini exists"
else
    check_fail "alembic.ini missing"
fi

# Check migrations directory
if [ -d "migrations/versions" ] && [ "$(ls -A migrations/versions)" ]; then
    check_pass "Database migrations exist"
else
    check_warn "No database migrations found"
fi

# Check health endpoint
if [ -f "src/interface/api/routes/health.py" ]; then
    check_pass "Health check endpoint exists"
else
    check_fail "Health check endpoint missing"
fi

echo ""
echo "🔐 Checking environment configuration..."
echo ""

# Check .env.example
if [ -f ".env.example" ]; then
    check_pass ".env.example exists"
else
    check_warn ".env.example missing"
fi

# Check .env.production.example
if [ -f ".env.production.example" ]; then
    check_pass ".env.production.example exists"
else
    check_warn ".env.production.example missing"
fi

# Check for sensitive data in .env files
if [ -f ".env" ]; then
    if grep -q "your_secret_key_here" .env 2>/dev/null; then
        check_warn ".env contains placeholder values"
    fi
    
    if git check-ignore .env &>/dev/null; then
        check_pass ".env is in .gitignore"
    else
        check_fail ".env is NOT in .gitignore (security risk!)"
    fi
fi

echo ""
echo "📚 Checking documentation..."
echo ""

# Check documentation files
if [ -f "API_DOCUMENTATION.md" ]; then
    check_pass "API_DOCUMENTATION.md exists"
else
    check_warn "API_DOCUMENTATION.md missing"
fi

if [ -f "RENDER_DEPLOYMENT.md" ]; then
    check_pass "RENDER_DEPLOYMENT.md exists"
else
    check_warn "RENDER_DEPLOYMENT.md missing"
fi

if [ -f "README.md" ]; then
    check_pass "README.md exists"
else
    check_warn "README.md missing"
fi

echo ""
echo "🧪 Checking tests..."
echo ""

# Check test directory
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    check_pass "Tests directory exists"
    
    # Check if tests pass (optional)
    if command -v pytest &> /dev/null; then
        if pytest tests/ -q --tb=no &>/dev/null; then
            check_pass "All tests pass"
        else
            check_warn "Some tests are failing"
        fi
    fi
else
    check_warn "No tests found"
fi

echo ""
echo "🔧 Checking Terraform (optional)..."
echo ""

if [ -d "terraform" ]; then
    check_pass "Terraform directory exists"
    
    if [ -f "terraform/main.tf" ]; then
        check_pass "terraform/main.tf exists"
    fi
    
    if [ -f "terraform/variables.tf" ]; then
        check_pass "terraform/variables.tf exists"
    fi
    
    # Check Terraform syntax if installed
    if command -v terraform &> /dev/null; then
        cd terraform
        if terraform fmt -check &>/dev/null; then
            check_pass "Terraform files are formatted correctly"
        else
            check_warn "Terraform files need formatting (run: terraform fmt)"
        fi
        cd ..
    fi
else
    check_warn "Terraform configuration not found (optional)"
fi

echo ""
echo "🐳 Checking Docker configuration..."
echo ""

# Check docker-compose
if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
    
    if command -v docker-compose &> /dev/null; then
        if docker-compose config &>/dev/null; then
            check_pass "docker-compose.yml syntax is valid"
        else
            check_fail "docker-compose.yml has syntax errors"
        fi
    fi
fi

# Check .dockerignore
if [ -f ".dockerignore" ]; then
    check_pass ".dockerignore exists"
else
    check_warn ".dockerignore missing (recommended for smaller images)"
fi

echo ""
echo "=============================================="
echo "📊 Summary:"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Ready for deployment.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ ${WARNINGS} warning(s) found. Review before deploying.${NC}"
    exit 0
else
    echo -e "${RED}✗ ${ERRORS} error(s) found. Fix before deploying.${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ ${WARNINGS} warning(s) also found.${NC}"
    fi
    exit 1
fi
