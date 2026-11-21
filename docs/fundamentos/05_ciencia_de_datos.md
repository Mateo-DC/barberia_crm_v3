# Ciencia de datos: Pandas y NumPy

[Índice](../README.md) · [Analítica](../../backend/analytics/metrics.py) · [Dashboard](../../app.py)

## Pandas
En `calcular_indicadores_ventas`, `pd.DataFrame.from_records` transforma registros SQLite a una tabla. `pd.to_numeric(..., errors='coerce')` convierte entradas y elimina valores no numéricos con `dropna()`.

## NumPy
`np.asarray(..., dtype=float)`, `np.mean`, `np.median` y `np.percentile(..., 90)` calculan indicadores. El uso de NumPy está justificado para análisis sobre arreglos, **no** para cada registro de una visita.

| Métrica | Cálculo | Uso |
|---|---|---|
| Ticket medio | Media de montos válidos | Dashboard |
| Mediana | Percentil 50 | Resistencia a valores extremos |
| Percentil 90 | `np.percentile` | Entender compras superiores |

## Reproducibilidad y advertencias
La muestra actual del dashboard son las últimas ocho ventas: sirve para un indicador de actividad reciente, **no para inferencia estadística de todo el historial**. Nunca confundir correlación con causalidad. Los datos personales no se envían a servicios externos para el análisis. [Pruebas de métricas](../../tests/test_conceptos.py).
