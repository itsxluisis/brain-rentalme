import sys
from pathlib import Path

# Ensure `backend/` (the parent of this tests/ dir, where the `app` package
# lives) is importable regardless of the directory pytest is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
