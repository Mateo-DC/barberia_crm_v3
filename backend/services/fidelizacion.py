"""Pure business rules for attendance-based promotion eligibility."""
from __future__ import annotations
from datetime import date
from typing import Iterable, Mapping, Sequence


def cliente_cumple_objetivo(cliente: Mapping, tipo_objetivo: str, objetivo: str, grupos_cliente: set[str]) -> bool:
    if tipo_objetivo == 'todos':
        return True
    if tipo_objetivo == 'categoria':
        return cliente['tipo_cliente'] == objetivo
    return objetivo in grupos_cliente


def contar_visitas(asistencias: Sequence[Mapping], modo: str) -> int:
    """Consecutive visits means consecutive attendance records, not calendar days."""
    if modo == 'acumuladas':
        return len(asistencias)
    if modo == 'consecutivas':
        # A missed visit can be recorded as rompe_racha=1. Count only visits after
        # the most recent break; accumulated mode ignores breaks.
        last_break = max((i for i, row in enumerate(asistencias) if row.get('rompe_racha', 0)), default=-1)
        return len(asistencias) - last_break
    raise ValueError('Modo de conteo no válido.')


def calcular_ronda(visitas: int, meta: int, repeticion: str) -> int:
    if visitas < meta:
        return 0
    return 1 if repeticion == 'una_vez' else visitas // meta


def personalizar_mensaje(plantilla: str, cliente: Mapping, promocion: Mapping, ronda: int) -> str:
    values = {
        'nombre': cliente['nombre'],
        'promocion': promocion['nombre'],
        'premio': promocion['premio'] or promocion['descripcion'],
        'visitas': promocion['meta_visitas'],
        'ronda': ronda,
    }
    try:
        return plantilla.format(**values)
    except (KeyError, ValueError):
        return plantilla.replace('{nombre}', cliente['nombre'])
