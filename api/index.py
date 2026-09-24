import os
import sys
from pathlib import Path

# Agregar la raíz del repositorio a sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Importar el manejador de peticiones del servidor IDC
try:
    from server import IDCBypassHandler
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from server import IDCBypassHandler


class handler(IDCBypassHandler):
    """Manejador Serverless nativo para Vercel Functions."""

    def _normalize_path(self):
        """Asegura que el enrutamiento interno de Vercel preserve la ruta original /api/..."""
        if self.path.startswith("/api/index"):
            real_path = (
                self.headers.get("x-matched-path")
                or self.headers.get("x-forwarded-uri")
                or self.headers.get("x-original-uri")
            )
            if real_path and not real_path.startswith("/api/index"):
                self.path = real_path

    def do_GET(self):
        self._normalize_path()
        super().do_GET()

    def do_POST(self):
        self._normalize_path()
        super().do_POST()

    def do_OPTIONS(self):
        self._normalize_path()
        super().do_OPTIONS()
