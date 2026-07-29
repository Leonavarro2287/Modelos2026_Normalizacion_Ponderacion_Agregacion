# decision_models

Paquete Python con herramientas completas para Estadística Descriptiva, Normalización, Ponderación, Agregación y Métodos Multicriterio (AHP, TOPSIS y RIM) para usar directamente en Google Colab.

---

## 🚀 Instalación

Ejecutá esta celda en Google Colab para instalar la última versión directamente desde el repositorio:

```python
!pip install git+[https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion.git](https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion.git) -q
```

---

## 🛠️ Herramientas disponibles

| Herramienta | Función | Descripción |
|---|---|---|
| **📐 Estadística Descriptiva** | `run_estadistica()` | Calcula métricas descriptivas, matriz de correlación de Pearson, boxplots e histogramas. |
| **🔢 Normalización** | `run_normalizacion()` | Transforma matrices originales mediante 6 métodos distintos (incluyendo referencia ideal RIM). |
| **⚖️ Ponderación** | `run_ponderacion()` | Obtiene pesos de criterios mediante métodos objetivos (CRITIC, Entropía, etc.) y subjetivos (AHP, Tasación, Ordenación). |
| **📊 Agregación Multicriterio** | `run_agregacion()` | Aplica Suma Ponderada y Media Geométrica Ponderada sobre matrices normalizadas. |
| **📊 AHP (Saaty)** | `run_ahp()` | Proceso Analítico Jerárquico completo con comparaciones pareadas e índices de consistencia (RC). |
| **📊 TOPSIS** | `run_topsis()` | Modelo TOPSIS con selección de funciones de distancia (Euclídea, Manhattan, Tchebycheff, etc.). |
| **📊 RIM** | `run_rim()` | Reference Ideal Method con rangos ideales personalizados $[b, d]$ por criterio. |

---

## 💻 Uso en Colab

Podés ejecutar cada herramienta en una celda independiente invocando su respectiva función:

### 1. Estadística Descriptiva
```python
# Celda 1 — Estadística Descriptiva
from decision_models import run_estadistica
run_estadistica()
```

### 2. Normalización de Matrices
```python
# Celda 2 — Normalización
from decision_models import run_normalizacion
run_normalizacion()
```

### 3. Calculadora de Ponderaciones (Pesos)
```python
# Celda 3 — Calculadora de Ponderaciones
from decision_models import run_ponderacion
run_ponderacion()
```

### 4. Agregación Multicriterio (Suma Ponderada / Media Geométrica)
```python
# Celda 4 — Agregación Multicriterio
from decision_models import run_agregacion
run_agregacion()
```

### 5. Proceso Analítico Jerárquico (AHP)
```python
# Celda 5 — AHP
from decision_models import run_ahp
run_ahp()
```

### 6. TOPSIS
```python
# Celda 6 — TOPSIS
from decision_models import run_topsis
run_topsis()
```

### 7. RIM (Reference Ideal Method)
```python
# Celda 7 — RIM
from decision_models import run_rim
run_rim()
```
---

## 📂 Formato de los archivos de entrada (Excel / CSV)

Para garantizar la correcta lectura de datos en las distintas funciones:

### 1. Para Estadística, Normalización, Ponderación, Agregación, TOPSIS y RIM:
- **Estructura de Matriz de Decisión:**
  - La **primera columna** debe contener las **Alternativas** (nombres o identificadores).
  - Las **columnas restantes** corresponden a los **Criterios** (nombres en la primera fila/encabezado).
  - Los datos numéricos no deben contener celdas combinadas, columnas vacías ni símbolos especiales.

| Alternativas | Criterio_1 | Criterio_2 | Criterio_3 |
| :--- | :---: | :---: | :---: |
| Alternativa A | 150.5 | 12.0 | 0.85 |
| Alternativa B | 200.0 | 18.5 | 0.92 |
| Alternativa C | 110.0 | 15.0 | 0.70 |

### 2. Para la herramienta AHP (`run_ahp()`):
- **Estructura de 2 Columnas sin Encabezado Complejo:**
  - **Columna A:** Lista de Alternativas a evaluar.
  - **Columna B:** Lista de Criterios a considerar.

| Columna A (Alternativas) | Columna B (Criterios) |
| :--- | :--- |
| Alternativa 1 | Criterio Costo |
| Alternativa 2 | Criterio Calidad |
| Alternativa 3 | Criterio Tiempo |

---

## 📦 Exportación de Resultados
Todas las herramientas incluyen un botón interactivo para descargar los reportes, matrices transformadas, ponderaciones y rankings calculados directamente en un archivo Excel (`.xlsx`) estructurado.
