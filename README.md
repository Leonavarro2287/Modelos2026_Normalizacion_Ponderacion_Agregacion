# mpa_modelos

Paquete Python con herramientas de Normalización, Ponderación y Agregación Multicriterio para usar en Google Colab.

## Instalación

```
!pip install git+https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion.git -q
```

## Herramientas disponibles

| Herramienta            | Descripción                                                                 |
| ----------------------- | ---------------------------------------------------------------------------- |
| `run_estadistica()`    | Estadística Descriptiva (medidas, matriz de correlación, boxplots, histogramas) |
| `run_normalizacion()`  | Normalización de matrices (fracción del máximo, suma, rango, vector, Z-score, RIM) |
| `run_ponderaciones()`  | Calculadora de Ponderaciones (Uniforme, Desv. estándar, CV, Entropía, CRITIC, Ordenación simple, Tasación simple, AHP) |
| `run_agregacion()`     | Agregación Multicriterio: Suma Ponderada y Media Geométrica Ponderada       |
| `run_ahp()`             | Proceso Analítico Jerárquico (AHP) completo con árbol jerárquico            |
| `run_topsis()`          | TOPSIS – Technique for Order Preference by Similarity to Ideal Solution      |
| `run_rim()`             | RIM – Reference Ideal Method                                                 |

## Uso en Colab

Cada herramienta se usa en una celda separada:

```
# Celda 1 — Estadística Descriptiva
from mpa_modelos import run_estadistica
run_estadistica()
```

```
# Celda 2 — Normalización
from mpa_modelos import run_normalizacion
run_normalizacion()
```

```
# Celda 3 — Calculadora de Ponderaciones
from mpa_modelos import run_ponderaciones
run_ponderaciones()
```

```
# Celda 4 — Agregación Multicriterio (Suma Ponderada / Media Geométrica Ponderada)
from mpa_modelos import run_agregacion
run_agregacion()
```

```
# Celda 5 — AHP
from mpa_modelos import run_ahp
run_ahp()
```

```
# Celda 6 — TOPSIS
from mpa_modelos import run_topsis
run_topsis()
```

```
# Celda 7 — RIM
from mpa_modelos import run_rim
run_rim()
```

## Formato del archivo de entrada

- Alternativas y criterios en columnas, con encabezados en la primera fila (.xlsx, .xls o .csv).
- Para AHP: archivo de dos columnas sin encabezado (primera columna = alternativas, segunda columna = criterios).
