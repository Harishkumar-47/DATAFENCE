import os
import sys
import tempfile
from pathlib import Path


TEST_DIR = tempfile.mkdtemp(prefix="datafence-tests-")
os.environ["DATAFENCE_DB_PATH"] = str(Path(TEST_DIR) / "test.db")
os.environ["ENABLE_ACCOUNT_DISCOVERY"] = "false"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
