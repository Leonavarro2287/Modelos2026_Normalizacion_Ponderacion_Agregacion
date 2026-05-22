# 📝 Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/).

---

## [1.0.0] – 2026-05-21

### ✨ Inicial Release

#### Added
- **Línea 1 – Estadística Descriptiva**
  - Cálculo de 16 medidas estadísticas
  - Matriz de correlación de Pearson
  - Boxplots y histogramas interactivos
  - Exportación a Excel

- **Línea 2 – Normalización**
  - 6 métodos de normalización:
    - Fracción del máximo
    - Fracción de la suma
    - Fracción del rango
    - Del vector (euclidiana)
    - Z-score
    - Ideal de Referencia (RIM)
  - Interfaz intuitiva
  - Descarga de matriz normalizada

- **Línea 3 – Calculadora de Ponderaciones**
  - 8 métodos de ponderación:
    - Uniforme
    - Desviación estándar
    - Coef. de variación
    - Entropía
    - CRITIC
    - Ordenación simple
    - Tasación simple
    - AHP (Saaty)
  - Soporte para comparaciones pareadas AHP
  - Validación de consistencia

- **Línea 4 – Agregación Multicriterio**
  - Suma Ponderada
  - Media Geométrica Ponderada
  - Gráficos de ranking
  - Análisis de sensibilidad
  - Matriz transformada para media geométrica

- **Línea 5 – TOPSIS**
  - 4 métricas de distancia:
    - Euclidea (p=2)
    - Manhattan (p=1)
    - Raíz de Manhattan
    - Tchebycheff (p=∞)
  - 6 métodos de normalización
  - Cálculo detallado S⁺, S⁻, C(i)
  - Importación desde Línea 2

- **Línea 6 – RIM**
  - Normalización con rango ideal [b, d]
  - Penalización por distancia mínima
  - 3 métricas de distancia
  - Índices I(i) y ranking
  - Análisis paso a paso

#### Technical
- Implementado en Jupyter Notebooks
- Interfaz con ipywidgets
- Exportación a Excel con openpyxl
- Visualizaciones con matplotlib
- Compatibilidad con Google Colab

#### Documentation
- README.md completo
- Ejemplos de uso
- Guía de métodos matemáticos
- Referencias académicas

---

## [Unreleased]

### 🔄 En Progreso
- [ ] Línea 4 integración completa en notebook
- [ ] Línea 5 TOPSIS en notebook
- [ ] Línea 6 RIM en notebook
- [ ] Ejemplos con datasets de prueba
- [ ] Validación numérica completa

### 🎯 Próximas Funcionalidades
- [ ] Método ELECTRE
- [ ] Método VIKOR
- [ ] Análisis de robustez
- [ ] Gráficos radar de criterios
- [ ] Exportación a PDF
- [ ] Traducción a inglés
- [ ] API REST (opcional)
- [ ] Dashboard interactivo con Streamlit

### 🐛 Bugs Conocidos
- Ninguno reportado aún

---

## Cómo Usar Este Changelog

- **Added** para nuevas funcionalidades
- **Changed** para cambios en funcionalidad existente
- **Deprecated** para funcionalidades próximas a eliminar
- **Removed** para funcionalidades eliminadas
- **Fixed** para correcciones de bugs
- **Security** para alertas de seguridad

---

**Última actualización:** 2026-05-21
