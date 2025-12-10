#!/bin/bash
# Run CQE test suite

echo "=== Running CQE Tests ==="

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    source venv/bin/activate
fi

# Run different test suites
echo ""
echo "1. Unit Tests"
pytest tests/unit -v

echo ""
echo "2. Integration Tests"
pytest tests/integration -v

echo ""
echo "3. Performance Tests"
pytest tests/performance -v

echo ""
echo "4. Full Coverage Report"
pytest --cov=cqe --cov-report=html --cov-report=term-missing

echo ""
echo "✓ All tests complete!"
echo "Coverage report: htmlcov/index.html"
