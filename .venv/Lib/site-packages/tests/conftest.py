import pytest
import sys
from pathlib import Path

# Add the project root to Python path
root_dir = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(root_dir))
