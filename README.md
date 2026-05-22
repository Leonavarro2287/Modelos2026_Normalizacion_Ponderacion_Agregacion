# 📊 Modelos 2026 – Normalización, Ponderación y Agregación Multicriterio

Herramienta integral basada en Jupyter Notebooks para análisis de decisiones multicriterio. Implementa métodos clásicos de normalización, ponderación y agregación de alternativas.

**Autor:** Leonardo Navarro  
**Curso:** Modelos de Decisión – Unidad 3  
**Plataforma:** Google Colab / Jupyter

---

## 🎯 Instalación

```python
!pip install git+https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion.git -q
```

---

## 📐 Herramientas Disponibles

| Herramienta | Descripción | Métodos |
|---|---|---|
| **Línea 1** | Estadística Descriptiva | Media, mediana, DS, CV, correlaciones, visualizaciones |
| **Línea 2** | Normalización | 6 métodos (máximo, suma, rango, vector, Z-score, RIM) |
| **Línea 3** | Ponderación | 8 métodos (uniforme, CRITIC, entropía, AHP, etc.) |
| **Línea 4** | Agregación | Suma Ponderada, Media Geométrica |
| **Línea 5** | TOPSIS | 4 funciones de distancia (euclidea, manhattan, etc.) |
| **Línea 6** | RIM | Rango ideal flexible con análisis completo |

---

## 🚀 Uso en Colab

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

---

## 📋 Formato de Datos

| Alternativa | Criterio_1 | Criterio_2 | Criterio_3 |
|---|---|---|---|
| A1 | 45.2 | 120 | 0.85 |
| A2 | 62.1 | 95 | 0.92 |
| A3 | 38.5 | 180 | 0.78 |

- ✅ Primera columna: nombres de alternativas
- ✅ Demás columnas: criterios numéricos
- ✅ Sin filas/columnas vacías
- ✅ Formatos: `.xlsx`, `.xls`, `.csv`

---

## 🔧 Métodos Matemáticos

### Normalización (Línea 2)

| Método | Fórmula | Rango |
|--------|---------|-------|
| Fracción del máximo | $\frac{x_j}{\max_j}$ | [0,1] |
| Fracción de la suma | $\frac{x_j}{\sum x_j}$ | [0,1] |
| Fracción del rango | $\frac{x_j - \min}{\max - \min}$ | [0,1] |
| Del vector | $\frac{x_j}{\sqrt{\sum x_j^2}}$ | [0,1] |
| Z-score | $\frac{x_j - \bar{x}}{DS}$ | ℝ |
| RIM | Piecewise (C, D) | [0,1] |

### Ponderación (Línea 3)

| Método | Tipo | Cálculo |
|--------|------|---------|
| Uniforme | Objetivo | $w_j = 1/n$ |
| Desviación Estándar | Objetivo | $w_j = \frac{DS_j}{\sum DS}$ |
| CRITIC | Objetivo | $w_j = \frac{DS_j \times (1-\rho)}{\sum}$ |
| Entropía | Objetivo | $w_j = \frac{1-E_j}{\sum(1-E)}$ |
| Coef. Variación | Objetivo | $w_j = \frac{CV_j}{\sum CV}$ |
| Ordenación Simple | Manual | $w_j = \frac{\text{rango}_j}{\sum \text{rango}}$ |
| Tasación Simple | Manual | $w_j = \frac{\text{puntaje}_j}{\sum \text{puntaje}}$ |
| AHP (Saaty) | Manual | Comparaciones pareadas (1-9) |

### Agregación (Línea 4)

$$\text{Suma Ponderada: } U(a_i) = \sum_{j=1}^{n} w_j \cdot r_{ij}$$

$$\text{Media Geométrica: } U(a_i) = \left( \prod_{j=1}^{n} r_{ij}^{w_j} \right)^{1/n}$$

### TOPSIS (Línea 5)

$$C(i) = \frac{S_i^-}{S_i^+ + S_i^-}$$

**Distancias disponibles:**
- Euclidea (p=2)
- Manhattan (p=1)
- Raíz Manhattan
- Tchebycheff (p=∞)

### RIM (Línea 6)

$$r_{ij} = \begin{cases}
1.0 & \text{si } b \le x \le d \\
1 - \frac{\min(|x-b|, |x-d|)}{b - a_{min}} & \text{si } x < b \\
1 - \frac{\min(|x-d|, |x-b|)}{a_{max} - d} & \text{si } x > d
\end{cases}$$

---

## 📊 Ejemplo de Análisis Completo
PASO 1: Estadística Descriptiva (L1)
├─ Cargar datos: 5 alternativas × 4 criterios
├─ Media, DS, CV, correlaciones
└─ Identificar outliers
PASO 2: Normalización (L2)
├─ Elegir método: Fracción del Máximo
└─ Resultado: matriz [0,1]
PASO 3: Ponderación (L3)
├─ Método 1: Uniforme (0.25 cada uno)
├─ Método 2: CRITIC (automático)
└─ Método 3: AHP (comparaciones pareadas)
PASO 4: Agregación (L4)
├─ Suma Ponderada con pesos CRITIC
└─ Ranking: A > C > B > E > D
PASO 5: Validar con TOPSIS (L5)
├─ Distancia euclidea
└─ Ranking: A > C > B > E > D ✓
PASO 6: Análisis RIM (L6)
├─ Rango ideal [50, 100]
└─ Ranking: A > C > B > E > D ✓

---

## 💡 Recomendaciones de Uso

### ¿Cuándo usar cada normalización?
- **Fracción del máximo:** Criterios de utilidad simple
- **Fracción de la suma:** Datos proporcionales
- **Fracción del rango:** Escala lineal [0,1]
- **Vector:** TOPSIS, RIM (distancias)
- **Z-score:** Distribuciones distintas
- **RIM:** Rangos ideales específicos

### ¿Cuándo usar cada ponderación?
- **Uniforme:** Sin criterios claros
- **CRITIC:** Datos con variabilidad
- **Ordenación/Tasación:** Experto disponible
- **AHP:** Decisión importante, consistencia

### ¿Cuándo usar cada agregación?
- **Suma Ponderada:** Flexibilidad, compensatorio
- **Media Geométrica:** Decisión severa, no compensatorio
- **TOPSIS:** Análisis de sensibilidad, robustez
- **RIM:** Rango ideal específico

---

## 📦 Dependencias
pandas>=1.3.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
ipywidgets>=7.6.0
openpyxl>=3.6.0
jupyter>=1.0.0

---

## 🎓 Aplicaciones

✅ Selección de proveedores  
✅ Evaluación de proyectos  
✅ Comparación de alternativas  
✅ Priorización de inversiones  
✅ Planificación estratégica  
✅ Análisis de sostenibilidad  
✅ Benchmarking competitivo

---

## 📝 Licencia

MIT License – Libre para uso académico y comercial

---

## 👤 Autor

**Leonardo Navarro**  
📧 [LinkedIn](https://linkedin.com/in/leonavarro)  
🔗 [GitHub](https://github.com/Leonavarro2287)

---

## 🔗 Referencias Académicas

- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
- Hwang, C. L., & Yoon, K. (1981). *Multiple Attribute Decision Making*. Springer.
- Roy, B. (1990). *The Outranking Approach and the Foundations of ELECTRE Methods*. Kluwer.
- Zeleny, M. (1982). *Multiple Criteria Decision Making*. McGraw-Hill.

---

**Última actualización:** 2026-05-21  
**Versión:** 1.0.0
