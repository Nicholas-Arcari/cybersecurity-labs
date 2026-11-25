"""Shared fixtures for cybersecurity-labs test suite."""

import os
import sys
import tempfile
import pytest

# Add script directories to path so imports work
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "02-vulnerability-assessment", "code"))
sys.path.insert(0, os.path.join(REPO_ROOT, "03-web-attacks (Red Team + Secure Coding)", "code"))
sys.path.insert(0, os.path.join(REPO_ROOT, "04-system-exploitation", "05-password-cracking", "code"))


@pytest.fixture
def tmp_file():
    """Create a temporary file and clean up after test."""
    files = []

    def _create(content, suffix=""):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
        f.write(content)
        f.close()
        files.append(f.name)
        return f.name

    yield _create

    for path in files:
        if os.path.exists(path):
            os.unlink(path)
