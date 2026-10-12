"""
Pramaan Root Entrypoint for Cloud Deployments (Render / Docker)
Automatically forwards to backend.main:app
"""
import os
import sys

_backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from backend.main import app  # noqa: F401
