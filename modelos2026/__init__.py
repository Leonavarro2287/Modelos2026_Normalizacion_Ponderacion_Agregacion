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
# LÍNEA 2 - NORMALIZACIÓN (6 métodos)
# ============================================================
def run_normalizacion():
    """Ejecuta análisis de normalización con 6 métodos"""
    display(widgets.HTML("<h3>🔢 LÍNEA 2 – Normalización</h3>"))

    L2 = {"df": None, "df_criterios": None, "tipos": {}, "normalizado": None}

    upload = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                description="📂 Subir archivo", button_style="primary")
    upload_out = widgets.Output()

    col_crit = widgets.SelectMultiple(description="Criterios:",
                                      layout=widgets.Layout(height="140px", width="380px"))
    tipo_criterios = widgets.VBox([])
    metodo_norm = widgets.Dropdown(
        description="Método:",
        options=["Min-Max", "Z-Score", "Max", "Suma", "Vector", "Rango"],
        value="Min-Max"
    )
    run_btn = widgets.Button(description="▶ Normalizar", button_style="success")
    run_out = widgets.Output()
    dl_btn = widgets.Button(description="⬇ Descargar Excel", button_style="info",
                            layout=widgets.Layout(width="200px"))
    dl_btn.layout.display = "none"
    dl_out = widgets.Output()

    def on_file_upload(change):
        with upload_out:
            clear_output()
            if not upload.value:
                return
            key = list(upload.value.keys())[0]
            fdata = upload.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L2["df"] = df
                cols = list(df.columns)
                col_crit.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload.observe(on_file_upload, names="value")

    def update_tipo_widgets(*args):
        selected = list(col_crit.value)
        if not selected:
            tipo_criterios.children = []
            return
        children = []
        for c in selected:
            btn = widgets.ToggleButton(value=True, description=f"{c}: Beneficio",
                                       layout=widgets.Layout(width="200px"))
            btn.observe(lambda change, col=c: on_tipo_change(change, col), names="value")
            children.append(btn)
        tipo_criterios.children = children

    def on_tipo_change(change, col):
        L2["tipos"][col] = change["new"]
        change["owner"].description = f"{col}: {'Beneficio' if change['new'] else 'Costo'}"

    col_crit.observe(update_tipo_widgets, names="value")

    def normalizar(df, metodo, tipos):
        df_norm = df.copy()
        for col in df.columns:
            datos = df[col].astype(float)
            if metodo == "Min-Max":
                min_val = datos.min()
                max_val = datos.max()
                if max_val == min_val:
                    norm = np.ones_like(datos)
                else:
                    norm = (datos - min_val) / (max_val - min_val)
                if not tipos.get(col, True):
                    norm = 1 - norm

            elif metodo == "Z-Score":
                mean = datos.mean()
                std = datos.std(ddof=0)
                if std == 0:
                    norm = np.zeros_like(datos)
                else:
                    norm = (datos - mean) / std
                # Reescalar a [0,1] para mantener coherencia
                if norm.max() != norm.min():
                    norm = (norm - norm.min()) / (norm.max() - norm.min())
                else:
                    norm = np.zeros_like(datos)

            elif metodo == "Max":
                max_val = datos.max()
                norm = datos / max_val if max_val != 0 else datos
                if not tipos.get(col, True):
                    norm = 1 - norm

            elif metodo == "Suma":
                suma = datos.sum()
                norm = datos / suma if suma != 0 else datos
                if not tipos.get(col, True):
                    norm = 1 - norm

            elif metodo == "Vector":
                norma = np.sqrt((datos**2).sum())
                norm = datos / norma if norma != 0 else datos
                if not tipos.get(col, True):
                    norm = 1 - norm

            elif metodo == "Rango":
                rango = datos.max() - datos.min()
                if rango == 0:
                    norm = np.ones_like(datos)
                else:
                    norm = (datos - datos.min()) / rango
                if not tipos.get(col, True):
                    norm = 1 - norm
            else:
                raise ValueError(f"Método {metodo} no implementado")

            df_norm[col] = norm
        return df_norm

    def on_run(b):
        with run_out:
            clear_output()
            df = L2["df"]
            if df is None:
                print("❌ Cargue un archivo primero.")
                return
            criterios = list(col_crit.value)
            if not criterios:
                print("❌ Seleccione al menos un criterio.")
                return
            for c in criterios:
                if c not in L2["tipos"]:
                    L2["tipos"][c] = True
            df_c = df[criterios].apply(pd.to_numeric, errors="coerce").dropna(how="all")
            if df_c.isnull().any().any():
                print("⚠️ Algunos valores no son numéricos y se reemplazaron con NaN. Revise sus datos.")
            L2["df_criterios"] = df_c

            metodo = metodo_norm.value
            df_norm = normalizar(df_c, metodo, L2["tipos"])
            L2["normalizado"] = df_norm

            display(HTML(f"<b>Matriz normalizada – Método: {metodo}</b>"))
            display(df_norm.round(4))
            dl_btn.layout.display = ""

    run_btn.on_click(on_run)

    def on_download(b):
        with dl_out:
            clear_output()
            if L2["normalizado"] is None:
                print("❌ Primero ejecute la normalización.")
                return
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                L2["df_criterios"].round(4).to_excel(writer, sheet_name="Originales", startrow=2)
                L2["normalizado"].round(4).to_excel(writer, sheet_name="Normalizados", startrow=2)
                ws1 = writer.sheets["Originales"]
                ws1.cell(row=1, column=1, value="DATOS ORIGINALES")
                ws2 = writer.sheets["Normalizados"]
                ws2.cell(row=1, column=1, value=f"NORMALIZADOS – Método: {metodo_norm.value}")
            buf.seek(0)
            b64 = base64.b64encode(buf.getvalue()).decode()
            display(HTML(f'<a download="normalizacion.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">⬇ Descargar normalizacion.xlsx</a>'))

    dl_btn.on_click(on_download)

    display(widgets.HTML("<h4>1. Cargar archivo</h4>"))
    display(upload, upload_out)
    display(widgets.HTML("<h4>2. Seleccionar criterios</h4>"))
    display(col_crit)
    display(widgets.HTML("<h4>3. Definir tipo de cada criterio (Beneficio/Costo)</h4>"))
    display(tipo_criterios)
    display(widgets.HTML("<h4>4. Elegir método de normalización</h4>"))
    display(metodo_norm)
    display(run_btn, run_out)
    display(dl_btn, dl_out)


