# tests/conftest.py
import sys
from pathlib import Path

import pytest

# Add repo root to PYTHONPATH for tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# Force AnyIO to use asyncio to avoid trio dependency
@pytest.fixture
def anyio_backend():
    return "asyncio"
