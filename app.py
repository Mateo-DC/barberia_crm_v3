"""Entrada ASGI de compatibilidad: uvicorn app:app."""
from backend.web import app

__all__ = ["app"]
