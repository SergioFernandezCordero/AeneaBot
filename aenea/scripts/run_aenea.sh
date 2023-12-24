#!/usr/bin/env bash
echo "## Running AeneaBot"
echo "# Activating Virtualenv"
. /opt/aenea/venv/bin/activate && \

echo "# Run AeneaBot"
python3 /opt/aenea/aenea.py
