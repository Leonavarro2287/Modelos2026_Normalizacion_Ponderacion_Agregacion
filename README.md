# 📊 Modelos 2026 – Normalización, Ponderación y Agregación Multicriterio

Herramienta integral basada en Jupyter Notebooks para análisis de decisiones multicriterio. Implementa métodos clásicos de normalización, ponderación y agregación de alternativas.

**Autor:** Leonardo Navarro  
**Curso:** Modelos de Decisión – Unidad 3  
**Plataforma:** Google Colab / Jupyter

---

## 🎯 Contenido

### **Línea 1 – Estadística Descriptiva**
Cálculo automático de estadísticas básicas para exploración de datos:
- **Medidas de tendencia central:** Media, mediana, moda
- **Medidas de dispersión:** Desviación estándar, varianza, coeficiente de variación
- **Medidas de forma:** Curtosis, asimetría
- **Análisis de distribución:** Boxplots, histogramas
- **Análisis de relación:** Matriz de correlación de Pearson

📥 **Entrada:** Archivo `.xlsx`, `.xls` o `.csv`  
📤 **Salida:** Estadísticas descriptivas, matriz de correlación, visualizaciones

---

### **Línea 2 – Normalización**
Transformación de matrices de evaluación a escala [0, 1] con 6 métodos distintos:

| Método | Fórmula | Uso |
|--------|---------|-----|
| **Fracción del máximo** | $\frac{x_j}{max_j}$ | Criterios de maximización |
| **Fracción de la suma** | $\frac{x_j}{\sum x_j}$ | Datos proporcionales |
| **Fracción del rango** | $\frac{x_j - min_j}{max_j - min_j}$ | Rango 0-1 lineal |
| **Del vector** | $\frac{x_j}{\sqrt{\sum x_j^2}}$ | Normalización euclidiana |
| **Z-score** | $\frac{x_j - \bar{x}}{DS}$ | Datos con media-varianza |
| **Ideal de Referencia (RIM)** | Piecewise (C, D) | Rango ideal flexible |

📥 **Entrada:** Matriz de decisión original  
📤 **Salida:** Matriz normalizada

---

### **Línea 3 – Calculadora de Ponderaciones**
Cálculo de pesos para criterios mediante **8 métodos objetivos y subjetivos:**

| Método | Descripción | Parámetro |
|--------|-------------|-----------|
| **Uniforme** | Pesos iguales para todos | — |
| **Desviación estándar** | Basado en variabilidad | Automático |
| **Coef. de variación** | CV = DS / Media | Automático |
| **Entropía** | Información de Shannon | Automático |
| **CRITIC** | Contraste y correlación | Automático |
| **Ordenación simple** | Rangos definidos por usuario | Manual |
| **Tasación simple** | Puntajes definidos por usuario | Manual |
| **AHP (Saaty)** | Comparaciones pareadas (1-9) | Manual |

📥 **Entrada:** Matriz normalizada  
📤 **Salida:** Vector de pesos por método

---

### **Línea 4 – Agregación Multicriterio**
Síntesis de criterios con dos métodos de combinación:

#### **Suma Ponderada**
$$U(a_i) = \sum_{j=1}^{n} w_j \cdot r_{ij}$$

**Ventajas:**
- Aditiva (compensatorio)
- Interpretable linealmente
- Rápida computacionalmente

**Desventajas:**
- Oculta debilidades en criterios
- Requiere normalización cuidadosa

#### **Media Geométrica Ponderada**
$$U(a_i) = \left( \prod_{j=1}^{n} r_{ij}^{w_j} \right)^{1/n}$$

**Ventajas:**
- No compensatorio
- Penaliza debilidades extremas
- Escala independiente

**Desventajas:**
- Solo valores > 0
- Menos intuitiva

📥 **Entrada:** Matriz normalizada, pesos  
📤 **Salida:** Ranking final, gráfico comparativo

---

### **Línea 5 – TOPSIS**
**Technique for Order Preference by Similarity to Ideal Solution**

Clasifica alternativas por proximidad a solución ideal y distancia de anti-ideal:

$$C(i) = \frac{S_i^-}{S_i^+ + S_i^-}$$

**Funciones de distancia:**
- Euclidea (p=2)
- Manhattan / Ciudad (p=1)
- Raíz Manhattan
- Tchebycheff (p=∞)

**Métodos de normalización:**
- Del vector
- Fracción del máximo
- Fracción del rango
- Ideal de referencia (RIM)

📥 **Entrada:** Matriz normalizada, pesos, tipos (max/min)  
📤 **Salida:** Distancias (S⁺, S⁻), índices C(i), ranking

---

### **Línea 6 – RIM**
**Reference Ideal Method** – Variante de TOPSIS con rango ideal flexible

Define intervalo óptimo [b, d] para cada criterio:
- Valores en [b, d] → normalización = 1.0
- Valores fuera → penalización por distancia mínima

$$r_{ij} = \begin{cases}
1.0 & \text{si } b \le x \le d \\
1 - \frac{\min(|x-b|, |x-d|)}{b - a_{min}} & \text{si } x < b \\
1 - \frac{\min(|x-d|, |x-b|)}{a_{max} - d} & \text{si } x > d
\end{cases}$$

📥 **Entrada:** Matriz original, pesos, rangos [b, d]  
📤 **Salida:** Matriz normalizada RIM, índices I(i), ranking

---

## 🚀 Uso Rápido

### **En Google Colab:**

```python
# 1. Copiar el notebook completo en una celda de Colab
# 2. Ejecutar todo (Ctrl+F9)
# 3. Cargar archivo .xlsx / .csv con datos
# 4. Seguir las líneas de análisis en orden
```

### **En Jupyter local:**

```bash
jupyter notebook Modelos2026_Normalizacion_Ponderacion_Agregacion.ipynb
```

