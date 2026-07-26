"""pytest configuration — add the module root to sys.path."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