# ============================================================
# LÍNEA 3 - PONDERACIÓN (8 métodos: Igual, RS, CRITIC, Entropía, AHP, Varianza, Promedio, Personalizada)
# ============================================================
def run_ponderacion():
    """Ejecuta análisis de ponderación multicriterio"""
    display(widgets.HTML("<h3>⚖️ LÍNEA 3 – Ponderación</h3>"))

    L3 = {"df": None, "df_normalizado": None, "pesos": None}

    upload = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                description="📂 Subir archivo", button_style="primary")
    upload_out = widgets.Output()
    col_crit = widgets.SelectMultiple(description="Criterios:",
                                      layout=widgets.Layout(height="140px", width="380px"))
    metodo_pond = widgets.Dropdown(
        description="Método:",
        options=["Igual", "RS (Rank Sum)", "CRITIC", "Entropía", "AHP", "Varianza", "Promedio", "Personalizada"],
        value="Igual"
    )
    # Widgets adicionales según método
    ahp_matrix_area = widgets.Output()  # para ingresar matriz AHP
    personalizado_sliders = widgets.VBox([])
    run_btn = widgets.Button(description="▶ Calcular pesos", button_style="success")
    run_out = widgets.Output()
    dl_btn = widgets.Button(description="⬇ Descargar Excel", button_style="info")
    dl_btn.layout.display = "none"
    dl_out = widgets.Output()

    def on_file_upload(change):
        with upload_out:
            clear_output()
            if not upload.value:
                return
            key = list(upload.value.keys())[0]
            fdata = upload.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L3["df"] = df
                cols = list(df.columns)
                col_crit.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload.observe(on_file_upload, names="value")

    def actualizar_widgets_metodo(*args):
        metodo = metodo_pond.value
        criterios = list(col_crit.value)
        if metodo == "AHP":
            with ahp_matrix_area:
                clear_output()
                display(HTML("<b>Ingrese matriz de comparación por pares (tamaño {})</b>".format(len(criterios))))
                # Crear una matriz de entry widgets
                entries = []
                for i in range(len(criterios)):
                    row = []
                    for j in range(len(criterios)):
                        if i == j:
                            val = widgets.FloatText(value=1.0, disabled=True, layout=widgets.Layout(width="70px"))
                        else:
                            val = widgets.FloatText(value=1.0, layout=widgets.Layout(width="70px"))
                        row.append(val)
                    entries.append(row)
                ahp_matrix_area.entries = entries
                # Mostrar tabla
                grid = widgets.GridBox(children=[w for row in entries for w in row],
                                       layout=widgets.Layout(grid_template_columns=f"repeat({len(criterios)}, 80px)"))
                display(grid)
        elif metodo == "Personalizada":
            personalizado_sliders.children = [widgets.FloatSlider(value=1.0/len(criterios), min=0, max=1, step=0.01,
                                                                   description=c, continuous_update=False,
                                                                   layout=widgets.Layout(width="400px"))
                                              for c in criterios]
            display(personalizado_sliders)

    metodo_pond.observe(actualizar_widgets_metodo, names="value")
    col_crit.observe(actualizar_widgets_metodo, names="value")

    def calcular_pesos(df_norm, metodo, criterios, ahp_matrix=None, pesos_personalizados=None):
        n = len(criterios)
        if metodo == "Igual":
            pesos = np.ones(n) / n
        elif metodo == "RS (Rank Sum)":
            # Asignar ranking (1 = más importante, n = menos importante) - aquí se pide al usuario
            # Simplificado: usamos rangos iguales (todos 1) -> pesos iguales
            # En una versión más completa se pediría el orden
            rangos = np.arange(1, n+1)[::-1]  # inverso: el primero más importante
            pesos = rangos / rangos.sum()
        elif metodo == "CRITIC":
            # Normalizar y calcular desviación estándar y correlaciones
            stds = df_norm.std()
            corr = df_norm.corr()
            conflict = np.sum(1 - corr, axis=1)
            info = stds * conflict
            pesos = info / info.sum()
        elif metodo == "Entropía":
            # Normalización adicional (suma=1 por columna)
            p = df_norm / df_norm.sum()
            with np.errstate(divide='ignore'):
                e = - (p * np.log(p)).sum() / np.log(len(df_norm))
            d = 1 - e
            pesos = d / d.sum()
        elif metodo == "AHP":
            if ahp_matrix is None:
                pesos = np.ones(n) / n
            else:
                # Calcular autovector principal
                mat = np.array(ahp_matrix)
                eigvals, eigvecs = np.linalg.eig(mat)
                principal = eigvecs[:, np.argmax(eigvals.real)]
                pesos = principal.real / principal.real.sum()
        elif metodo == "Varianza":
            vars_ = df_norm.var()
            pesos = vars_ / vars_.sum()
        elif metodo == "Promedio":
            pesos = df_norm.mean() / df_norm.mean().sum()
        elif metodo == "Personalizada":
            if pesos_personalizados is not None:
                pesos = np.array(pesos_personalizados) / sum(pesos_personalizados)
            else:
                pesos = np.ones(n) / n
        else:
            pesos = np.ones(n) / n
        return pd.Series(pesos, index=criterios)

    def on_run(b):
        with run_out:
            clear_output()
            df = L3["df"]
            if df is None:
                print("❌ Cargue un archivo primero.")
                return
            criterios = list(col_crit.value)
            if not criterios:
                print("❌ Seleccione al menos un criterio.")
                return
            # Se espera que los datos ya estén normalizados (idealmente desde run_normalizacion)
            # Por simplicidad, normalizamos con Min-Max beneficio
            df_c = df[criterios].apply(pd.to_numeric, errors="coerce")
            # Normalización simple Min-Max
            df_norm = (df_c - df_c.min()) / (df_c.max() - df_c.min())
            L3["df_normalizado"] = df_norm

            metodo = metodo_pond.value
            ahp_mat = None
            if metodo == "AHP" and hasattr(ahp_matrix_area, "entries"):
                entries = ahp_matrix_area.entries
                sz = len(criterios)
                ahp_mat = np.ones((sz, sz))
                for i in range(sz):
                    for j in range(sz):
                        if i != j:
                            ahp_mat[i, j] = entries[i][j].value
                            ahp_mat[j, i] = 1.0 / entries[i][j].value
            pesos_personal = None
            if metodo == "Personalizada" and personalizado_sliders.children:
                pesos_personal = [s.value for s in personalizado_sliders.children]

            pesos = calcular_pesos(df_norm, metodo, criterios, ahp_mat, pesos_personal)
            L3["pesos"] = pesos
            display(HTML(f"<b>Pesos calculados – Método: {metodo}</b>"))
            df_pesos = pd.DataFrame(pesos).T
            display(df_pesos.round(4))
            dl_btn.layout.display = ""

    run_btn.on_click(on_run)

    def on_download(b):
        with dl_out:
            clear_output()
            if L3["pesos"] is None:
                print("❌ Primero calcule los pesos.")
                return
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                pd.DataFrame(L3["pesos"]).T.to_excel(writer, sheet_name="Pesos", startrow=2)
                ws = writer.sheets["Pesos"]
                ws.cell(row=1, column=1, value=f"PESOS – Método: {metodo_pond.value}")
            buf.seek(0)
            b64 = base64.b64encode(buf.getvalue()).decode()
            display(HTML(f'<a download="ponderacion.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">⬇ Descargar ponderacion.xlsx</a>'))

    dl_btn.on_click(on_download)

    display(widgets.HTML("<h4>1. Cargar archivo con datos</h4>"))
    display(upload, upload_out)
    display(widgets.HTML("<h4>2. Seleccionar criterios</h4>"))
    display(col_crit)
    display(widgets.HTML("<h4>3. Método de ponderación</h4>"))
    display(metodo_pond)
    display(ahp_matrix_area)
    display(run_btn, run_out)
    display(dl_btn, dl_out)


