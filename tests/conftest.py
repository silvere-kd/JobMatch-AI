# tests/conftest.py
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Set DATA_DIR & ENV *before* importing any backend code
TEST_DATA_DIR = tempfile.mkdtemp(prefix="jobmatch_test_data_")
os.environ["DATA_DIR"] = TEST_DATA_DIR
os.environ["ENV"] = "test"

# Add repo root to PYTHONPATH for tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# Force AnyIO to use asyncio to avoid trio dependency
@pytest.fixture
def anyio_backend():
    return "asyncio"
