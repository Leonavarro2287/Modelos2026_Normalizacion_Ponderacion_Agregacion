# 📊 Modelos 2026 – Normalización, Ponderación y Agregación Multicriterio

Paquete Python con herramientas para análisis de decisiones multicriterio en Google Colab.

## Instalación

```python
!pip install git+https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion.git -q
```

## Herramientas Disponibles

| Herramienta | Descripción |
|---|---|
| `run_estadistica()` | Estadística Descriptiva — 16 medidas + correlaciones |
| `run_normalizacion()` | Normalización — 6 métodos |
| `run_ponderacion()` | Ponderación — 8 métodos (incluye AHP) |
| `run_agregacion()` | Agregación — Suma Ponderada, Media Geométrica |
| `run_topsis()` | TOPSIS — 4 funciones de distancia |
| `run_rim()` | RIM — Rango ideal flexible |

## Uso en Colab

Cada herramienta se usa en una celda separada:

```python
# Celda 1 — Estadística Descriptiva
from modelos2026 import run_estadistica
run_estadistica()
```

```python
# Celda 2 — Normalización
from modelos2026 import run_normalizacion
run_normalizacion()
```

```python
# Celda 3 — Ponderación
from modelos2026 import run_ponderacion
run_ponderacion()
```

```python
# Celda 4 — Agregación
from modelos2026 import run_agregacion
run_agregacion()
```

```python
# Celda 5 — TOPSIS
from modelos2026 import run_topsis
run_topsis()
```

```python
# Celda 6 — RIM
from modelos2026 import run_rim
run_rim()
```

## Formato del archivo Excel

- Alternativas en **filas** (primera columna = nombre de alternativa)
- Criterios en **columnas** (primera fila = nombre de criterio)
- Sin celdas combinadas, sin hojas múltiples

| Alternativa | Criterio_1 | Criterio_2 | Criterio_3 |
|---|---|---|---|
| A1 | 45.2 | 120 | 0.85 |
| A2 | 62.1 | 95 | 0.92 |
| A3 | 38.5 | 180 | 0.78 |

## Dependencias

- pandas>=1.3.0
- numpy>=1.21.0
- scipy>=1.7.0
- matplotlib>=3.4.0
- ipywidgets>=7.6.0
- openpyxl>=3.0.0
- jupyter>=1.0.0

## Licencia

MIT License — Uso libre académico y comercial

---

**Autor:** Leonardo Navarro  
**Versión:** 1.0.0
