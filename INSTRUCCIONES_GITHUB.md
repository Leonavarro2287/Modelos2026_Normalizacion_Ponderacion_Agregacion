# 📤 Instrucciones para Subir el Repositorio a GitHub

## 1️⃣ Crear el Repositorio en GitHub

### Opción A: Desde GitHub Web
1. Ve a https://github.com/new
2. Nombre: `Modelos2026_Normalizacion_Ponderacion_Agregacion`
3. Descripción: "Herramienta integral para análisis de decisiones multicriterio"
4. Privado/Público: **Público** (recomendado)
5. **No** inicializar con README (ya tenemos)
6. Haz clic en "Create repository"

---

## 2️⃣ Descargar y Preparar Archivos

### Opción A: Desde archivo ZIP (más fácil)

```bash
# 1. Descomprime el ZIP descargado
unzip Modelos2026_Normalizacion_Ponderacion_Agregacion.zip

# 2. Entra en la carpeta
cd Modelos2026_Normalizacion_Ponderacion_Agregacion

# 3. Inicializa repositorio Git
git init

# 4. Agrega tu email y nombre
git config user.name "Tu Nombre"
git config user.email "tu@email.com"

# 5. Agrega todos los archivos
git add .

# 6. Primer commit
git commit -m "Commit inicial: Herramienta multicriterio completa"

# 7. Renombra rama principal (si es necesario)
git branch -M main

# 8. Agregua URL del repositorio remoto
git remote add origin https://github.com/TU_USUARIO/Modelos2026_Normalizacion_Ponderacion_Agregacion.git

# 9. Push al repositorio
git push -u origin main
```

### Opción B: Clone y Reemplaza

```bash
# Si ya clonaste antes:
cd Modelos2026_Normalizacion_Ponderacion_Agregacion

# Reemplaza URL del remoto
git remote set-url origin https://github.com/TU_USUARIO/Modelos2026_Normalizacion_Ponderacion_Agregacion.git

# Agrega cambios
git add .
git commit -m "Actualización: Archivos completados"
git push origin main
```

---

## 3️⃣ Verificar que Todo Está Bien

### Después de hacer push:

1. **Accede a GitHub:**
   ```
   https://github.com/TU_USUARIO/Modelos2026_Normalizacion_Ponderacion_Agregacion
   ```

2. **Verifica que veas:**
   - ✅ Todos los archivos (.md, .ipynb, .csv)
   - ✅ README.md renderizado correctamente
   - ✅ Carpeta con la estructura completa

3. **Prueba el botón "Open in Colab":**
   - Si incluyes badge en README, debe funcionar

---

## 4️⃣ Problemas Comunes y Soluciones

### ❌ Error: "authentication failed"

**Solución:** Configura token personal de GitHub

```bash
# 1. Crea token en: https://github.com/settings/tokens
# 2. Genera con scopes: repo, gist

# 3. Intenta push nuevamente (te pedirá token)
git push origin main

# Ingresa token como contraseña
```

### ❌ Error: "fatal: 'origin' does not appear to be a 'git' repository"

**Solución:** Agrega nuevamente el remoto

```bash
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/Modelos2026_Normalizacion_Ponderacion_Agregacion.git
git push -u origin main
```

### ❌ Archivo muy grande (.ipynb > 100MB)

**Solución:** Limpia salidas del notebook

```bash
# Opción 1: Desde Jupyter
# Kernel → Restart & Clear Output

# Opción 2: Desde terminal
jupyter nbconvert --to notebook --inplace --ClearOutputPreprocessor.enabled=True Modelos2026_Normalizacion_Ponderacion_Agregacion.ipynb
```

---

## 5️⃣ Recomendaciones Adicionales

### 📌 Agrega Badges al README

En la sección superior del README.md, después del título:

```markdown
# 📊 Modelos 2026 – Normalización, Ponderación y Agregación Multicriterio

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Leonavarro2287/Modelos2026_Normalizacion_Ponderacion_Agregacion/blob/main/Modelos2026_Normalizacion_Ponderacion_Agregacion.ipynb)
```

### 📌 Actualiza Descripción del Repo

1. Ve a **Settings** → **About**
2. Descripción: "Herramienta integral para análisis de decisiones multicriterio"
3. URL (si tienes sitio web): tu-sitio.com
4. Topics: `decision-making`, `multicriteria`, `topsis`, `ahp`, `python`, `jupyter`

### 📌 Habilita GitHub Pages (opcional)

1. Ve a **Settings** → **Pages**
2. Source: **main branch**
3. Tema: Elige uno (ej: Minimal)
4. Se generará sitio en: `https://tu-usuario.github.io/Modelos2026_...`

---

## 6️⃣ Flujo de Trabajo Futuro

### Para hacer cambios:

```bash
# 1. Crea rama de feature
git checkout -b feature/mi-mejora

# 2. Realiza cambios
# (edita archivos)

# 3. Commit
git add .
git commit -m "Agregar nueva funcionalidad: [descripción]"

# 4. Push a tu rama
git push origin feature/mi-mejora

# 5. En GitHub, abre Pull Request
# - Elige base: main
# - Compara con: feature/mi-mejora
```

### Actualizar versión en CHANGELOG.md:

```markdown
## [1.1.0] – 2026-06-15

### Added
- Nueva funcionalidad X

### Fixed
- Bug en método Y

### Changed
- Mejora de rendimiento en Z
```

---

## 7️⃣ Verificación Final

Antes de dar por completo el repositorio:

✅ Todos los archivos están en GitHub  
✅ README.md se ve bien renderizado  
✅ Links funcionan (ej: QUICKSTART, CONTRIBUTING)  
✅ Notebook se abre sin errores en Colab  
✅ Datos de ejemplo carga correctamente  
✅ LICENSE visible  
✅ Badge "Open in Colab" funciona  

---

## 📞 Soporte

Si tienes problemas:

1. Revisa [GitHub Docs](https://docs.github.com)
2. Abre issue en tu repositorio
3. Consulta Stack Overflow con tags: `github`, `git`

**¡Éxito! 🎉**
