#!/bin/bash

###############################################################################
# Phase 12 Playwright Test Suite Runner
# Comprehensive testing for multi-user & multi-child support
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
TEST_SCREENSHOTS_DIR="$SCRIPT_DIR/test-screenshots/phase12"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 12: Playwright Test Suite${NC}"
echo -e "${BLUE}Multi-User & Multi-Child Support Tests${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"

if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi
echo -e "${GREEN}✓ uv installed${NC}"

# Step 2: Install dependencies
echo -e "\n${YELLOW}[2/5] Installing test dependencies...${NC}"
cd "$BACKEND_DIR"

echo "Installing pytest-asyncio..."
uv pip install pytest-asyncio > /dev/null 2>&1 || echo "Already installed"
echo -e "${GREEN}✓ pytest-asyncio installed${NC}"

echo "Installing aiohttp..."
uv pip install aiohttp > /dev/null 2>&1 || echo "Already installed"
echo -e "${GREEN}✓ aiohttp installed${NC}"

echo "Installing playwright..."
uv pip install playwright > /dev/null 2>&1 || echo "Already installed"
echo -e "${GREEN}✓ playwright installed${NC}"

echo "Installing Chromium browser..."
uv run playwright install chromium > /dev/null 2>&1 || echo "Browser already installed"
echo -e "${GREEN}✓ Chromium browser ready${NC}"

# Step 3: Start servers
echo -e "\n${YELLOW}[3/5] Starting test servers...${NC}"

# Kill any existing servers
pkill -f "http.server.*8002" 2>/dev/null || true
pkill -f "uvicorn.*8000" 2>/dev/null || true
sleep 1

# Check if backend is running
if ! lsof -i :8000 > /dev/null 2>&1; then
    echo "Starting backend server on port 8000..."
    cd "$BACKEND_DIR"
    nohup uv run python main.py > /tmp/backend.log 2>&1 &
    sleep 3
    echo -e "${GREEN}✓ Backend running on http://localhost:8000${NC}"
else
    echo -e "${GREEN}✓ Backend already running on http://localhost:8000${NC}"
fi

# Check if frontend is running
if ! lsof -i :8002 > /dev/null 2>&1; then
    echo "Starting frontend server on port 8002..."
    cd "$FRONTEND_DIR"
    nohup python -m http.server 8002 > /tmp/frontend.log 2>&1 &
    sleep 2
    echo -e "${GREEN}✓ Frontend running on http://localhost:8002${NC}"
else
    echo -e "${GREEN}✓ Frontend already running on http://localhost:8002${NC}"
fi

# Step 4: Create screenshots directory
echo -e "\n${YELLOW}[4/5] Preparing test environment...${NC}"
mkdir -p "$TEST_SCREENSHOTS_DIR"
echo -e "${GREEN}✓ Screenshots directory: $TEST_SCREENSHOTS_DIR${NC}"

# Step 5: Run tests
echo -e "\n${YELLOW}[5/5] Running test suite...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes...${NC}\n"

cd "$BACKEND_DIR"

case "${1:-all}" in
    all)
        echo -e "${BLUE}Running all 32 tests...${NC}\n"
        uv run pytest test_phase12_auth.py -v --tb=short
        ;;
    auth)
        echo -e "${BLUE}Running auth tests (Suite 1)...${NC}\n"
        uv run pytest test_phase12_auth.py -k "registration or login" -v
        ;;
    child)
        echo -e "${BLUE}Running child management tests (Suite 2)...${NC}\n"
        uv run pytest test_phase12_auth.py -k "child" -v
        ;;
    isolation)
        echo -e "${BLUE}Running data isolation tests (Suite 3)...${NC}\n"
        uv run pytest test_phase12_auth.py -k "isolation or persistence or token" -v
        ;;
    api)
        echo -e "${BLUE}Running API tests (Suite 9)...${NC}\n"
        uv run pytest test_phase12_auth.py -k "api_" -v
        ;;
    quick)
        echo -e "${BLUE}Running quick smoke tests...${NC}\n"
        uv run pytest test_phase12_auth.py::test_user_registration_success -v
        uv run pytest test_phase12_auth.py::test_user_login_success -v
        uv run pytest test_phase12_auth.py::test_create_child_profile -v
        uv run pytest test_phase12_auth.py::test_complete_signup_to_app_flow -v
        ;;
    summary)
        echo -e "${BLUE}Running test summary...${NC}\n"
        uv run pytest test_phase12_auth.py::test_phase12_summary -v
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Usage: $0 [all|auth|child|isolation|api|quick|summary]"
        echo ""
        echo "Options:"
        echo "  all       - Run all 32 tests (default)"
        echo "  auth      - Run registration & login tests"
        echo "  child     - Run child profile management tests"
        echo "  isolation - Run data isolation & security tests"
        echo "  api       - Run API endpoint tests"
        echo "  quick     - Run 4 quick smoke tests"
        echo "  summary   - Show test summary"
        exit 1
        ;;
esac

TEST_RESULT=$?

# Summary
echo -e "\n${BLUE}========================================${NC}"
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo -e "${YELLOW}Check output above for details${NC}"
fi
echo -e "${BLUE}========================================${NC}"

# Show test artifacts
if [ -d "$TEST_SCREENSHOTS_DIR" ] && [ "$(ls -A $TEST_SCREENSHOTS_DIR)" ]; then
    echo -e "\n${YELLOW}Test artifacts:${NC}"
    echo -e "${BLUE}Screenshots saved to:${NC}"
    echo "  $TEST_SCREENSHOTS_DIR"
    echo "  Total files: $(ls -1 $TEST_SCREENSHOTS_DIR | wc -l)"
fi

echo -e "\n${YELLOW}Logs:${NC}"
echo "  Backend: /tmp/backend.log"
echo "  Frontend: /tmp/frontend.log"

exit $TEST_RESULT
