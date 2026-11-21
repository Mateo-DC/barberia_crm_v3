"""Restricción por IP de origen de conexión. No sustituye autenticación de administrador.

No se confía en X-Forwarded-For: Uvicorn desactiva proxy_headers.
"""
from __future__ import annotations
import ipaddress
import socket
from functools import lru_cache
from fastapi import Request

@lru_cache(maxsize=1)
def host_addresses() -> frozenset[str]:
    addresses = {'127.0.0.1', '::1'}
    try:
        for entry in socket.getaddrinfo(socket.gethostname(), None):
            if entry[0] in (socket.AF_INET, socket.AF_INET6):
                addresses.add(entry[4][0].split('%')[0])
    except OSError:
        pass
    return frozenset(addresses)


def is_host_request(request: Request) -> bool:
    if request.client is None:
        return False
    try:
        peer = ipaddress.ip_address(request.client.host.split('%')[0])
    except ValueError:
        return False
    return peer.is_loopback or str(peer) in host_addresses()


def public_registration_path(path: str) -> bool:
    """Only registration + static assets are reachable from other machines."""
    return path == '/registro' or path.startswith('/static/')
