"""Ciencia de datos sobre resultados agregados: evita pandas en operaciones CRUD."""
from __future__ import annotations
from collections.abc import Iterable, Mapping
from backend.domain.rules import seleccionar


def calcular_indicadores_ventas(registros: Iterable[Mapping]) -> dict[str, float]:
    """Usa Pandas y NumPy solo cuando se solicitan los indicadores estadísticos."""
    import pandas as pd
    import numpy as np

    filas = [dict(item) for item in registros]
    df = pd.DataFrame.from_records(filas)
    if df.empty or 'monto' not in df:
        return {'ticket_medio': 0.0, 'mediana': 0.0, 'percentil_90': 0.0}
    montos = pd.to_numeric(df['monto'], errors='coerce').dropna().to_numpy(dtype=float)
    montos = seleccionar(montos, lambda monto: monto > 0)  # lambda + filtro genérico
    if not montos:
        return {'ticket_medio': 0.0, 'mediana': 0.0, 'percentil_90': 0.0}
    valores = np.asarray(montos, dtype=float)
    return {'ticket_medio': float(np.mean(valores)),
            'mediana': float(np.median(valores)),
            'percentil_90': float(np.percentile(valores, 90))}
