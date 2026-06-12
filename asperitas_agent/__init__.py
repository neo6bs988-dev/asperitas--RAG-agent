from pathlib import Path

_src_pkg = Path(__file__).resolve().parents[1] / "src" / "asperitas_agent"
__path__ = [str(_src_pkg)]

version_file = _src_pkg / "__init__.py"
__version__ = "0.1.0"
