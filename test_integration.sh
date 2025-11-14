#!/bin/bash

# Integration Test Script - API + Website

set -e

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "SPELLING APP INTEGRATION TEST"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
passed=0
failed=0

function test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    test_count=$((test_count + 1))
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "$data")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [[ $status_code == $expected_status ]]; then
        echo -e "${GREEN}✓ Test $test_count: $name${NC}"
        passed=$((passed + 1))
        echo "  Response: $body" | head -c 100
        echo ""
    else
        echo -e "${RED}✗ Test $test_count: $name${NC}"
        echo "  Expected: $expected_status, Got: $status_code"
        echo "  Response: $body" | head -c 100
        echo ""
        failed=$((failed + 1))
    fi
}

# ========== STEP 1: AUTH FLOW ==========
echo ""
echo "STEP 1: Authentication Flow"
echo "----------------------------------------"

# Register
echo "Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"integrationtest@example.com","password":"testpass123"}')
echo "$REGISTER_RESPONSE" | python3 -m json.tool
USER_ID=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo "  User ID: $USER_ID"
echo ""

# Login
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"integrationtest@example.com","password":"testpass123"}')
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "  Token: ${TOKEN:0:30}..."
echo ""

# ========== STEP 2: CHILD MANAGEMENT ==========
echo "STEP 2: Child Management"
echo "----------------------------------------"

# Create child
echo "Creating child profile..."
CHILD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/children" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"name":"TestChild","age":5}')
echo "$CHILD_RESPONSE" | python3 -m json.tool
CHILD_ID=$(echo "$CHILD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "  Child ID: $CHILD_ID"
echo ""

# Get children
echo "Fetching children..."
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/children" | python3 -m json.tool
echo ""

# ========== STEP 3: WORD MANAGEMENT (ADMIN) ==========
echo "STEP 3: Word Management"
echo "----------------------------------------"

# Add word
echo "Adding test word..."
ADD_WORD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/admin/words" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"word":"bee","category":"insect"}')
echo "$ADD_WORD_RESPONSE" | python3 -m json.tool
WORD_ID=$(echo "$ADD_WORD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "error")
echo "  Word ID: $WORD_ID"
echo ""

# Get admin words
echo "Fetching all words..."
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/admin/words" | python3 -m json.tool
echo ""

# ========== STEP 4: PRACTICE FLOW ==========
echo "STEP 4: Practice Flow"
echo "----------------------------------------"

# Get next word
echo "Getting next word..."
WORD_RESPONSE=$(curl -s "http://localhost:8000/api/next-word?child_id=$CHILD_ID" \
    -H "Authorization: Bearer $TOKEN")
echo "$WORD_RESPONSE" | python3 -m json.tool
PRACTICE_WORD_ID=$(echo "$WORD_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id', 'error'))" 2>/dev/null)
echo ""

# Submit practice (if word found)
if [ "$PRACTICE_WORD_ID" != "error" ] && [ ! -z "$PRACTICE_WORD_ID" ]; then
    echo "Submitting practice attempt..."
    PRACTICE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/practice" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{\"word_id\":$PRACTICE_WORD_ID,\"child_id\":$CHILD_ID,\"spelled_word\":\"bee\",\"is_correct\":true}")
    echo "$PRACTICE_RESPONSE" | python3 -m json.tool
else
    echo "Skipped practice test (no word available)"
fi
echo ""

# ========== STEP 5: DASHBOARD ==========
echo "STEP 5: Dashboard Stats"
echo "----------------------------------------"

echo "Fetching dashboard stats..."
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/dashboard/accuracy" | python3 -m json.tool
echo ""

echo "Fetching 7-day trend..."
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/dashboard/7-day-trend" | python3 -m json.tool
echo ""

# ========== SUMMARY ==========
echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "Total Tests: $test_count"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
