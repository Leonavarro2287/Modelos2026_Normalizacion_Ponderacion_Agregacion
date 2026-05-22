"""
📊 Modelos 2026 - Normalización, Ponderación y Agregación Multicriterio
Version: 1.0.0
Autor: Leonardo Navarro
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import io
import base64
import warnings
from itertools import combinations

warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:.4f}'.format

__version__ = "1.0.0"
__author__ = "Leonardo Navarro"

# ============================================================
# LÍNEA 1 - ESTADÍSTICA DESCRIPTIVA
# ============================================================

def run_estadistica():
    """Ejecuta análisis de estadística descriptiva"""
    
    L1 = {"df": None, "df_stats": None, "df_criterios": None, "corr_matrix": None}

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

    upload1 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                  description="📂 Subir archivo", button_style="primary")
    upload1_out = widgets.Output()
    col_alt1 = widgets.Dropdown(description="Alternativas:", options=[],
                                style={"description_width":"110px"},
                                layout=widgets.Layout(width="320px"))
    col_crit1 = widgets.SelectMultiple(description="Criterios:", options=[],
                                        layout=widgets.Layout(height="140px", width="380px"),
                                        style={"description_width":"80px"})
    run1_btn = widgets.Button(description="▶ Calcular estadísticas",
                              button_style="success",
                              layout=widgets.Layout(width="240px"))
    run1_out = widgets.Output()
    dl1_btn = widgets.Button(description="⬇ Descargar Excel",
                              button_style="info",
                              layout=widgets.Layout(width="200px"))
    dl1_btn.layout.display = "none"
    dl1_out = widgets.Output()

    def _load1(change):
        with upload1_out:
            clear_output()
            if not upload1.value: return
            key = list(upload1.value.keys())[0]
            fdata = upload1.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L1["df"] = df
                cols = list(df.columns)
                col_alt1.options = cols
                col_crit1.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload1.observe(_load1, names="value")

    STATS_NOMBRES = [
        "Media", "Error típico", "Mediana", "Moda",
        "Desviación estándar", "CV (DS/Media)", "Varianza muestral",
        "Curtosis", "Coef. asimetría (Excel SKEW)",
        "Rango", "Mínimo", "Máximo", "Máx/Mín",
        "Suma", "Cuenta", "Módulo"
    ]

    def _calcular_stats(serie):
        s = pd.to_numeric(serie, errors="coerce").dropna()
        n = len(s)
        media = s.mean()
        err_tip = stats.sem(s)
        mediana = s.median()
        try:
            moda = s.mode().iloc[0]
        except:
            moda = np.nan
        ds = s.std(ddof=1)
        cv = ds / media if media != 0 else np.nan
        varianza = s.var(ddof=1)
        kurt = s.kurt()
        if n > 2 and ds != 0:
            asim = (n / ((n-1) * (n-2))) * (((s - media) / ds)**3).sum()
        else:
            asim = np.nan
        rango = s.max() - s.min()
        minimo = s.min()
        maximo = s.max()
        max_min = maximo / minimo if minimo != 0 else np.nan
        suma = s.sum()
        cuenta = n
        modulo = np.sqrt((s**2).sum())
        return [media, err_tip, mediana, moda, ds, cv, varianza,
                kurt, asim, rango, minimo, maximo, max_min, suma, cuenta, modulo]

    def _run1(b):
        with run1_out:
            clear_output()
            df = L1["df"]
            if df is None:
                print("❌ Cargá un archivo primero.")
                return
            crit_cols = list(col_crit1.value)
            if not crit_cols:
                print("❌ Seleccioná al menos un criterio.")
                return
            df_c = df[crit_cols].apply(pd.to_numeric, errors="coerce")
            L1["df_criterios"] = df_c
            filas = {col: _calcular_stats(df_c[col]) for col in crit_cols}
            df_stats = pd.DataFrame(filas, index=STATS_NOMBRES)
            L1["df_stats"] = df_stats
            display(HTML("<b>Estadísticas descriptivas</b>"))
            display(df_stats.round(4))

            if len(crit_cols) >= 2:
                corr_matrix = df_c[crit_cols].corr()
                L1["corr_matrix"] = corr_matrix
                display(HTML("<br><b>Matriz de correlación de Pearson</b>"))
                display(corr_matrix.round(4))
            else:
                L1["corr_matrix"] = None
                print("\n⚠️ Se necesitan al menos 2 criterios para la matriz de correlación.")

            # Boxplots
            display(HTML("<b>Boxplots</b>"))
            n_crit = len(crit_cols)
            colors = plt.cm.tab10.colors
            fig, axes = plt.subplots(1, n_crit, figsize=(max(4*n_crit, 6), 5), squeeze=False)
            for idx, col in enumerate(crit_cols):
                ax = axes[0][idx]
                bp = ax.boxplot(df_c[col].dropna(), patch_artist=True,
                                medianprops=dict(color="white", linewidth=2))
                bp["boxes"][0].set_facecolor(colors[idx % 10])
                ax.set_title(col, fontsize=11, fontweight="bold")
                ax.set_xticks([])
                ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.4f"))
                ax.grid(axis="y", linestyle="--", alpha=0.5)
            plt.suptitle("Boxplots por criterio", fontsize=13, fontweight="bold", y=1.01)
            plt.tight_layout()
            plt.show()

            # Histogramas
            display(HTML("<b>Histogramas</b>"))
            fig2, axes2 = plt.subplots(1, n_crit, figsize=(max(4*n_crit, 6), 4), squeeze=False)
            for idx, col in enumerate(crit_cols):
                ax = axes2[0][idx]
                ax.hist(df_c[col].dropna(), bins="auto", color=colors[idx % 10],
                        edgecolor="white", alpha=0.85)
                ax.set_title(col, fontsize=11, fontweight="bold")
                ax.set_xlabel("Valor", fontsize=9)
                ax.set_ylabel("Frecuencia", fontsize=9)
                ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.4f"))
                ax.grid(axis="y", linestyle="--", alpha=0.4)
            plt.suptitle("Histogramas por criterio", fontsize=13, fontweight="bold", y=1.01)
            plt.tight_layout()
            plt.show()
            dl1_btn.layout.display = ""

    run1_btn.on_click(_run1)

    def _download1(b):
        with dl1_out:
            clear_output()
            df_stats = L1.get("df_stats")
            df_c = L1.get("df_criterios")
            corr_mat = L1.get("corr_matrix")
            if df_stats is None:
                print("❌ Calculá primero.")
                return
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_stats.round(4).to_excel(writer, sheet_name="Estadisticas", startrow=2)
                ws1 = writer.sheets["Estadisticas"]
                ws1.cell(row=1, column=1,
                         value="ESTADÍSTICAS DESCRIPTIVAS – Modelos de Decisión | Unidad 3")
                if df_c is not None:
                    df_c.round(4).to_excel(writer, sheet_name="Datos_criterios", startrow=2)
                    ws2 = writer.sheets["Datos_criterios"]
                    ws2.cell(row=1, column=1, value="DATOS ORIGINALES – Criterios seleccionados")
                if corr_mat is not None:
                    corr_mat.round(4).to_excel(writer, sheet_name="Matriz_correlacion", startrow=2)
                    ws3 = writer.sheets["Matriz_correlacion"]
                    ws3.cell(row=1, column=1, value="MATRIZ DE CORRELACIÓN (Pearson)")
            buf.seek(0)
            b64 = base64.b64encode(buf.getvalue()).decode()
            display(HTML(f'<a download="estadisticas.xlsx" '
                         f'href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">'
                         f'⬇ Descargar estadisticas.xlsx</a>'))

    dl1_btn.on_click(_download1)

    display(widgets.HTML("<h3>📐 LÍNEA 1 – Estadística Descriptiva</h3>"))
    display(_sep("1. Cargar archivo (.xlsx / .xls / .csv)"))
    display(upload1, upload1_out)
    display(_sep("2. Seleccionar columnas"))
    display(widgets.HBox([col_alt1, col_crit1]))
    display(_sep("3. Calcular"))
    display(run1_btn, run1_out)
    display(dl1_btn, dl1_out)


# ============================================================
# LÍNEA 2 - NORMALIZACIÓN
# ============================================================

def run_normalizacion():
    """Ejecuta análisis de normalización"""
    display(widgets.HTML("<h3>🔢 LÍNEA 2 – Normalización</h3>"))
    display(widgets.HTML("<p>⚙️ Función en desarrollo - Úsalo desde el notebook</p>"))


# ============================================================
# LÍNEA 3 - PONDERACIÓN
# ============================================================

def run_ponderacion():
    """Ejecuta análisis de ponderación"""
    display(widgets.HTML("<h3>⚖️ LÍNEA 3 – Ponderación</h3>"))
    display(widgets.HTML("<p>⚙️ Función en desarrollo - Úsalo desde el notebook</p>"))


# ============================================================
# LÍNEA 4 - AGREGACIÓN
# ============================================================

def run_agregacion():
    """Ejecuta análisis de agregación multicriterio"""
    display(widgets.HTML("<h3>📊 LÍNEA 4 – Agregación</h3>"))
    display(widgets.HTML("<p>⚙️ Función en desarrollo - Úsalo desde el notebook</p>"))


# ============================================================
# LÍNEA 5 - TOPSIS
# ============================================================

def run_topsis():
    """Ejecuta análisis TOPSIS"""
    display(widgets.HTML("<h3>📊 LÍNEA 5 – TOPSIS</h3>"))
    display(widgets.HTML("<p>⚙️ Función en desarrollo - Úsalo desde el notebook</p>"))


# ============================================================
# LÍNEA 6 - RIM
# ============================================================

def run_rim():
    """Ejecuta análisis RIM"""
    display(widgets.HTML("<h3>📊 LÍNEA 6 – RIM</h3>"))
    display(widgets.HTML("<p>⚙️ Función en desarrollo - Úsalo desde el notebook</p>"))


__all__ = [
    'run_estadistica',
    'run_normalizacion',
    'run_ponderacion',
    'run_agregacion',
    'run_topsis',
    'run_rim'
]
