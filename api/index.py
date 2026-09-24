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
    # Fallback en caso de rutas relativas de Vercel
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from server import IDCBypassHandler

class handler(IDCBypassHandler):
    """Manejador Serverless nativo para Vercel Functions."""
    pass