# ============================================================
# LÍNEA 4 - AGREGACIÓN (Suma Ponderada y Media Geométrica)
# ============================================================
def run_agregacion():
    """Ejecuta agregación multicriterio (Suma Ponderada y Media Geométrica)"""
    display(widgets.HTML("<h3>📊 LÍNEA 4 – Agregación</h3>"))

    L4 = {"df": None, "pesos": None, "resultados": None}

    upload = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                description="📂 Subir matriz normalizada", button_style="primary")
    upload_out = widgets.Output()
    upload_pesos = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                      description="📂 Subir pesos (opcional)", button_style="primary")
    pesos_out = widgets.Output()
    metodo_agr = widgets.Dropdown(description="Método:", options=["Suma Ponderada", "Media Geométrica Ponderada"])
    run_btn = widgets.Button(description="▶ Agregar", button_style="success")
    run_out = widgets.Output()
    dl_btn = widgets.Button(description="⬇ Descargar Excel", button_style="info")
    dl_btn.layout.display = "none"
    dl_out = widgets.Output()

    def on_upload_matriz(change):
        with upload_out:
            clear_output()
            if not upload.value:
                return
            key = list(upload.value.keys())[0]
            fdata = upload.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L4["df"] = df
                print(f"✅ Matriz cargada: {df.shape[0]} alternativas × {df.shape[1]} criterios")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload.observe(on_upload_matriz, names="value")

    def on_upload_pesos(change):
        with pesos_out:
            clear_output()
            if not upload_pesos.value:
                return
            key = list(upload_pesos.value.keys())[0]
            fdata = upload_pesos.value[key]["content"]
            try:
                dfp = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                # Se espera que los pesos estén en una fila o columna
                if dfp.shape[0] == 1:
                    pesos = dfp.iloc[0].values
                elif dfp.shape[1] == 1:
                    pesos = dfp.iloc[:,0].values
                else:
                    pesos = dfp.values.flatten()
                L4["pesos"] = pesos
                print(f"✅ Pesos cargados: {pesos}")
            except Exception as e:
                print(f"❌ Error al cargar pesos: {e}")

    upload_pesos.observe(on_upload_pesos, names="value")

    def on_run(b):
        with run_out:
            clear_output()
            df = L4["df"]
            if df is None:
                print("❌ Cargue la matriz normalizada.")
                return
            # Si no hay pesos, usar pesos iguales
            if L4["pesos"] is None:
                n_crit = df.shape[1]
                pesos = np.ones(n_crit) / n_crit
                print("⚠️ No se cargaron pesos. Se usarán pesos iguales.")
            else:
                pesos = L4["pesos"]
                if len(pesos) != df.shape[1]:
                    print(f"❌ La longitud de pesos ({len(pesos)}) no coincide con el número de criterios ({df.shape[1]}).")
                    return

            metodo = metodo_agr.value
            if metodo == "Suma Ponderada":
                resultados = df.dot(pesos)
            else:  # Media Geométrica Ponderada
                # Elevar cada valor al peso y luego producto fila
                resultados = (df ** pesos).prod(axis=1) ** (1 / pesos.sum())
            L4["resultados"] = resultados
            df_res = pd.DataFrame({"Alternativa": df.index, "Puntuación": resultados})
            display(HTML(f"<b>Resultados – {metodo}</b>"))
            display(df_res.sort_values("Puntuación", ascending=False).round(4))
            dl_btn.layout.display = ""

    run_btn.on_click(on_run)

    def on_download(b):
        with dl_out:
            clear_output()
            if L4["resultados"] is None:
                print("❌ Primero ejecute la agregación.")
                return
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_res = pd.DataFrame({"Alternativa": L4["df"].index, "Puntuación": L4["resultados"]})
                df_res.to_excel(writer, sheet_name="Agregacion", index=False)
                ws = writer.sheets["Agregacion"]
                ws.cell(row=1, column=1, value=f"AGREGACIÓN – {metodo_agr.value}")
            buf.seek(0)
            b64 = base64.b64encode(buf.getvalue()).decode()
            display(HTML(f'<a download="agregacion.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">⬇ Descargar agregacion.xlsx</a>'))

    dl_btn.on_click(on_download)

    display(widgets.HTML("<h4>1. Cargar matriz normalizada (alternativas × criterios)</h4>"))
    display(upload, upload_out)
    display(widgets.HTML("<h4>2. (Opcional) Cargar archivo con pesos</h4>"))
    display(upload_pesos, pesos_out)
    display(widgets.HTML("<h4>3. Método de agregación</h4>"))
    display(metodo_agr)
    display(run_btn, run_out)
    display(dl_btn, dl_out)


