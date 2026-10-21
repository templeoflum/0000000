#!/bin/zsh
set -eu
cd "$(dirname "$0")"
exec engine/.venv/bin/python launch.py
