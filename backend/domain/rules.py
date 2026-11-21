"""Funciones puras de dominio: datos inmutables y composición declarativa."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Callable, TypeVar

T = TypeVar('T')

@dataclass(frozen=True, slots=True)
class MetaVisitas:
    cantidad: int
    modo: str

    def __post_init__(self):
        if self.cantidad <= 0 or self.modo not in ('acumuladas', 'consecutivas'):
            raise ValueError('Regla de asistencia inválida')


def seleccionar(items: Iterable[T], criterio: Callable[[T], bool]) -> list[T]:
    """Función genérica de orden superior: recibe otra función como parámetro."""
    return list(filter(criterio, items))


def cumple_meta(asistencias: int, meta: MetaVisitas) -> bool:
    return asistencias >= meta.cantidad
