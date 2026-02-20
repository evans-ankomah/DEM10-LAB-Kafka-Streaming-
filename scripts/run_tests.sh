#!/bin/bash
"""Helper script to run all tests."""

set -e

echo "Running all tests..."
python -m pytest tests/ -v --tb=short --color=yes

echo ""
echo "✓ All tests passed!"
