#!/bin/zsh
cd "${0:A:h}"
exec ../engine/.venv/bin/python server.py
