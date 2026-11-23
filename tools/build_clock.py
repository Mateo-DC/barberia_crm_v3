"""Guarda duración real del comando Nuitka, incluso entre pasos de .bat."""
from __future__ import annotations
from pathlib import Path
import sys
import time

folder = Path(__file__).resolve().parent.parent / 'reports'
folder.mkdir(parents=True, exist_ok=True)
mark = folder / '.build_start.txt'
if sys.argv[1:] == ['start']:
    mark.write_text(str(time.time()), encoding='ascii')
elif sys.argv[1:] == ['stop']:
    if mark.exists():
        (folder/'build_duration_seconds.txt').write_text(str(round(time.time()-float(mark.read_text()), 2)), encoding='ascii')
        mark.unlink()
else:
    raise SystemExit('Uso: build_clock.py start|stop')