# ============================================================
# LÍNEA 5 - TOPSIS (4 distancias: Euclidiana, Manhattan, Chebyshev, Minkowski)
# ============================================================
def run_topsis():
    """Ejecuta TOPSIS con 4 funciones de distancia"""
    display(widgets.HTML("<h3>📊 LÍNEA 5 – TOPSIS</h3>"))

    L5 = {"df": None, "pesos": None, "tipos": None, "resultados": None}

    upload = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                description="📂 Subir matriz de decisión", button_style="primary")
    upload_out = widgets.Output()
    col_crit = widgets.SelectMultiple(description="Criterios:", layout=widgets.Layout(height="140px"))
    upload_pesos = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                      description="📂 Cargar pesos", button_style="primary")
    pesos_out = widgets.Output()
    distancia = widgets.Dropdown(description="Distancia:", options=["Euclidiana", "Manhattan", "Chebyshev", "Minkowski (p=3)"])
    run_btn = widgets.Button(description="▶ Ejecutar TOPSIS", button_style="success")
    run_out = widgets.Output()
    dl_btn = widgets.Button(description="⬇ Descargar Excel", button_style="info")
    dl_btn.layout.display = "none"
    dl_out = widgets.Output()

    # Definir tipos de criterio (beneficio/costo) mediante botones
    tipo_criterios_widget = widgets.VBox([])

    def on_file_upload(change):
        with upload_out:
            clear_output()
            if not upload.value:
                return
            key = list(upload.value.keys())[0]
            fdata = upload.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L5["df"] = df
                cols = list(df.columns)
                col_crit.options = cols
                # Crear botones de tipo
                children = []
                for c in cols:
                    btn = widgets.ToggleButton(value=True, description=f"{c}: Beneficio")
                    children.append(btn)
                tipo_criterios_widget.children = children
                print(f"✅ {key}  |  {df.shape}")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload.observe(on_file_upload, names="value")

    def on_pesos_upload(change):
        with pesos_out:
            clear_output()
            if not upload_pesos.value:
                return
            key = list(upload_pesos.value.keys())[0]
            fdata = upload_pesos.value[key]["content"]
            try:
                dfp = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                if dfp.shape[0] == 1:
                    pesos = dfp.iloc[0].values
                elif dfp.shape[1] == 1:
                    pesos = dfp.iloc[:,0].values
                else:
                    pesos = dfp.values.flatten()
                L5["pesos"] = pesos
                print(f"✅ Pesos cargados: {pesos}")
            except Exception as e:
                print(f"❌ Error: {e}")

    upload_pesos.observe(on_pesos_upload, names="value")

    def topsis(df, pesos, tipos, dist_metrica):
        # Normalización vectorial
        norm = df / np.sqrt((df**2).sum())
        # Ponderación
        norm_pond = norm * pesos
        # Soluciones ideal y anti-ideal
        ideal_pos = []
        ideal_neg = []
        for i, col in enumerate(df.columns):
            if tipos[i]:  # beneficio
                ideal_pos.append(norm_pond[col].max())
                ideal_neg.append(norm_pond[col].min())
            else:  # costo
                ideal_pos.append(norm_pond[col].min())
                ideal_neg.append(norm_pond[col].max())
        # Distancias
        d_pos = []
        d_neg = []
        for idx, row in norm_pond.iterrows():
            if dist_metrica == "Euclidiana":
                d_pos.append(np.sqrt(((row - ideal_pos)**2).sum()))
                d_neg.append(np.sqrt(((row - ideal_neg)**2).sum()))
            elif dist_metrica == "Manhattan":
                d_pos.append(np.abs(row - ideal_pos).sum())
                d_neg.append(np.abs(row - ideal_neg).sum())
            elif dist_metrica == "Chebyshev":
                d_pos.append(np.max(np.abs(row - ideal_pos)))
                d_neg.append(np.max(np.abs(row - ideal_neg)))
            elif dist_metrica.startswith("Minkowski"):
                p = 3
                d_pos.append((np.abs(row - ideal_pos)**p).sum()**(1/p))
                d_neg.append((np.abs(row - ideal_neg)**p).sum()**(1/p))
        d_pos = np.array(d_pos)
        d_neg = np.array(d_neg)
        # Índice de desempeño
        C = d_neg / (d_pos + d_neg)
        return C, norm_pond, ideal_pos, ideal_neg

    def on_run(b):
        with run_out:
            clear_output()
            df = L5["df"]
            if df is None:
                print("❌ Cargue la matriz de decisión.")
                return
            criterios = list(col_crit.value)
            if not criterios:
                print("❌ Seleccione los criterios.")
                return
            # Tipos
            tipos = [w.value for w in tipo_criterios_widget.children]
            if len(tipos) != len(criterios):
                print("❌ Número de criterios no coincide con tipos.")
                return
            # Pesos
            if L5["pesos"] is None:
                pesos = np.ones(len(criterios)) / len(criterios)
                print("⚠️ No se cargaron pesos. Usando pesos iguales.")
            else:
                pesos = L5["pesos"]
                if len(pesos) != len(criterios):
                    print(f"❌ Número de pesos ({len(pesos)}) diferente a criterios ({len(criterios)}).")
                    return

            df_sel = df[criterios].apply(pd.to_numeric, errors="coerce")
            C, _, _, _ = topsis(df_sel, pesos, tipos, distancia.value)
            L5["resultados"] = C
            df_res = pd.DataFrame({"Alternativa": df_sel.index, "Índice TOPSIS": C})
            display(HTML(f"<b>Resultados TOPSIS – Distancia {distancia.value}</b>"))
            display(df_res.sort_values("Índice TOPSIS", ascending=False).round(4))
            dl_btn.layout.display = ""

    run_btn.on_click(on_run)

    def on_download(b):
        with dl_out:
            clear_output()
            if L5["resultados"] is None:
                print("❌ Primero ejecute TOPSIS.")
                return
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_res = pd.DataFrame({"Alternativa": L5["df"].index, "Índice TOPSIS": L5["resultados"]})
                df_res.to_excel(writer, sheet_name="TOPSIS", index=False)
                ws = writer.sheets["TOPSIS"]
                ws.cell(row=1, column=1, value=f"TOPSIS – Distancia {distancia.value}")
            buf.seek(0)
            b64 = base64.b64encode(buf.getvalue()).decode()
            display(HTML(f'<a download="topsis.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">⬇ Descargar topsis.xlsx</a>'))

    dl_btn.on_click(on_download)

    display(widgets.HTML("<h4>1. Cargar matriz de decisión (alternativas × criterios)</h4>"))
    display(upload, upload_out)
    display(widgets.HTML("<h4>2. Seleccionar criterios y definir tipo (Beneficio/Costo)</h4>"))
    display(col_crit)
    display(tipo_criterios_widget)
    display(widgets.HTML("<h4>3. Cargar pesos (archivo con una fila o columna)</h4>"))
    display(upload_pesos, pesos_out)
    display(widgets.HTML("<h4>4. Seleccionar distancia</h4>"))
    display(distancia)
    display(run_btn, run_out)
    display(dl_btn, dl_out)


