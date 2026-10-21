"""Run existing bounded regressions with real network connections prohibited."""
import os
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / 'engine'
sys.path.insert(0, str(ENGINE))
sys.dont_write_bytecode = True
MODULES = '''test_effect_direction test_strobe_hold test_effect_readback
 test_effect_claim test_effect_ownership test_effect_open test_targets
 test_feedback test_figure_guard test_figure_geometry test_dependencies
 test_patches test_surface_targets test_play_all'''.split()

def denied(*args, **kwargs):
    raise AssertionError('Offline audit prohibits real network access')

if __name__ == '__main__':
    with patch.object(socket.socket, 'connect', denied), patch.object(socket, 'create_connection', denied):
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(MODULES))
    raise SystemExit(not result.wasSuccessful())
