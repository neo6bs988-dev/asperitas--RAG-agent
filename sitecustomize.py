"""Make the src layout runnable with `python -m asperitas_agent.cli`.

This keeps MVP-001 usable from a plain repository checkout before editable
installation.
"""

from pathlib import Path
import sys

src = Path(__file__).resolve().parent / "src"
if src.exists() and str(src) not in sys.path:
    sys.path.insert(0, str(src))