# ============================================================
# LÍNEA 6 - RIM (Rango Ideal Flexible)
# ============================================================
def run_rim():
    """Ejecuta análisis RIM (Rango Ideal Flexible)"""
    display(widgets.HTML("<h3>📊 LÍNEA 6 – RIM</h3>"))

    L6 = {"df": None, "pesos": None, "ideal": None, "antiideal": None, "resultados": None}

    upload = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                description="📂 Subir matriz normalizada", button_style="primary")
    upload_out = widgets.Output()
    upload_pesos = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                      description="📂 Cargar pesos", button_style="primary")
    pesos_out = widgets.Output()
    # Valores ideal y anti-ideal personalizables
    ideal_input = widgets.Text(description="Ideal (separado por comas):", layout=widgets.Layout(width="400px"))
    antiideal_input = widgets.Text(description="Anti-ideal:", layout=widgets.Layout(width="400px"))
    run_btn = widgets.Button(description="▶ Calcular RIM", button_style="success")
    run_out = widgets.Output()
    dl_btn = widgets.Button(description="⬇ Descargar Excel", button_style="info")
    dl_btn.layout.display = "none"
    dl_out = widgets.Output()

    def on_upload(change):
        with upload_out:
            clear_output()
            if not upload.value:
                return
            key = list(upload.value.keys())[0]
            fdata = upload.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L6["df"] = df
                print(f"✅ Matriz cargada: {df.shape}")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload.observe(on_upload, names="value")

    def on_pesos(change):
        with pesos_out:
            clear_output()
            if not upload_pesos.value:
                return
            key = list(upload_pesos.value.keys())[0]
            fdata = upload_pesos.value[key]["content"]
            try:
                dfp = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                if dfp.shape[0] == 1:
                    pesos = dfp.iloc[0].values
                else:
                    pesos = dfp.iloc[:,0].values
                L6["pesos"] = pesos
                print(f"✅ Pesos cargados: {pesos}")
            except Exception as e:
                print(f"❌ Error: {e}")

    upload_pesos.observe(on_pesos, names="value")

    def on_run(b):
        with run_out:
            clear_output()
            df = L6["df"]
            if df is None:
                print("❌ Cargue la matriz normalizada.")
                return
            if L6["pesos"] is None:
                pesos = np.ones(df.shape[1]) / df.shape[1]
                print("⚠️ Usando pesos iguales.")
            else:
                pesos = L6["pesos"]
                if len(pesos) != df.shape[1]:
                    print(f"❌ Número de pesos ({len(pesos)}) no coincide con criterios ({df.shape[1]}).")
                    return

            # Determinar ideal y anti-ideal
            if ideal_input.value.strip():
                try:
                    ideal = np.array([float(x) for x in ideal_input.value.split(",")])
                except:
                    ideal = df.max().values
                    print("⚠️ Ideal inválido. Usando máximos por criterio.")
            else:
                ideal = df.max().values

            if antiideal_input.value.strip():
                try:
                    antiideal = np.array([float(x) for x in antiideal_input.value.split(",")])
                except:
                    antiideal = df.min().values
                    print("⚠️ Anti-ideal inválido. Usando mínimos.")
            else:
                antiideal = df.min().values

            # Distancia euclidiana ponderada al ideal y anti-ideal
            d_ideal = np.sqrt(((df - ideal)**2 * pesos).sum(axis=1))
            d_anti = np.sqrt(((df - antiideal)**2 * pesos).sum(axis=1))
            # Índice RIM
            C = d_anti / (d_ideal + d_anti)
            L6["resultados"] = C
            df_res = pd.DataFrame({"Alternativa": df.index, "Índice RIM": C})
            display(HTML("<b>Resultados RIM</b>"))
            display(df_res.sort_values("Índice RIM", ascending=False).round(4))
            dl_btn.layout.display = ""

    run_btn.on_click(on_run)

    def on_download(b):
        with dl_out:
            clear_output()
            if L6["resultados"] is None:
                print("❌ Primero ejecute RIM.")
                return
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_res = pd.DataFrame({"Alternativa": L6["df"].index, "Índice RIM": L6["resultados"]})
                df_res.to_excel(writer, sheet_name="RIM", index=False)
                ws = writer.sheets["RIM"]
                ws.cell(row=1, column=1, value="RIM – Rango Ideal Flexible")
            buf.seek(0)
            b64 = base64.b64encode(buf.getvalue()).decode()
            display(HTML(f'<a download="rim.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">⬇ Descargar rim.xlsx</a>'))

    dl_btn.on_click(on_download)

    display(widgets.HTML("<h4>1. Cargar matriz normalizada (alternativas × criterios)</h4>"))
    display(upload, upload_out)
    display(widgets.HTML("<h4>2. Cargar pesos (opcional)</h4>"))
    display(upload_pesos, pesos_out)
    display(widgets.HTML("<h4>3. (Opcional) Definir Ideal y Anti-ideal (separados por comas)</h4>"))
    display(ideal_input, antiideal_input)
    display(run_btn, run_out)
    display(dl_btn, dl_out)


__all__ = [
    'run_estadistica',
    'run_normalizacion',
    'run_ponderacion',
    'run_agregacion',
    'run_topsis',
    'run_rim'
]
