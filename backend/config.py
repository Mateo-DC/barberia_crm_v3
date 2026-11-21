"""Rutas de recursos empaquetados y datos persistentes (escritura fuera del .exe)."""
from pathlib import Path
import shutil
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
# Cuando se ejecuta .exe, la base e imágenes van en LocalAppData, no en Program Files.
if getattr(sys, 'frozen', False) or '__compiled__' in globals():
    DEFAULT_DATA_DIR = Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'BarberiaCRM'
else:
    DEFAULT_DATA_DIR = BASE_DIR / 'data'
DATA_DIR = Path(os.getenv('CRM_DATA_DIR', str(DEFAULT_DATA_DIR))).expanduser().resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / 'barberia.db'
# Migración conservadora: solo copia desde el esquema de carpetas anterior si
# el destino todavía no existe. Nunca sobrescribe datos del usuario.
LEGACY_DB_PATH = BASE_DIR / 'barberia.db'
if not DB_PATH.exists() and LEGACY_DB_PATH.is_file() and LEGACY_DB_PATH != DB_PATH:
    shutil.copy2(LEGACY_DB_PATH, DB_PATH)
APP_TITLE = 'Barbería CRM & Fidelización'
CLIENT_TYPES = ['Nuevo', 'Frecuente', 'Esporádico', 'Inactivo', 'VIP', 'Premium']
CAMPAIGNS = ['Sin campaña','Promo WhatsApp 15%', 'Reactivación de inactivos', 'Publicidad general', 'Programa de fidelización']
