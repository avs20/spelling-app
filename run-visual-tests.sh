#!/bin/bash

# Visual Regression Testing Runner
# Captures screenshots of all app screens and states

echo "=========================================="
echo "Visual Regression Testing"
echo "=========================================="
echo ""

# Check if servers are running
echo "Checking if servers are running..."

# Check backend
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "❌ Backend not running on http://localhost:8000"
    echo "   Start it with: cd backend && ~/.local/bin/uv run python main.py"
    exit 1
fi

# Check frontend
if ! curl -s http://localhost:8002/ > /dev/null 2>&1; then
    echo "❌ Frontend not running on http://localhost:8002"
    echo "   Start it with: cd frontend && ~/.local/bin/uv run python -m http.server 8002"
    exit 1
fi

echo "✓ Backend running"
echo "✓ Frontend running"
echo ""

# Run visual tests
cd backend
~/.local/bin/uv run python visual_tests.py

echo ""
echo "=========================================="
echo "View results at: test-screenshots/*_index.html"
echo "=========================================="
