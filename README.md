# modelos_decision
Paquete Python con herramientas de Análisis Multicriterio para usar en Google Colab.

## Instalación
```python
!pip install git+https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion.git -q
```

## Herramientas disponibles

| Herramienta | Descripción |
|---|---|
| `run_estadistica()` | Estadística Descriptiva — Media, CV, correlación, boxplots, histogramas |
| `run_normalizacion()` | Normalización — Fracción del máximo/suma/rango, vector, Z-score, RIM |
| `run_ponderaciones()` | Ponderaciones — Uniforme, Entropía, CRITIC, CV, AHP, Ordenación, Tasación |
| `run_agregacion()` | Agregación — Suma Ponderada · Media Geométrica Ponderada |
| `run_ahp()` | AHP — Proceso Analítico Jerárquico (Thomas Saaty) |
| `run_topsis()` | TOPSIS — Similarity to Ideal Solution |
| `run_rim()` | RIM — Reference Ideal Method |

## Uso en Colab
Cada herramienta se usa en una celda separada:

```python
# Celda 0 — Instalación (ejecutar una sola vez)
!pip install git+https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion.git -q
```

```python
# Celda 1 — Estadística Descriptiva
from Modelos2026_Normalizacion_Ponderacion_Agregacion import run_estadistica
run_estadistica()
```

```python
# Celda 2 — Normalización
from modelos_decision import run_normalizacion
run_normalizacion()
```

```python
# Celda 3 — Ponderaciones
from modelos_decision import run_ponderaciones
run_ponderaciones()
```

```python
# Celda 4 — Agregación (Suma Ponderada / Media Geométrica)
from modelos_decision import run_agregacion
run_agregacion()
```

```python
# Celda 5 — AHP
from modelos_decision import run_ahp
run_ahp()
```

```python
# Celda 6 — TOPSIS
from modelos_decision import run_topsis
run_topsis()
```

```python
# Celda 7 — RIM
from modelos_decision import run_rim
run_rim()
```

## Formato del archivo Excel / CSV
- Primera fila: encabezados (nombre de columnas)
- Primera columna: nombre de las alternativas
- Columnas siguientes: criterios con valores numéricos
- Sin celdas combinadas, sin hojas múltiples
- Para AHP: dos columnas sin encabezado (primera: alternativas, segunda: criterios)

## Recomendaciones previas
- Cargar archivos con datos ya transformados (mínimos convertidos a máximos)
- Valores no negativos para Suma Ponderada y Media Geométrica
- Para seleccionar varios criterios: mantener **Ctrl** y hacer clic
- La normalización RIM usa por defecto el cuartil 75 como C y el máximo como D (editables manualmente)
