"""Ejecutable host. Variables CRM_PORT y CRM_NO_BROWSER habilitan benchmark reproducible."""
from __future__ import annotations
import os
import socket
import threading
import webbrowser
import uvicorn
from app import app

HOST = '0.0.0.0'
PORT = int(os.getenv('CRM_PORT', '8000'))

def get_lan_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(('192.0.2.1', 80))
            return sock.getsockname()[0]
        except OSError:
            return '127.0.0.1'

if __name__ == '__main__':
    print('Barbería CRM iniciado', flush=True)
    print(f'Administración: http://127.0.0.1:{PORT}', flush=True)
    print(f'Registro LAN: http://{get_lan_ip()}:{PORT}/registro', flush=True)
    if os.getenv('CRM_NO_BROWSER') != '1':
        threading.Timer(1.5, lambda: webbrowser.open(f'http://127.0.0.1:{PORT}')).start()
    uvicorn.run(app, host=HOST, port=PORT, access_log=False, proxy_headers=False, workers=1)