---

## 📋 Estructura de Datos

### **Formato de entrada:**

```
Alternativas | Criterio_1 | Criterio_2 | Criterio_3 | ...
A1           | 45.2       | 120        | 0.85       | ...
A2           | 62.1       | 95         | 0.92       | ...
A3           | 38.5       | 180        | 0.78       | ...
...
```

✅ **Columnas numéricas:** Criterios de evaluación  
✅ **Primera columna:** Nombres de alternativas (opcional para métodos internos)  
✅ **Sin filas vacías** en los datos

### **Formatos soportados:**
- `.xlsx` (Excel moderno)
- `.xls` (Excel clásico)
- `.csv` (separador por comas, punto decimal)

---

## 🔧 Métodos Matemáticos Implementados

### **Normalización**
| Método | Rango | Fórmula |
|--------|-------|---------|
| Máximo | [0,1] | $r = x / \max$ |
| Suma | [0,1] | $r = x / \sum x$ |
| Rango | [0,1] | $r = (x - \min) / (\max - \min)$ |
| Vector | [0,1] | $r = x / \sqrt{\sum x^2}$ |
| Z-score | ℝ | $r = (x - \mu) / \sigma$ |
| RIM | [0,1] | Piecewise (C, D) |

### **Ponderación**
| Método | Fundamento |
|--------|-----------|
| Uniforme | Equipeso |
| DS | Variabilidad de columnas |
| CV | Coef. variación |
| Entropía | Teoría de información |
| CRITIC | Contraste + correlación |
| Ordenación | Ranking experto |
| Tasación | Puntuación experto |
| AHP | Comparaciones pareadas Saaty |

### **Agregación**
| Método | Compensatorio | Valores Requeridos |
|--------|---------------|--------------------|
| Suma Ponderada | Sí | ≥ 0 |
| Media Geométrica | No | > 0 |
| TOPSIS | Parcial | ≥ 0 |
| RIM | No | Flexible |

---

## 📊 Ejemplo de Análisis Completo

```
PASO 1: Cargar datos de 5 alternativas × 4 criterios
├─ Alternativa A, B, C, D, E
└─ Criterios: Costo, Calidad, Tiempo, Sostenibilidad

PASO 2: Explorar con Estadística Descriptiva (L1)
├─ Media, DS, CV por criterio
├─ Matriz de correlaciones
└─ Identificar outliers

PASO 3: Normalizar (L2)
├─ Elegir método: Fracción del Máximo
└─ Resultado: matriz [0,1]

PASO 4: Ponderar (L3)
├─ Método 1: Uniforme (0.25 cada uno)
├─ Método 2: CRITIC (automático)
└─ Método 3: AHP (comparaciones pareadas)

PASO 5: Agregar (L4)
├─ Suma Ponderada con pesos CRITIC
└─ Ranking final: A > C > B > E > D

PASO 6: Validar con TOPSIS (L5)
├─ Función distancia: Euclidea
├─ Ranking: A > C > B > E > D ✓
└─ Robustez confirmada

PASO 7: Análisis RIM (L6)
├─ Rango ideal [50, 100] para cada criterio
└─ Ranking: A > C > B > E > D ✓
```

---

## 📈 Recomendaciones de Uso

### **¿Cuándo usar cada método de normalización?**
- **Fracción del máximo:** Criterios de utilidad simple
- **Fracción de la suma:** Datos proporcionales (ej: presupuestos)
- **Fracción del rango:** Escala lineal [0,1]
- **Vector:** Métodos de distancia (TOPSIS, RIM)
- **Z-score:** Datos con distribuciones distintas
- **RIM:** Rangos ideales flexibles

### **¿Cuándo usar cada método de ponderación?**
| Situación | Método | Razón |
|-----------|--------|-------|
| Sin criterios claros | Uniforme | Equipeso |
| Datos con variabilidad | CRITIC | Automático |
| Experto disponible | Ordenación/Tasación | Captura juicio |
| Decisión importante | AHP | Consistencia verificada |

### **¿Cuándo usar cada método de agregación?**
| Objetivo | Método | Razón |
|----------|--------|-------|
| Flexibilidad | Suma Ponderada | Compensatorio |
| Decisión severa | Media Geométrica | No compensatorio |
| Análisis de sensibilidad | TOPSIS | Robustez probada |
| Rango ideal específico | RIM | Flexible |

---

## 📦 Dependencias

```
pandas>=1.3.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
ipywidgets>=7.6.0
openpyxl>=3.6.0
```

**Instalación automática en Colab:** ✓ Incluida  
**Instalación en Jupyter local:**
```bash
pip install pandas numpy scipy matplotlib ipywidgets openpyxl
```

---

## 🎓 Aplicaciones

✅ **Selección de proveedores**  
✅ **Evaluación de proyectos**  
✅ **Comparación de alternativas**  
✅ **Priorización de inversiones**  
✅ **Planificación estratégica**  
✅ **Análisis de sostenibilidad**  
✅ **Benchmarking competitivo**  

---

## 📝 Licencia

MIT License – Libre para uso académico y comercial

---

## 👤 Contacto

**Autor:** Leonardo Navarro  
**GitHub:** [@Leonavarro2287](https://github.com/Leonavarro2287)  
**Institución:** Modelos de Decisión – Unidad 3

---

## 🔗 Referencias Académicas

- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
- Hwang, C. L., & Yoon, K. (1981). *Multiple Attribute Decision Making*. Springer.
- Roy, B. (1990). *The Outranking Approach and the Foundations of ELECTRE Methods*. Kluwer.
- Zeleny, M. (1982). *Multiple Criteria Decision Making*. McGraw-Hill.

---

**Última actualización:** 2026-05-21  
**Versión:** 1.0
