# 🚀 Guía Rápida de Inicio

## ⏱️ 5 minutos para empezar

### 1️⃣ **Abrir en Google Colab** (recomendado)

Acceso directo sin instalación:

```
https://colab.research.google.com/github/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion/blob/main/Modelos2026_Normalizacion_Ponderacion_Agregacion.ipynb
```

O:
1. Copia el link anterior
2. Abre https://colab.research.google.com
3. Archivo → Abrir desde URL
4. Pega el link
5. ¡Listo! Ejecuta la primera celda (Ctrl+F9)

---

### 2️⃣ **Instalación Local (Jupyter)**

#### Requisitos previos:
- Python 3.8+
- pip

#### Pasos:

```bash
# 1. Clonar repositorio
git clone https://github.com/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion.git
cd Modelos2026_Normalizacion_Ponderacion_Agregacion

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar Jupyter
jupyter notebook Modelos2026_Normalizacion_Ponderacion_Agregacion.ipynb
```

---

## 📊 Tu Primer Análisis

### Paso 1: Preparar datos

Crea un archivo `datos.csv` con formato:

```csv
Alternativa,Criterio1,Criterio2,Criterio3
Alt_A,45,120,0.85
Alt_B,62,95,0.92
Alt_C,38,180,0.78
```

**Requisitos:**
- Primera columna: nombres de alternativas
- Demás columnas: criterios numéricos
- Sin filas/columnas vacías

### Paso 2: Explorar datos (Línea 1)

1. Carga tu archivo en el widget "📂 Subir archivo"
2. Selecciona los criterios que analizar
3. Haz clic en "▶ Calcular estadísticas"
4. Observa medias, desviaciones, correlaciones
5. Descarga resultados en Excel

**Salida esperada:**
```
✅ datos.csv | 3 filas × 4 columnas

Estadísticas descriptivas
Media       45.0    130.5   0.85
DS          12.3    42.1    0.07
...

Matriz de correlación de Pearson
           C1    C2     C3
C1      1.00  -0.82  0.91
C2     -0.82   1.00 -0.87
...
```

### Paso 3: Normalizar (Línea 2)

1. Carga la matriz original
2. Selecciona criterios
3. Elige método:
   - **Fracción de la suma** → datos proporcionales
   - **Del vector** → TOPSIS, RIM
   - **Fracción del rango** → escala lineal
4. Haz clic en "▶ Normalizar"
5. Descarga matriz normalizada

**Salida esperada:**
```
🔢 Matriz Normalizada – Fracción de la suma

Alternativa  Criterio1  Criterio2  Criterio3
Alt_A        0.3333     0.3571     0.3367
Alt_B        0.4576     0.2813     0.3633
Alt_C        0.2791     0.5357     0.3080
```

### Paso 4: Asignar pesos (Línea 3)

1. Carga matriz normalizada
2. Selecciona criterios
3. Elige métodos de ponderación:
   - **Uniforme** → equipeso
   - **CRITIC** → automático
   - **AHP** → comparaciones pareadas
4. Haz clic en "▶ Calcular pesos"

**Salida esperada:**
```
Pesos calculados

Método              Criterio1  Criterio2  Criterio3  ∑ pesos
Uniforme            0.3333     0.3333     0.3333     1.0000
CRITIC              0.2156     0.4521     0.3323     1.0000
AHP                 0.2857     0.4286     0.2857     1.0000
```

### Paso 5: Agregar (Línea 4)

1. Carga matriz normalizada
2. Selecciona criterios y pesos
3. Elige método:
   - **Suma Ponderada** → flexible, compensatorio
   - **Media Geométrica** → severo, no compensatorio
4. Haz clic en "▶ Calcular agregación"

**Salida esperada:**
```
Resultados – Suma Ponderada

Ranking  Alternativa  U(a)      
1        Alt_A        0.8234
2        Alt_C        0.7892
3        Alt_B        0.7156
```

### Paso 6: Validar con TOPSIS (Línea 5)

1. Carga matriz normalizada
2. Define tipo de cada criterio (max/min)
3. Asigna pesos
4. Elige función de distancia (euclidea recomendada)
5. Haz clic en "▶ Ejecutar TOPSIS"

**Salida esperada:**
```
Paso 7: Índice de Similaridad C(i) y Ranking

Alternativa  S+      S-      C(i)    Ranking
Alt_A        0.1234  0.4567  0.7874  1
Alt_C        0.1456  0.3892  0.7278  2
Alt_B        0.1678  0.3456  0.6732  3
```

### Paso 7: Análisis RIM (Línea 6)

1. Define rango ideal [b, d] para cada criterio
2. Asigna pesos
3. Haz clic en "⚙️ Configurar rangos ideales"
4. Haz clic en "▶ Ejecutar RIM"

---

## 🎯 Ejemplos de Uso

### Seleccionar Proveedor

**Alternativas:** Proveedor A, B, C  
**Criterios:**
- Precio (minimizar)
- Calidad (maximizar, 0-10)
- Tiempo entrega (minimizar, días)
- Sostenibilidad (maximizar, 0-100)

**Pasos:**
1. Estadística Descriptiva → explorar datos
2. Normalización → Fracción del rango
3. Ponderación → CRITIC (automático)
4. Agregación → Suma Ponderada
5. Validar → TOPSIS

---

### Evaluar Proyectos

**Alternativas:** Proyecto 1, 2, 3  
**Criterios:**
- ROI esperado (%)
- Riesgo (1-10)
- Plazo (meses)
- Impacto estratégico (1-10)

**Pasos:** Mismo flujo anterior

---

### Comparar Productos

**Alternativas:** Producto A, B, C  
**Criterios:**
- Precio
- Especificaciones
- Garantía (años)
- Opinión usuarios (1-5)

**Pasos:** Mismo flujo anterior

---

## 🔧 Troubleshooting

### ❌ Error: "No module named 'openpyxl'"
```bash
pip install openpyxl
```

### ❌ Error: "File not found"
- Verifica que el archivo esté en la carpeta correcta
- Usa rutas absolutas si es necesario
- En Colab, carga desde Google Drive

### ❌ Error: "División por cero"
- Elimina filas/columnas con valores 0
- Reemplaza con valores mínimos positivos
- Usa método de normalización diferente

### ⚠️ Suma de pesos ≠ 1
- Puede ser normal con métodos como Z-score
- Normaliza manualmente: w_i / Σw_i
- Verifica fórmula en documentación

---

## 📚 Próximos Pasos

1. **Lee el README completo** para entender cada método
2. **Explora los ejemplos** en la carpeta `ejemplos/`
3. **Consulta referencias académicas** al final del README
4. **Experimenta** con tus propios datos
5. **Reporta bugs** o sugiere mejoras en Issues

---

## 💬 ¿Preguntas?

- 📖 Revisa el README.md
- 🐛 Abre una Issue en GitHub
- 💬 Usa Discussions
- 📧 Contacta al autor

**¡Feliz análisis! 🎉**
