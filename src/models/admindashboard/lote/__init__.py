"""Package shim for models.admindashboard.lote package.

This file exposes `LotePage` by dynamically loading the sibling
module file `models/admindashboard/lote.py` (the SPA entry). This
resolves the name collision between the package `lote/` and the
module `lote.py` so callers can continue using
`from models.admindashboard.lote import LotePage`.
"""

from pathlib import Path
import importlib.util
import sys

__all__ = []

_module_path = Path(__file__).resolve().parents[1] / "lote.py"
if _module_path.exists():
	try:
		spec = importlib.util.spec_from_file_location("models.admindashboard._lote_module", str(_module_path))
		if spec and spec.loader:
			module = importlib.util.module_from_spec(spec)
			sys.modules[spec.name] = module
			spec.loader.exec_module(module)
			if hasattr(module, "LotePage"):
				LotePage = getattr(module, "LotePage")
				__all__.append("LotePage")
	except Exception:
		# If loading fails, leave package empty so imports fail loudly later.
		pass
