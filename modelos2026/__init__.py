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
            if df is None: print("❌ Cargá un archivo primero."); return
            crit_cols = list(col_crit1.value)
            if not crit_cols: print("❌ Seleccioná al menos un criterio."); return
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
            plt.tight_layout(); plt.show()
            # Histogramas
            display(HTML("<b>Histogramas</b>"))
            fig2, axes2 = plt.subplots(1, n_crit, figsize=(max(4*n_crit, 6), 4), squeeze=False)
            for idx, col in enumerate(crit_cols):
                ax = axes2[0][idx]
                ax.hist(df_c[col].dropna(), bins="auto", color=colors[idx % 10],
                        edgecolor="white", alpha=0.85)
                ax.set_title(col, fontsize=11, fontweight="bold")
                ax.set_xlabel("Valor", fontsize=9); ax.set_ylabel("Frecuencia", fontsize=9)
                ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.4f"))
                ax.grid(axis="y", linestyle="--", alpha=0.4)
            plt.suptitle("Histogramas por criterio", fontsize=13, fontweight="bold", y=1.01)
            plt.tight_layout(); plt.show()
            dl1_btn.layout.display = ""

    run1_btn.on_click(_run1)

    def _download1(b):
        with dl1_out:
            clear_output()
            df_stats = L1.get("df_stats")
            df_c     = L1.get("df_criterios")
            corr_mat = L1.get("corr_matrix")
            if df_stats is None: print("❌ Calculá primero."); return
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
    import numpy as np
    import pandas as pd
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    import io, base64, warnings
    warnings.filterwarnings("ignore")
    pd.options.display.float_format = '{:.4f}'.format

    def _norm_fraccion_max(df):
        return df.div(df.max())

    def _norm_fraccion_suma(df):
        return df.div(df.sum())

    def _norm_fraccion_rango(df):
        rango = df.max() - df.min()
        return (df - df.min()).div(rango.replace(0, np.nan))

    def _norm_vector(df):
        return df.div(np.sqrt((df**2).sum()))

    def _norm_zscore(df):
        return (df - df.mean()) / df.std(ddof=1)

    def _norm_ideal_ref(df, metas_rim):
        result = df.copy()
        for col in df.columns:
            c, d = metas_rim[col]
            a = df[col].min()
            b = df[col].max()
            x = df[col].values
            v = np.where(x < c,
                         np.maximum(0, (x - a) / (c - a)) if c != a else 0,
                         np.where(x <= d,
                                  1.0,
                                  np.maximum(0, (b - x) / (b - d)) if b != d else 0))
            result[col] = v
        return result

    NORM_METODOS = {
        "Fracción del máximo":  _norm_fraccion_max,
        "Fracción de la suma":  _norm_fraccion_suma,
        "Fracción del rango":   _norm_fraccion_rango,
        "Del vector":           _norm_vector,
        "Z-score":              _norm_zscore,
        "Ideal de referencia":  None,
        "(Sin normalizar)":     lambda df: df.copy(),
    }

    L2 = {"df": None, "df_norm": None, "df_show": None}

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

    upload2     = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                      description="📂 Subir archivo", button_style="primary")
    upload2_out = widgets.Output()
    col_alt2    = widgets.Dropdown(description="Alternativas:", options=[],
                                    style={"description_width":"110px"},
                                    layout=widgets.Layout(width="320px"))
    col_crit2   = widgets.SelectMultiple(description="Criterios:", options=[],
                                          layout=widgets.Layout(height="140px", width="380px"),
                                          style={"description_width":"80px"})
    norm_method2 = widgets.Dropdown(
        description="Normalización:",
        options=list(NORM_METODOS.keys()),
        value="Fracción de la suma",
        style={"description_width":"120px"},
        layout=widgets.Layout(width="360px"))
    run2_btn    = widgets.Button(description="▶ Normalizar", button_style="success",
                                  layout=widgets.Layout(width="200px"))
    run2_out    = widgets.Output()
    dl2_btn     = widgets.Button(description="⬇ Descargar matriz normalizada",
                                  button_style="info",
                                  layout=widgets.Layout(width="270px"))
    dl2_btn.layout.display = "none"
    dl2_out     = widgets.Output()

    rim_box = widgets.VBox([])
    rim_inputs = {}

    def _crear_rim_inputs(criterios):
        nonlocal rim_inputs
        children = []
        rim_inputs = {}
        for crit in criterios:
            if L2["df"] is not None and crit in L2["df"].columns:
                col_data = L2["df"][crit].dropna()
                sugerido_c = col_data.quantile(0.75) if len(col_data) else 0.0
                sugerido_d = col_data.max() if len(col_data) else 0.0
            else:
                sugerido_c, sugerido_d = 0.0, 1.0
            w_c = widgets.BoundedFloatText(value=round(sugerido_c, 4),
                                           min=-1e6, max=1e6, step=0.01,
                                           description=f'{crit[:15]} C:',
                                           layout=widgets.Layout(width='280px'))
            w_d = widgets.BoundedFloatText(value=round(sugerido_d, 4),
                                           min=-1e6, max=1e6, step=0.01,
                                           description='D:',
                                           layout=widgets.Layout(width='280px'))
            rim_inputs[crit] = (w_c, w_d)
            children.append(widgets.HBox([w_c, w_d]))
        rim_box.children = children

    def _actualizar_visibilidad_rim(*args):
        if norm_method2.value == "Ideal de referencia":
            _crear_rim_inputs(col_crit2.value)
            rim_box.layout.display = ""
        else:
            rim_box.layout.display = "none"

    norm_method2.observe(_actualizar_visibilidad_rim, names="value")
    col_crit2.observe(_actualizar_visibilidad_rim, names="value")

    def _descargar_enlace(df, nombre_archivo, titulo_hoja, metodo):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.round(4).to_excel(writer, sheet_name=titulo_hoja, index=False, startrow=2)
            ws = writer.sheets[titulo_hoja]
            ws.cell(row=1, column=1,
                    value=f"{titulo_hoja.upper()} – Método: {metodo} | Modelos de Decisión | Unidad 3")
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return HTML(f'<a download="{nombre_archivo}" '
                    f'href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">'
                    f'⬇ Descargar {nombre_archivo}</a>')

    def _load2(change):
        with upload2_out:
            clear_output()
            if not upload2.value: return
            key = list(upload2.value.keys())[0]
            fdata = upload2.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L2["df"] = df
                cols = list(df.columns)
                col_alt2.options = cols
                col_crit2.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
                _actualizar_visibilidad_rim()
            except Exception as e:
                print(f"❌ Error: {e}")

    upload2.observe(_load2, names="value")

    def _run2(b):
        with run2_out:
            clear_output()
            df = L2["df"]
            if df is None: print("❌ Cargá un archivo primero."); return
            crit_cols = list(col_crit2.value)
            if not crit_cols: print("❌ Seleccioná al menos un criterio."); return
            metodo = norm_method2.value

            df_c = df[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

            alt_col = col_alt2.value
            if alt_col and alt_col in df.columns:
                df_show = df_c.copy()
                df_show.insert(0, alt_col, df[alt_col].values)
            else:
                df_show = df_c.copy()

            try:
                if metodo == "Ideal de referencia":
                    rim_dict = {}
                    for crit in crit_cols:
                        wc, wd = rim_inputs[crit]
                        rim_dict[crit] = (wc.value, wd.value)
                    df_norm = _norm_ideal_ref(df_c, rim_dict)
                else:
                    df_norm = NORM_METODOS[metodo](df_c)
            except Exception as e:
                print(f"❌ Error al normalizar: {e}"); return

            if alt_col and alt_col in df.columns:
                df_norm_show = df_norm.copy()
                df_norm_show.insert(0, alt_col, df[alt_col].values)
            else:
                df_norm_show = df_norm.copy()

            L2["df_norm"] = df_norm
            L2["df_show"] = df_norm_show

            display(HTML(f"<b>🔢 Matriz Normalizada – {metodo}</b>"))
            display(df_norm_show.round(4))
            dl2_btn.layout.display = ""

    run2_btn.on_click(_run2)

    def _download2(b):
        with dl2_out:
            clear_output()
            df_show = L2.get("df_show")
            if df_show is None: print("❌ Normalizá primero."); return
            metodo = norm_method2.value
            display(_descargar_enlace(df_show, "matriz_normalizada.xlsx",
                                      "Normalizada", metodo))

    dl2_btn.on_click(_download2)

    display(widgets.HTML("<h3>🔢 LÍNEA 2 – Normalización</h3>"))
    display(widgets.HTML("""
    <div style="background-color: #fff3cd; border-left: 4px solid #ff9800; padding: 12px; margin: 10px 0; border-radius: 4px;">
        <p style="margin: 5px 0; font-weight: bold; color: #d32f2f;">📋 IMPORTANTE – Preparación de datos:</p>
        <ul style="margin: 8px 0; padding-left: 20px; color: #333;">
            <li><strong>Cargar planillas con datos ya transformados</strong></li>
            <li><strong>Mínimos ya convertidos a máximos</strong></li>
            <li><strong>Valores no negativos</strong></li>
        </ul>
    </div>
    """))
    display(_sep("1. Cargar archivo"))
    display(upload2, upload2_out)
    display(_sep("2. Seleccionar columnas"))
    display(widgets.HBox([col_alt2, col_crit2]))
    display(_sep("3. Elegir método de normalización"))
    display(norm_method2)
    display(_sep("Parámetros para Ideal de referencia (RIM)"))
    display(rim_box)
    display(_sep("4. Normalizar"))
    display(run2_btn, run2_out)
    display(dl2_btn, dl2_out)


# ============================================================
# LÍNEA 3 - PONDERACIÓN
# ============================================================
def run_ponderacion():
    """Ejecuta análisis de ponderación"""
    import numpy as np
    import pandas as pd
    from itertools import combinations
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    import warnings
    warnings.filterwarnings("ignore")
    pd.options.display.float_format = '{:.4f}'.format

    L3 = {"df": None}

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

    # ------------------------------ Funciones de ponderación ------------------------------
    def pesos_uniformes(df, **kw):
        n = df.shape[1]
        return pd.Series({c: 1/n for c in df.columns})

    def pesos_desv_estandar(df, **kw):
        s = df.std(ddof=0); return s / s.sum()

    def pesos_coef_variacion(df, **kw):
        cv = df.std(ddof=0).abs() / df.mean().abs().replace(0, np.nan)
        cv = cv.fillna(0); tot = cv.sum()
        return cv / tot if tot != 0 else pd.Series({c: np.nan for c in df.columns})

    def pesos_entropia(df, **kw):
        r = df.div(df.sum()).fillna(0)
        r_safe = r.replace(0, 1e-12)
        m = r.shape[0]; k = 1 / np.log(m) if m > 1 else 1
        ej = -k * (r_safe * np.log(r_safe)).sum()
        dj = 1 - ej; tot = dj.sum()
        return dj / tot if tot != 0 else pd.Series({c: np.nan for c in df.columns})

    def pesos_critic(df, **kw):
        r_norm = (df - df.min()) / (df.max() - df.min()).replace(0, np.nan)
        r_norm = r_norm.fillna(0); s = r_norm.std(ddof=0); corr = r_norm.corr()
        wj = {j: s[j] * sum(1 - corr.loc[j, k] for k in df.columns) for j in df.columns}
        w = pd.Series(wj); tot = w.sum()
        return w / tot if tot != 0 else pd.Series({c: np.nan for c in df.columns})

    def pesos_ordenacion_simple(df, orden=None, **kw):
        if orden is None: orden = {c: i+1 for i, c in enumerate(df.columns)}
        s = pd.Series(orden); tot = s.sum()
        return s / tot if tot != 0 else pd.Series({c: np.nan for c in df.columns})

    def pesos_tasacion_simple(df, puntuaciones=None, **kw):
        if puntuaciones is None: puntuaciones = {c: 1 for c in df.columns}
        s = pd.Series(puntuaciones); tot = s.sum()
        return s / tot if tot != 0 else pd.Series({c: np.nan for c in df.columns})

    def pesos_ahp(df, matriz_comparacion=None, **kw):
        cols = list(df.columns); n = len(cols)
        M = matriz_comparacion if matriz_comparacion is not None else pd.DataFrame(np.ones((n, n)), index=cols, columns=cols)
        M_norm = M.div(M.sum()); w = M_norm.mean(axis=1)
        return w / w.sum()

    PONDERACIONES3 = {
        "Uniforme":             pesos_uniformes,
        "Desviación estándar":  pesos_desv_estandar,
        "Coef. de variación":   pesos_coef_variacion,
        "Entropía":             pesos_entropia,
        "CRITIC":               pesos_critic,
        "Ordenación simple":    pesos_ordenacion_simple,
        "Tasación simple":      pesos_tasacion_simple,
        "AHP":                  pesos_ahp,
    }

    # ------------------------------ Normalizaciones ------------------------------
    def _norm_fraccion_max(df): return df.div(df.max())
    def _norm_fraccion_suma(df): return df.div(df.sum())
    def _norm_fraccion_rango(df):
        rango = df.max() - df.min()
        return (df - df.min()).div(rango.replace(0, np.nan))
    def _norm_vector(df): return df.div(np.sqrt((df**2).sum()))
    def _norm_zscore(df): return (df - df.mean()) / df.std(ddof=0)
    def _norm_ideal_ref(df, metas_rim):
        result = df.copy()
        for col in df.columns:
            c, d = metas_rim[col]
            a = df[col].min()
            b = df[col].max()
            x = df[col].values
            v = np.where(x < c,
                         np.maximum(0, (x - a) / (c - a)) if c != a else 0,
                         np.where(x <= d,
                                  1.0,
                                  np.maximum(0, (b - x) / (b - d)) if b != d else 0))
            result[col] = v
        return result

    NORM_FUNC3 = {
        "(Sin normalizar)":     lambda d: d.copy(),
        "Fracción del máximo":  _norm_fraccion_max,
        "Fracción de la suma":  _norm_fraccion_suma,
        "Fracción del rango":   _norm_fraccion_rango,
        "Del vector":           _norm_vector,
        "Z-score":              _norm_zscore,
        "Ideal de referencia":  None,
    }

    # ------------------------------ Widgets de interfaz ------------------------------
    upload3     = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                      description="📂 Subir archivo", button_style="primary")
    upload3_out = widgets.Output()
    col_alt3    = widgets.Dropdown(description="Alternativas:", options=[],
                                    style={"description_width":"110px"},
                                    layout=widgets.Layout(width="320px"))
    col_crit3   = widgets.SelectMultiple(description="Criterios:", options=[],
                                          layout=widgets.Layout(height="140px", width="380px"),
                                          style={"description_width":"80px"})
    norm3_method = widgets.Dropdown(
        description="Normalización previa:",
        options=list(NORM_FUNC3.keys()),
        value="(Sin normalizar)",
        style={"description_width":"150px"}, layout=widgets.Layout(width="400px"))

    rim3_box = widgets.VBox([])
    rim3_inputs = {}

    pond3_select = widgets.SelectMultiple(
        options=list(PONDERACIONES3.keys()), value=["Uniforme"],
        description="Ponderaciones:",
        layout=widgets.Layout(height="200px", width="340px"),
        style={"description_width":"120px"})
    ahp3_out = widgets.Output()
    ahp3_panel = widgets.VBox([
        widgets.HTML("<b>Matriz AHP (comparaciones pareadas)</b><br>"
                     "<small>1 = igual importancia, 9 = extremadamente más importante.</small>"),
        ahp3_out])
    ahp3_panel.layout.display = "none"
    ord3_out = widgets.Output()
    ord3_panel = widgets.VBox([
        widgets.HTML("<b>Ordenación Simple – Rangos</b><br>"
                     "<small>1 = menos importante, n = más importante.</small>"),
        ord3_out])
    ord3_panel.layout.display = "none"
    tas3_out = widgets.Output()
    tas3_panel = widgets.VBox([
        widgets.HTML("<b>Tasación Simple – Puntajes</b>"),
        tas3_out])
    tas3_panel.layout.display = "none"
    run3_btn = widgets.Button(description="▶ Calcular pesos", button_style="success",
                               layout=widgets.Layout(width="200px"))
    run3_out = widgets.Output()

    def _render3_rim():
        df = L3["df"]
        crit_cols = list(col_crit3.value) if col_crit3.value else []
        if df is None or not crit_cols:
            rim3_box.children = [widgets.HTML("<small>Seleccioná criterios para definir C y D.</small>")]
            return
        nonlocal rim3_inputs
        rim3_inputs = {}
        children = []
        for crit in crit_cols:
            col_data = pd.to_numeric(df[crit], errors="coerce").dropna()
            if len(col_data) > 0:
                sugerido_c = col_data.quantile(0.75)
                sugerido_d = col_data.max()
            else:
                sugerido_c, sugerido_d = 0.0, 1.0
            w_c = widgets.BoundedFloatText(value=round(sugerido_c, 4),
                                           min=-1e6, max=1e6, step=0.01,
                                           description=f'{crit[:15]} C:',
                                           layout=widgets.Layout(width='280px'))
            w_d = widgets.BoundedFloatText(value=round(sugerido_d, 4),
                                           min=-1e6, max=1e6, step=0.01,
                                           description='D:',
                                           layout=widgets.Layout(width='280px'))
            rim3_inputs[crit] = (w_c, w_d)
            children.append(widgets.HBox([w_c, w_d]))
        rim3_box.children = children

    def _render3_ahp():
        df = L3["df"]
        if df is None or not L3.get("crit_cols"): return
        cols = L3["crit_cols"]; n = len(cols)
        sliders = {}; rows = []
        for (i, j) in combinations(range(n), 2):
            s = widgets.FloatText(value=1.0, step=0.5,
                                  description=f"{cols[i]} vs {cols[j]}:",
                                  style={"description_width":"260px"},
                                  layout=widgets.Layout(width="380px"))
            sliders[(i, j)] = s; rows.append(s)
        L3["ahp_widgets"] = (sliders, cols, n)
        with ahp3_out:
            clear_output(); display(widgets.VBox(rows))

    def _render3_ord():
        df = L3["df"]
        if df is None or not L3.get("crit_cols"): return
        cols = L3["crit_cols"]; wmap = {}; rows = []
        for c in cols:
            w = widgets.IntText(value=1, description=f"{c}:",
                                style={"description_width":"200px"},
                                layout=widgets.Layout(width="320px"))
            wmap[c] = w; rows.append(w)
        L3["ord_widgets"] = wmap
        with ord3_out:
            clear_output(); display(widgets.VBox(rows))

    def _render3_tas():
        df = L3["df"]
        if df is None or not L3.get("crit_cols"): return
        cols = L3["crit_cols"]; wmap = {}; rows = []
        for c in cols:
            w = widgets.FloatText(value=1.0, description=f"{c}:",
                                  style={"description_width":"200px"},
                                  layout=widgets.Layout(width="320px"))
            wmap[c] = w; rows.append(w)
        L3["tas_widgets"] = wmap
        with tas3_out:
            clear_output(); display(widgets.VBox(rows))

    def _update3_panels(change=None):
        sel = pond3_select.value
        ahp3_panel.layout.display = "" if "AHP" in sel else "none"
        ord3_panel.layout.display = "" if "Ordenación simple" in sel else "none"
        tas3_panel.layout.display = "" if "Tasación simple" in sel else "none"
        if norm3_method.value == "Ideal de referencia":
            _render3_rim()
            rim3_box.layout.display = ""
        else:
            rim3_box.layout.display = "none"

    pond3_select.observe(_update3_panels, names="value")
    norm3_method.observe(_update3_panels, names="value")

    def _load3(change):
        with upload3_out:
            clear_output()
            if not upload3.value: return
            key = list(upload3.value.keys())[0]
            fdata = upload3.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L3["df"] = df
                cols = list(df.columns)
                col_alt3.options = cols; col_crit3.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload3.observe(_load3, names="value")

    def _on_crit3_change(change):
        L3["crit_cols"] = list(col_crit3.value)
        _render3_ahp(); _render3_ord(); _render3_tas()
        if norm3_method.value == "Ideal de referencia":
            _render3_rim()

    col_crit3.observe(_on_crit3_change, names="value")

    def _run3(b):
        with run3_out:
            clear_output()
            df = L3["df"]
            if df is None: print("❌ Cargá un archivo primero."); return
            crit_cols = list(col_crit3.value)
            if not crit_cols: print("❌ Seleccioná al menos un criterio."); return
            ponds_sel = list(pond3_select.value)
            if not ponds_sel: print("❌ Seleccioná al menos un método de ponderación."); return
            df_c = df[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
            metodo_norm = norm3_method.value

            if metodo_norm == "Ideal de referencia":
                if not rim3_inputs:
                    print("❌ No se definieron parámetros C y D para RIM. Seleccioná 'Ideal de referencia' y completá los campos.")
                    return
                metas = {}
                for crit in crit_cols:
                    wc, wd = rim3_inputs[crit]
                    metas[crit] = (wc.value, wd.value)
                df_norm = _norm_ideal_ref(df_c, metas)
            else:
                df_norm = NORM_FUNC3[metodo_norm](df_c)
            df_norm = df_norm.fillna(0)

            display(HTML(f"<b>Matriz normalizada</b> <small>({metodo_norm})</small>"))
            alt_col = col_alt3.value
            if alt_col and alt_col in df.columns:
                display_df = df_norm.copy()
                display_df.insert(0, alt_col, df[alt_col].values)
            else:
                display_df = df_norm.copy()
            display(display_df.round(4))
            display(HTML("<hr>"))

            kwargs_extra = {}
            if "AHP" in ponds_sel and "ahp_widgets" in L3:
                sliders, cols, n = L3["ahp_widgets"]
                M = pd.DataFrame(np.ones((n, n)), index=cols, columns=cols)
                for (i, j), s in sliders.items():
                    val = s.value if s.value > 0 else 1.0
                    M.iloc[i, j] = val; M.iloc[j, i] = 1 / val
                kwargs_extra["AHP"] = {"matriz_comparacion": M}
            if "Ordenación simple" in ponds_sel and "ord_widgets" in L3:
                kwargs_extra["Ordenación simple"] = {"orden": {c: w.value for c, w in L3["ord_widgets"].items()}}
            if "Tasación simple" in ponds_sel and "tas_widgets" in L3:
                kwargs_extra["Tasación simple"] = {"puntuaciones": {c: w.value for c, w in L3["tas_widgets"].items()}}

            display(HTML(f"<b>Pesos calculados</b>"))
            rows_pesos = {}
            for met in ponds_sel:
                fn = PONDERACIONES3[met]; kw = kwargs_extra.get(met, {})
                try:
                    w = fn(df_norm, **kw)
                    rows_pesos[met] = {c: round(float(w[c]), 4) for c in crit_cols}
                except Exception as e:
                    rows_pesos[met] = {c: f"Error: {e}" for c in crit_cols}
            df_pesos = pd.DataFrame(rows_pesos).T
            df_pesos.index.name = "Método"; df_pesos.columns.name = "Criterio"
            try:
                df_pesos["∑ pesos"] = df_pesos.astype(float).sum(axis=1).round(4)
            except Exception:
                pass
            display(df_pesos)
            print("✅ Suma de pesos ≈ 1 por método (verificar columna ∑ pesos)")

    run3_btn.on_click(_run3)

    display(widgets.HTML("<h3>⚖️ LÍNEA 3 – Calculadora de Ponderaciones <small>solo muestra pesos</small></h3>"))
    display(_sep("1. Cargar archivo"))
    display(upload3, upload3_out)
    display(_sep("2. Seleccionar columnas"))
    display(widgets.HBox([col_alt3, col_crit3]))
    display(_sep("3. Normalización previa (opcional)"))
    display(norm3_method)
    display(_sep("Parámetros para Ideal de referencia (RIM)"))
    display(rim3_box)
    display(_sep("4. Elegir métodos de ponderación (Ctrl+clic para varios)"))
    display(pond3_select)
    display(_sep("5. Parámetros adicionales (si aplica)"))
    display(ahp3_panel, ord3_panel, tas3_panel)
    display(_sep("6. Calcular"))
    display(run3_btn, run3_out)


# ============================================================
# LÍNEA 4 - AGREGACIÓN (Suma Ponderada y Media Geométrica)
# ============================================================
def run_agregacion():
    """Ejecuta agregación multicriterio (Suma Ponderada y Media Geométrica)"""
    import numpy as np
    import pandas as pd
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    import io, base64, warnings
    import matplotlib.pyplot as plt
    warnings.filterwarnings("ignore")
    pd.options.display.float_format = '{:.4f}'.format

    L4 = {"df_norm": None, "df_show": None, "pesos": None, "df_agreg": None, "matriz_transform": None,
          "crit_cols": None, "alternativas": None}

    try:
        # Intenta acceder a L2 del entorno global (útil si se ejecuta en notebook)
        import __main__
        if hasattr(__main__, "L2"):
            L2 = __main__.L2
        else:
            L2 = {"df_show": None}
    except:
        L2 = {"df_show": None}

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

    def suma_ponderada(matriz, pesos):
        return matriz.dot(pesos)

    def media_geometrica_ponderada(matriz, pesos, return_matriz=True):
        n_crit = matriz.shape[1]
        matriz_potencia = np.power(matriz, pesos)
        producto = np.prod(matriz_potencia, axis=1)
        resultado = producto ** (1.0 / n_crit)
        if return_matriz:
            return resultado, matriz_potencia
        else:
            return resultado

    origen_data = widgets.RadioButtons(
        options=["📂 Cargar archivo de matriz normalizada", "📎 Usar matriz normalizada de L2"],
        value="📂 Cargar archivo de matriz normalizada",
        description="Origen de datos:",
        style={"description_width": "120px"},
        layout=widgets.Layout(width="auto")
    )

    upload4 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                  description="📂 Subir matriz normalizada", button_style="primary")
    upload4_out = widgets.Output()

    col_alt4 = widgets.Dropdown(description="Alternativas:", options=[],
                                 style={"description_width": "110px"},
                                 layout=widgets.Layout(width="320px"))
    col_crit4 = widgets.SelectMultiple(description="Criterios:", options=[],
                                        layout=widgets.Layout(height="140px", width="380px"),
                                        style={"description_width": "80px"})

    pesos_box = widgets.VBox([])
    pesos_widgets = {}

    btn_generar_pesos = widgets.Button(description="🔄 Actualizar campos de pesos",
                                       button_style="info",
                                       layout=widgets.Layout(width="250px"))

    metodo_agreg4 = widgets.Dropdown(
        options=["Suma ponderada", "Media geométrica ponderada"],
        value="Suma ponderada",
        description="Método:",
        style={"description_width": "100px"},
        layout=widgets.Layout(width="330px")
    )

    recomendaciones_agreg = widgets.HTML("""
    <div style='background-color: #2a2a2a; border-left: 4px solid #4a90e2; padding: 12px; margin-top: 8px; border-radius: 4px;'>
        <b style='color: #4a90e2;'>💡 Recomendación para Suma Ponderada:</b><br>
        <div style='margin-top: 8px; font-size: 0.95em; line-height: 1.6; color: #e0e0e0;'>
            Para criterios de <b style='color: #64b5f6;'>minimización</b>:<br>
            &nbsp;&nbsp;1. Transformar con <b>recíproca</b> (1/x)<br>
            &nbsp;&nbsp;2. Normalizar por <b>Fracción del Máximo</b>
        </div>
    </div>
    """)

    run4_btn = widgets.Button(description="▶ Calcular agregación", button_style="success",
                              layout=widgets.Layout(width="240px"))
    run4_out = widgets.Output()
    dl4_btn = widgets.Button(description="⬇ Descargar resultados", button_style="info",
                             layout=widgets.Layout(width="220px"))
    dl4_btn.layout.display = "none"
    dl4_out = widgets.Output()

    def _actualizar_campos_pesos(criterios):
        nonlocal pesos_widgets
        pesos_widgets.clear()
        n = len(criterios)
        valor_inicial = 1.0 / n if n > 0 else 0
        children = []
        for crit in criterios:
            w = widgets.FloatText(value=round(valor_inicial, 4),
                                  min=0, max=1e6, step=0.01,
                                  description=f'{crit[:30]}:',
                                  style={"description_width": "280px"},
                                  layout=widgets.Layout(width='400px'))
            pesos_widgets[crit] = w
            children.append(w)
        pesos_box.children = children

    def _on_generar_pesos_click(b):
        criterios = list(col_crit4.value)
        if not criterios:
            with run4_out:
                clear_output()
                print("⚠️ Seleccioná al menos un criterio.")
            return
        _actualizar_campos_pesos(criterios)

    btn_generar_pesos.on_click(_on_generar_pesos_click)

    def _load4(change):
        with upload4_out:
            clear_output()
            if not upload4.value: return
            key = list(upload4.value.keys())[0]
            fdata = upload4.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L4["df_norm"] = df
                cols = list(df.columns)
                col_alt4.options = cols
                col_crit4.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
                pesos_box.children = []
                pesos_widgets.clear()
            except Exception as e:
                print(f"❌ Error: {e}")

    upload4.observe(_load4, names="value")

    def _visibilidad_origen(change=None):
        if origen_data.value == "📂 Cargar archivo de matriz normalizada":
            upload4.layout.display = ""
            upload4_out.layout.display = ""
            col_alt4.layout.display = ""
            col_crit4.layout.display = ""
            btn_generar_pesos.layout.display = ""
            pesos_box.layout.display = ""
            col_alt4.options = []
            col_crit4.options = []
            pesos_box.children = []
            pesos_widgets.clear()
            L4["df_norm"] = None
        else:
            upload4.layout.display = "none"
            upload4_out.layout.display = "none"
            if L2.get("df_show") is not None:
                df_l2 = L2["df_show"].copy()
                L4["df_norm"] = df_l2
                cols = list(df_l2.columns)
                alt_col = cols[0]
                crit_cols = cols[1:] if len(cols) > 1 else []
                col_alt4.options = [alt_col]
                col_alt4.value = alt_col
                col_crit4.options = crit_cols
                col_crit4.value = crit_cols
                col_alt4.layout.display = ""
                col_crit4.layout.display = ""
                btn_generar_pesos.layout.display = ""
                pesos_box.layout.display = ""
                with upload4_out:
                    clear_output()
                    print(f"✅ Matriz cargada desde L2: {df_l2.shape[0]} filas × {df_l2.shape[1]} columnas")
                    display(df_l2.head())
                if crit_cols:
                    _actualizar_campos_pesos(crit_cols)
            else:
                col_alt4.layout.display = "none"
                col_crit4.layout.display = "none"
                btn_generar_pesos.layout.display = "none"
                pesos_box.layout.display = "none"
                with upload4_out:
                    clear_output()
                    print("⚠️ No se encontró L2['df_show']. Ejecutá primero la Línea 2.")

    origen_data.observe(_visibilidad_origen, names="value")

    def _run4(b):
        with run4_out:
            clear_output()
            metodo = metodo_agreg4.value
            if L4["df_norm"] is None:
                print("❌ No hay matriz cargada. Seleccioná origen y cargá los datos.")
                return

            df_norm = L4["df_norm"]
            crit_cols = list(col_crit4.value)
            if not crit_cols:
                print("❌ Seleccioná al menos un criterio.")
                return
            alt_col = col_alt4.value
            if not alt_col or alt_col not in df_norm.columns:
                print("❌ Seleccioná una columna de alternativas válida.")
                return

            df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

            if not pesos_widgets:
                print("❌ Primero actualizá los campos de pesos.")
                return
            try:
                pesos_dict = {c: pesos_widgets[c].value for c in crit_cols}
            except KeyError:
                print("❌ Los criterios cambiaron. Volvé a actualizar los campos de pesos.")
                return
            if any(v < 0 for v in pesos_dict.values()):
                print("❌ Todos los pesos deben ser >= 0.")
                return
            suma_pesos = sum(pesos_dict.values())
            if suma_pesos == 0:
                print("❌ La suma de pesos no puede ser 0.")
                return

            pesos_norm = np.array([pesos_dict[c] / suma_pesos for c in crit_cols])

            matriz_val = df_c.values
            alternativas = df_norm[alt_col].values
            L4["df_show"] = df_c.copy()
            L4["df_show"].insert(0, alt_col, alternativas)

            L4["crit_cols"] = crit_cols
            L4["alternativas"] = alternativas

            matriz_transform = None
            if metodo == "Media geométrica ponderada":
                if np.any(matriz_val <= 0):
                    print("❌ La media geométrica ponderada requiere valores estrictamente positivos (>0).")
                    print("   Hay ceros o negativos en la matriz. Normalizá con otro método o ajustá los datos.")
                    return
                u, matriz_transform = media_geometrica_ponderada(matriz_val, pesos_norm, return_matriz=True)
                L4["matriz_transform"] = matriz_transform
            else:
                u = suma_ponderada(matriz_val, pesos_norm)
                L4["matriz_transform"] = None

            df_result = pd.DataFrame({"Alternativa": alternativas, "U(a)": u})
            df_result["Ranking"] = df_result["U(a)"].rank(ascending=False, method="min").astype(int)
            df_result = df_result.sort_values("Ranking")
            L4["df_agreg"] = df_result
            L4["pesos"] = pd.Series(pesos_norm, index=crit_cols)

            display(HTML(f"<b>Resultados – {metodo}</b>"))
            display(df_result.set_index("Ranking").round(4))

            if metodo == "Media geométrica ponderada" and matriz_transform is not None:
                df_transform = pd.DataFrame(matriz_transform, columns=crit_cols, index=alternativas)
                df_transform = df_transform.round(4)
                display(HTML("<br><b>📐 Matriz transformada (r_ij^w_j) – utilizada para la media geométrica ponderada</b>"))
                display(df_transform)

            fig, ax = plt.subplots(figsize=(8, max(4, len(alternativas)*0.4)))
            colores = plt.cm.viridis(np.linspace(0.2, 0.9, len(df_result)))
            ax.barh(df_result["Alternativa"], df_result["U(a)"], color=colores, edgecolor="gray")
            ax.set_xlabel("Utilidad global U(a)", fontweight="bold")
            ax.set_title(f"Ranking – {metodo}", fontweight="bold")
            ax.invert_yaxis()
            ax.grid(axis="x", linestyle="--", alpha=0.6)
            for i, (val, alt) in enumerate(zip(df_result["U(a)"], df_result["Alternativa"])):
                ax.text(val + 0.01*df_result["U(a)"].max(), i, f"{val:.4f}", va="center", fontsize=9)
            plt.tight_layout()
            plt.show()

            dl4_btn.layout.display = ""

    run4_btn.on_click(_run4)

    def _download4(b):
        with dl4_out:
            clear_output()
            if L4["df_agreg"] is None:
                print("❌ Primero calculá la agregación.")
                return
            metodo = metodo_agreg4.value
            crit_cols = L4.get("crit_cols", [])
            alternativas = L4.get("alternativas", [])
            if not crit_cols or len(alternativas) == 0:
                print("❌ No se encontraron criterios o alternativas. Recalculá la agregación.")
                return

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                if L4["df_show"] is not None:
                    L4["df_show"].round(4).to_excel(writer, sheet_name="Matriz_normalizada", startrow=2)
                    ws = writer.sheets["Matriz_normalizada"]
                    ws.cell(row=1, column=1, value="MATRIZ NORMALIZADA")
                if L4["pesos"] is not None:
                    df_pesos = L4["pesos"].to_frame("Peso normalizado").round(4)
                    df_pesos.to_excel(writer, sheet_name="Pesos", startrow=2)
                    ws2 = writer.sheets["Pesos"]
                    ws2.cell(row=1, column=1, value="PESOS UTILIZADOS")
                L4["df_agreg"].round(4).to_excel(writer, sheet_name="Resultados", index=False, startrow=2)
                ws3 = writer.sheets["Resultados"]
                ws3.cell(row=1, column=1, value=f"RESULTADOS – {metodo} | Línea 4 – Modelos de Decisión")
                if metodo == "Media geométrica ponderada" and L4.get("matriz_transform") is not None:
                    df_trans = pd.DataFrame(L4["matriz_transform"],
                                            columns=crit_cols,
                                            index=alternativas).round(4)
                    df_trans.to_excel(writer, sheet_name="Matriz_transformada", startrow=2)
                    ws4 = writer.sheets["Matriz_transformada"]
                    ws4.cell(row=1, column=1, value="MATRIZ r_ij^w_j – Media Geométrica Ponderada")
            buf.seek(0)
            b64 = base64.b64encode(buf.getvalue()).decode()
            display(HTML(f'<a download="agregacion.xlsx" '
                         f'href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">'
                         f'⬇ Descargar agregacion.xlsx</a>'))

    dl4_btn.on_click(_download4)

    display(widgets.HTML("<h3>📊 LÍNEA 4 – Agregación Multicriterio <small>Suma Ponderada · Media Geométrica Ponderada</small></h3>"))
    display(_sep("Origen de los datos"))
    display(origen_data)
    display(_sep("Carga de archivo (si corresponde)"))
    display(upload4, upload4_out)
    display(_sep("Seleccionar columnas"))
    display(widgets.HBox([col_alt4, col_crit4]))
    display(btn_generar_pesos)
    display(_sep("Pesos de cada criterio (ajustar manualmente)"))
    display(pesos_box)
    display(_sep("Método de agregación"))
    display(metodo_agreg4)
    display(recomendaciones_agreg)
    display(_sep("Ejecutar"))
    display(run4_btn, run4_out)
    display(dl4_btn, dl4_out)

    _visibilidad_origen()


# ============================================================
# LÍNEA 5 - TOPSIS
# ============================================================
def run_topsis():
    """Ejecuta TOPSIS"""
    import numpy as np
    import pandas as pd
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    import io, base64, warnings
    warnings.filterwarnings("ignore")
    pd.options.display.float_format = '{:.4f}'.format

    L5 = {
        "df_norm": None,
        "pesos": None,
        "crit_cols": None,
        "alternativas": None,
        "tipo_criterio": {},
        "distancia_type": "euclidea",
        "normalizacion_type": "vector",
        "resultados": None,
        "matriz_r": None,
        "matriz_v": None,
        "v_plus": None,
        "v_minus": None,
        "distancias_ideal": None,
        "distancias_antideal": None,
    }

    # Funciones de normalización
    def _norm_fraccion_max(df):
        return df.div(df.max())
    def _norm_fraccion_suma(df):
        return df.div(df.sum())
    def _norm_fraccion_rango(df):
        rango = df.max() - df.min()
        return (df - df.min()).div(rango.replace(0, np.nan))
    def _norm_vector(df):
        return df.div(np.sqrt((df**2).sum()))
    def _norm_zscore(df):
        return (df - df.mean()) / df.std(ddof=0)
    def _norm_ideal_ref(df, metas_rim):
        result = df.copy()
        for col in df.columns:
            if col not in metas_rim:
                result[col] = df[col]
                continue
            c, d = metas_rim[col]
            a = df[col].min()
            b = df[col].max()
            x = df[col].values
            v = np.where(x < c,
                         np.maximum(0, (x - a) / (c - a)) if c != a else 0,
                         np.where(x <= d,
                                  1.0,
                                  np.maximum(0, (b - x) / (b - d)) if b != d else 0))
            result[col] = v
        return result

    NORM_METODOS = {
        "Fracción del máximo":  _norm_fraccion_max,
        "Fracción de la suma":  _norm_fraccion_suma,
        "Fracción del rango":   _norm_fraccion_rango,
        "Del vector":           _norm_vector,
        "Z-score":              _norm_zscore,
        "Ideal de referencia":  None,
    }

    def obtener_normalizacion(df, tipo, rim_config=None):
        if tipo == "Ideal de referencia":
            return _norm_ideal_ref(df, rim_config or {})
        elif tipo in NORM_METODOS and NORM_METODOS[tipo] is not None:
            return NORM_METODOS[tipo](df)
        else:
            return _norm_vector(df)

    # Funciones de distancia
    def distancia_euclidea_detallada(v_i, v_ref):
        diferencias = v_i - v_ref
        diferencias_cuadrado = diferencias ** 2
        distancia_total = np.sqrt(diferencias_cuadrado.sum(axis=1))
        return distancia_total, diferencias_cuadrado

    def distancia_ciudad_detallada(v_i, v_ref):
        diferencias = np.abs(v_i - v_ref)
        diferencias_cuadrado = diferencias ** 2
        distancia_total = diferencias.sum(axis=1)
        return distancia_total, diferencias_cuadrado

    def distancia_raiz_manhattan_detallada(v_i, v_ref):
        diferencias = np.abs(v_i - v_ref)
        diferencias_cuadrado = diferencias ** 2
        suma_abs = diferencias.sum(axis=1)
        distancia_total = np.sqrt(suma_abs)
        return distancia_total, diferencias_cuadrado

    def distancia_tchebycheff_detallada(v_i, v_ref):
        diferencias = np.abs(v_i - v_ref)
        diferencias_cuadrado = diferencias ** 2
        distancia_total = np.max(diferencias, axis=1)
        return distancia_total, diferencias_cuadrado

    def obtener_distancia_detallada(v_i, v_ref, tipo):
        if tipo == "ciudad":
            return distancia_ciudad_detallada(v_i, v_ref)
        elif tipo == "euclidea":
            return distancia_euclidea_detallada(v_i, v_ref)
        elif tipo == "tchebycheff":
            return distancia_tchebycheff_detallada(v_i, v_ref)
        elif tipo == "raiz_manhattan":
            return distancia_raiz_manhattan_detallada(v_i, v_ref)
        else:
            return distancia_euclidea_detallada(v_i, v_ref)

    def ejecutar_topsis(df_norm, crit_cols, alt_col, pesos_norm, tipo_criterio,
                        distancia_ideal, distancia_antideal, decimales=4):
        df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        alternativas = df_norm[alt_col].values
        if np.any(df_c.values < 0):
            df_c = df_c - df_c.min() + 1
        r_matriz = df_c.values
        v_matriz = r_matriz * pesos_norm
        if decimales is not None:
            v_matriz = np.round(v_matriz, decimales)
        v_plus = np.zeros(len(crit_cols))
        v_minus = np.zeros(len(crit_cols))
        for j, crit in enumerate(crit_cols):
            if tipo_criterio.get(crit, "max") == "max":
                v_plus[j] = v_matriz[:, j].max()
                v_minus[j] = v_matriz[:, j].min()
            else:
                v_plus[j] = v_matriz[:, j].min()
                v_minus[j] = v_matriz[:, j].max()
        if decimales is not None:
            v_plus = np.round(v_plus, decimales)
            v_minus = np.round(v_minus, decimales)
        s_plus, dist_plus_cuadrado = obtener_distancia_detallada(v_matriz, v_plus, distancia_ideal)
        s_minus, dist_minus_cuadrado = obtener_distancia_detallada(v_matriz, v_minus, distancia_antideal)
        c_i = s_minus / (s_plus + s_minus + 1e-9)
        df_result = pd.DataFrame({
            "Alternativa": alternativas,
            "S+": s_plus,
            "S-": s_minus,
            "C(i)": c_i
        })
        df_result["Ranking"] = df_result["C(i)"].rank(ascending=False, method="min").astype(int)
        df_result = df_result.sort_values("Ranking")
        df_dist_plus = pd.DataFrame(dist_plus_cuadrado, columns=crit_cols, index=alternativas)
        df_dist_minus = pd.DataFrame(dist_minus_cuadrado, columns=crit_cols, index=alternativas)
        return df_result, r_matriz, v_matriz, v_plus, v_minus, df_dist_plus, df_dist_minus

    # Widgets
    upload5 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                  description="📂 Subir matriz", button_style="primary")
    upload5_out = widgets.Output()

    btn_desde_l2 = widgets.Button(
        description="📥 Usar matriz de Línea 2",
        button_style="warning",
        layout=widgets.Layout(width="260px")
    )
    btn_desde_l2_out = widgets.Output()

    def _cargar_desde_l2(b):
        with btn_desde_l2_out:
            clear_output()
            try:
                import __main__
                if not hasattr(__main__, "L2"):
                    print("❌ No se encontró L2. ¿Ejecutaste la celda de Normalización?")
                    return
                df_l2 = __main__.L2.get("df_show")
            except Exception as ex:
                print(f"❌ Error al acceder a L2: {ex}")
                return
            if df_l2 is None or (hasattr(df_l2, "empty") and df_l2.empty):
                print("❌ No hay matriz normalizada en Línea 2. Ejecutá primero ▶ Normalizar.")
                return
            L5["df_norm"] = df_l2.copy()
            cols = list(df_l2.columns)
            col_alt5.options = cols
            col_crit5.options = cols
            print(f"✅ Matriz importada desde Línea 2 | {df_l2.shape[0]} filas × {df_l2.shape[1]} columnas")
            display(df_l2.head())

    btn_desde_l2.on_click(_cargar_desde_l2)

    col_alt5 = widgets.Dropdown(description="Alternativas:", options=[],
                                 style={"description_width": "110px"},
                                 layout=widgets.Layout(width="320px"))
    col_crit5 = widgets.SelectMultiple(description="Criterios:", options=[],
                                        layout=widgets.Layout(height="140px", width="380px"),
                                        style={"description_width": "80px"})
    tipo_crit_box = widgets.VBox([])
    tipo_crit_widgets = {}
    btn_actualizar_tipos = widgets.Button(description="🔄 Actualizar tipos",
                                          button_style="info",
                                          layout=widgets.Layout(width="220px"))
    pesos_box = widgets.VBox([])
    pesos_widgets = {}
    btn_generar_pesos = widgets.Button(description="🔄 Actualizar pesos",
                                       button_style="info",
                                       layout=widgets.Layout(width="220px"))
    normalizacion5 = widgets.Dropdown(
        description="Normalización:",
        options=list(NORM_METODOS.keys()),
        value="Del vector",
        style={"description_width": "130px"},
        layout=widgets.Layout(width="380px")
    )
    distancia5 = widgets.Dropdown(
        options=[
            ("Euclidea (p=2): √Σ(dif²)", "euclidea"),
            ("Ciudad/Manhattan (p=1): Σ|dif|", "ciudad"),
            ("Raíz de Manhattan: √(Σ|dif|)", "raiz_manhattan"),
            ("Tchebycheff (p=∞): max|dif|", "tchebycheff")
        ],
        value="euclidea",
        description="Distancia:",
        style={"description_width": "130px"},
        layout=widgets.Layout(width="380px")
    )
    recomendaciones_text = widgets.HTML("""
    <div style='background-color: #2a2a2a; border-left: 4px solid #4a90e2; padding: 12px; margin-top: 8px; border-radius: 4px;'>
        <b style='color: #4a90e2;'>💡 Recomendaciones de Combinación Óptima:</b><br>
        <div style='margin-top: 8px; font-size: 0.95em; line-height: 1.6; color: #e0e0e0;'>
            ✓ <b style='color: #64b5f6;'>Distancia Euclídea (p=2)</b> → Normalización del <b>Vector</b><br>
            ✓ <b style='color: #64b5f6;'>Distancia Ciudad/Manhattan (p=1)</b> → Normalización por <b>Rango</b><br>
            ✓ <b style='color: #64b5f6;'>Distancia Tchebycheff (p=∞)</b> → Normalización del <b>Máximo</b>
        </div>
    </div>
    """)
    rim_box = widgets.VBox([])
    rim_inputs = {}

    def _crear_rim_inputs(criterios):
        nonlocal rim_inputs
        children = []
        rim_inputs = {}
        for crit in criterios:
            if L5["df_norm"] is not None and crit in L5["df_norm"].columns:
                col_data = L5["df_norm"][crit].apply(pd.to_numeric, errors="coerce").dropna()
                sugerido_c = col_data.quantile(0.75) if len(col_data) > 0 else 0.0
                sugerido_d = col_data.max() if len(col_data) > 0 else 1.0
            else:
                sugerido_c, sugerido_d = 0.0, 1.0
            w_c = widgets.BoundedFloatText(value=round(sugerido_c, 4),
                                           min=-1e6, max=1e6, step=0.01,
                                           description=f'{crit[:15]} C:',
                                           layout=widgets.Layout(width='280px'))
            w_d = widgets.BoundedFloatText(value=round(sugerido_d, 4),
                                           min=-1e6, max=1e6, step=0.01,
                                           description='D:',
                                           layout=widgets.Layout(width='280px'))
            rim_inputs[crit] = (w_c, w_d)
            children.append(widgets.HBox([w_c, w_d]))
        rim_box.children = children

    def _actualizar_visibilidad_rim(*args):
        if normalizacion5.value == "Ideal de referencia":
            _crear_rim_inputs(col_crit5.value)
            rim_box.layout.display = ""
        else:
            rim_box.layout.display = "none"

    normalizacion5.observe(_actualizar_visibilidad_rim, names="value")
    col_crit5.observe(_actualizar_visibilidad_rim, names="value")

    run5_btn = widgets.Button(description="▶ Ejecutar TOPSIS", button_style="success",
                              layout=widgets.Layout(width="240px"))
    run5_out = widgets.Output()

    def _actualizar_tipos_criterio(criterios):
        nonlocal tipo_crit_widgets
        tipo_crit_widgets.clear()
        children = []
        for crit in criterios:
            dd = widgets.Dropdown(options=["max", "min"], value="max",
                                  description=f"{crit[:12]}:",
                                  style={"description_width": "120px"},
                                  layout=widgets.Layout(width="250px"))
            tipo_crit_widgets[crit] = dd
            children.append(dd)
        tipo_crit_box.children = children

    def _on_actualizar_tipos_click(b):
        criterios = list(col_crit5.value)
        if not criterios:
            with run5_out:
                clear_output()
                print("⚠️ Seleccioná al menos un criterio.")
            return
        _actualizar_tipos_criterio(criterios)

    btn_actualizar_tipos.on_click(_on_actualizar_tipos_click)

    def _actualizar_campos_pesos(criterios):
        nonlocal pesos_widgets
        pesos_widgets.clear()
        n = len(criterios)
        valor_inicial = 1.0 / n if n > 0 else 0
        children = []
        for crit in criterios:
            w = widgets.FloatText(value=round(valor_inicial, 4),
                                  min=0, max=1e6, step=0.01,
                                  description=f'{crit[:15]}:',
                                  layout=widgets.Layout(width='300px'))
            pesos_widgets[crit] = w
            children.append(w)
        pesos_box.children = children

    def _on_generar_pesos_click(b):
        criterios = list(col_crit5.value)
        if not criterios:
            with run5_out:
                clear_output()
                print("⚠️ Seleccioná al menos un criterio.")
            return
        _actualizar_campos_pesos(criterios)

    btn_generar_pesos.on_click(_on_generar_pesos_click)

    def _load5(change):
        with upload5_out:
            clear_output()
            if not upload5.value:
                return
            key = list(upload5.value.keys())[0]
            fdata = upload5.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L5["df_norm"] = df
                cols = list(df.columns)
                col_alt5.options = cols
                col_crit5.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload5.observe(_load5, names="value")

    def _run5(b):
        with run5_out:
            clear_output()
            if L5["df_norm"] is None:
                print("❌ No hay matriz cargada.")
                return
            df_norm = L5["df_norm"]
            crit_cols = list(col_crit5.value)
            if not crit_cols:
                print("❌ Seleccioná al menos un criterio.")
                return
            alt_col = col_alt5.value
            if not alt_col or alt_col not in df_norm.columns:
                print("❌ Seleccioná una columna de alternativas válida.")
                return
            if not tipo_crit_widgets:
                print("❌ Primero actualizá los tipos de criterio.")
                return
            tipo_criterio = {c: tipo_crit_widgets[c].value for c in crit_cols}
            L5["tipo_criterio"] = tipo_criterio
            if not pesos_widgets:
                print("❌ Primero actualizá los pesos.")
                return
            try:
                pesos_dict = {c: pesos_widgets[c].value for c in crit_cols}
            except KeyError:
                print("❌ Los criterios cambiaron. Volvé a actualizar pesos.")
                return
            suma_pesos = sum(pesos_dict.values())
            if suma_pesos == 0:
                print("❌ La suma de pesos no puede ser 0.")
                return
            pesos_norm = np.array([pesos_dict[c] / suma_pesos for c in crit_cols])
            normalizacion = normalizacion5.value
            distancia_opt = distancia5.value
            dist_ideal = distancia_opt
            dist_antideal = distancia_opt

            etiqueta_dist = {
                "raiz_manhattan": "Raíz de Manhattan: S = √( Σ|Vij - Vj| )",
                "euclidea": "Euclídea: S = √( Σ (Vij - Vj)² )",
                "ciudad": "Manhattan: S = Σ |Vij - Vj|",
                "tchebycheff": "Tchebycheff: S = max|Vij - Vj|"
            }.get(distancia_opt, distancia_opt)

            L5["pesos"] = pd.Series(pesos_norm, index=crit_cols)
            L5["crit_cols"] = crit_cols
            L5["alternativas"] = df_norm[alt_col].values
            L5["distancia_type"] = distancia_opt
            L5["normalizacion_type"] = normalizacion

            try:
                df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
                rim_config = None
                if normalizacion == "Ideal de referencia":
                    rim_config = {}
                    for crit in crit_cols:
                        if crit in rim_inputs:
                            wc, wd = rim_inputs[crit]
                            rim_config[crit] = (wc.value, wd.value)
                df_c_norm = obtener_normalizacion(df_c, normalizacion, rim_config)
                df_c_norm = df_c_norm.round(4)
                df_norm_topsis = df_c_norm.copy()
                df_norm_topsis.insert(0, alt_col, df_norm[alt_col].values)
                df_result, r_mat, v_mat, v_p, v_m, df_dist_p, df_dist_m = ejecutar_topsis(
                    df_norm_topsis, crit_cols, alt_col, pesos_norm, tipo_criterio,
                    distancia_ideal=dist_ideal, distancia_antideal=dist_antideal, decimales=4
                )
                L5["resultados"] = df_result
                L5["matriz_r"] = r_mat
                L5["matriz_v"] = v_mat
                L5["v_plus"] = v_p
                L5["v_minus"] = v_m
                L5["distancias_ideal"] = df_dist_p
                L5["distancias_antideal"] = df_dist_m

                display(HTML(f"<h2>TOPSIS - Cálculo Detallado</h2>"))
                display(HTML(f"<b>Método normalización:</b> {normalizacion} | <b>Función distancia:</b> {etiqueta_dist}"))
                display(HTML("<h3>Paso 1: Matriz Original de Evaluaciones</h3>"))
                display(df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0).round(4))
                display(HTML("<h3>Paso 2: Matriz Normalizada (R) - Método: " + normalizacion + "</h3>"))
                df_r = pd.DataFrame(r_mat, columns=crit_cols, index=L5["alternativas"])
                display(df_r.round(4))
                display(HTML("<h3>Paso 3: Pesos Normalizados</h3>"))
                df_pesos = L5["pesos"].to_frame("Peso normalizado").T
                display(df_pesos.round(4))
                display(HTML("<h3>Paso 4: Matriz Ponderada (V = W·R)</h3>"))
                df_v = pd.DataFrame(v_mat, columns=crit_cols, index=L5["alternativas"])
                display(df_v.round(4))
                display(HTML("<h3>Paso 5: Alternativa Ideal (v+) y Anti-Ideal (v-)</h3>"))
                df_ideales = pd.DataFrame({
                    "Criterio": crit_cols,
                    "Tipo": [tipo_criterio.get(c, "max") for c in crit_cols],
                    "v+": v_p,
                    "v-": v_m
                })
                display(df_ideales.round(4))
                display(HTML("<h3>Paso 6A: Calcular las distancias a la alternativa Ideal (S⁺)</h3>"))
                display(HTML("<b>Fórmula:</b> S<sub>i</sub><sup>+</sup> = √[ Σ<sub>j=1</sub><sup>n</sup> (V<sub>ij</sub> - V<sub>j</sub><sup>+</sup>)<sup>2</sup> ]"))
                display(HTML("<b>Matriz V:</b>"))
                display(df_v.round(4))
                display(HTML("<b>Alternativa v⁺:</b>"))
                display(pd.DataFrame({"Criterio": crit_cols, "v⁺": v_p}).T.round(4))
                display(HTML("<b>S⁺:</b>"))
                display(pd.DataFrame({
                    "Alternativa": L5["alternativas"],
                    "S⁺": df_result.set_index("Alternativa").loc[L5["alternativas"], "S+"]
                }).round(4))
                display(HTML("<h3>Paso 6B: Calcular las distancias a la alternativa Anti-ideal (S⁻)</h3>"))
                display(HTML("<b>Fórmula:</b> S<sub>i</sub><sup>-</sup> = √[ Σ<sub>j=1</sub><sup>n</sup> (V<sub>ij</sub> - V<sub>j</sub><sup>-</sup>)<sup>2</sup> ]"))
                display(HTML("<b>Matriz V:</b>"))
                display(df_v.round(4))
                display(HTML("<b>Alternativa v⁻:</b>"))
                display(pd.DataFrame({"Criterio": crit_cols, "v⁻": v_m}).T.round(4))
                display(HTML("<b>S⁻:</b>"))
                display(pd.DataFrame({
                    "Alternativa": L5["alternativas"],
                    "S⁻": df_result.set_index("Alternativa").loc[L5["alternativas"], "S-"]
                }).round(4))
                display(HTML("<h3>Paso 7: Índice de Similaridad (C(i)) y Ranking</h3>"))
                display(HTML("<i>C(i) = S⁻ / (S⁺ + S⁻)</i>"))
                display(df_result[["Alternativa", "S+", "S-", "C(i)", "Ranking"]].round(4))
                display(HTML("<h3>✅ Alternativas Ordenadas por Ranking (de mejor a peor)</h3>"))
                ranking_final = df_result[["Ranking", "Alternativa", "C(i)"]].sort_values("Ranking")
                display(ranking_final.round(4))
            except Exception as e:
                print(f"❌ Error en cálculos: {e}")
                import traceback
                traceback.print_exc()

    run5_btn.on_click(_run5)

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

    display(widgets.HTML("<h2 style='color: #1f77b4;'>📊 LÍNEA 5 – TOPSIS</h2>"))
    display(widgets.HTML("<p><i>Technique for Order Preference by Similarity to Ideal Solution</i></p>"))
    display(_sep("1️⃣ Cargar archivo"))
    display(upload5, upload5_out)
    display(widgets.HTML("<i>— o bien —</i>"))
    display(btn_desde_l2, btn_desde_l2_out)
    display(_sep("2️⃣ Seleccionar columnas"))
    display(widgets.HBox([col_alt5, col_crit5]))
    display(_sep("3️⃣ Definir tipo de criterio (max/min)"))
    display(btn_actualizar_tipos)
    display(tipo_crit_box)
    display(_sep("4️⃣ Asignar pesos"))
    display(btn_generar_pesos)
    display(pesos_box)
    display(_sep("5️⃣ Opciones de cálculo"))
    display(normalizacion5)
    display(widgets.HTML("<i>Parámetros para Ideal de referencia (RIM):</i>"))
    display(rim_box)
    display(distancia5)
    display(recomendaciones_text)
    display(_sep("6️⃣ Ejecutar"))
    display(run5_btn, run5_out)


# ============================================================
# LÍNEA 6 - RIM
# ============================================================
def run_rim():
    """Ejecuta RIM"""
    import numpy as np
    import pandas as pd
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    import io, base64, warnings
    warnings.filterwarnings("ignore")
    pd.options.display.float_format = '{:.4f}'.format

    L6 = {
        "df_norm": None,
        "pesos": None,
        "crit_cols": None,
        "alternativas": None,
        "tipo_criterio": {},
        "distancia_type": "euclidea",
        "rim_config": {},
        "resultados": None,
        "matriz_r": None,
        "matriz_v": None,
        "v_plus": None,
        "v_minus": None,
        "distancias_ideal": None,
        "distancias_antideal": None,
    }

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

    def normalizar_rim(matriz_vals, crit_cols, rim_config):
        n_rows, n_cols = matriz_vals.shape
        r_matriz = np.zeros_like(matriz_vals, dtype=float)
        for j, crit in enumerate(crit_cols):
            col_vals = matriz_vals[:, j]
            a_minus = col_vals.min()
            a_plus = col_vals.max()
            config = rim_config.get(crit, {})
            b = config.get('b', a_minus)
            d = config.get('d', a_plus)
            for i, val in enumerate(col_vals):
                if b <= val <= d:
                    r_matriz[i, j] = 1.0
                elif val < b:
                    if a_minus != b:
                        dist = min(abs(val - b), abs(val - d))
                        r_matriz[i, j] = 1.0 - dist / (b - a_minus)
                    else:
                        r_matriz[i, j] = 1.0
                elif val > d:
                    if a_plus != d:
                        dist = min(abs(val - d), abs(val - b))
                        r_matriz[i, j] = 1.0 - dist / (a_plus - d)
                    else:
                        r_matriz[i, j] = 1.0
        r_matriz = np.clip(r_matriz, 0, 1)
        return r_matriz

    def distancia_euclidea_detallada(v_i, v_ref):
        diferencias = v_i - v_ref
        diferencias_cuadrado = diferencias ** 2
        distancia_total = np.sqrt(diferencias_cuadrado.sum(axis=1))
        return distancia_total, diferencias_cuadrado

    def distancia_ciudad_detallada(v_i, v_ref):
        diferencias = np.abs(v_i - v_ref)
        diferencias_cuadrado = diferencias ** 2
        distancia_total = diferencias.sum(axis=1)
        return distancia_total, diferencias_cuadrado

    def distancia_tchebycheff_detallada(v_i, v_ref):
        diferencias = np.abs(v_i - v_ref)
        diferencias_cuadrado = diferencias ** 2
        distancia_total = np.max(diferencias, axis=1)
        return distancia_total, diferencias_cuadrado

    def obtener_distancia_detallada(v_i, v_ref, tipo):
        if tipo == "ciudad":
            return distancia_ciudad_detallada(v_i, v_ref)
        elif tipo == "euclidea":
            return distancia_euclidea_detallada(v_i, v_ref)
        elif tipo == "tchebycheff":
            return distancia_tchebycheff_detallada(v_i, v_ref)
        else:
            return distancia_euclidea_detallada(v_i, v_ref)

    def ejecutar_rim(df_norm, crit_cols, alt_col, pesos_norm, rim_config, distancia):
        df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        alternativas = df_norm[alt_col].values
        if np.any(df_c.values < 0):
            df_c = df_c - df_c.min() + 1
        r_matriz = normalizar_rim(df_c.values, crit_cols, rim_config)
        v_matriz = r_matriz * pesos_norm
        v_plus = pesos_norm.copy()
        v_minus = np.zeros(len(crit_cols))
        s_plus, dist_plus_cuadrado = obtener_distancia_detallada(v_matriz, v_plus, distancia)
        s_minus, dist_minus_cuadrado = obtener_distancia_detallada(v_matriz, v_minus, distancia)
        i_index = s_minus / (s_plus + s_minus + 1e-9)
        df_result = pd.DataFrame({
            "Alternativa": alternativas,
            "S+": s_plus,
            "S-": s_minus,
            "I(i)": i_index
        })
        df_result["Ranking"] = df_result["I(i)"].rank(ascending=False, method="min").astype(int)
        df_result = df_result.sort_values("Ranking")
        df_dist_plus = pd.DataFrame(dist_plus_cuadrado, columns=crit_cols, index=alternativas)
        df_dist_minus = pd.DataFrame(dist_minus_cuadrado, columns=crit_cols, index=alternativas)
        return df_result, r_matriz, v_matriz, v_plus, v_minus, df_dist_plus, df_dist_minus

    upload6 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                  description="📂 Subir matriz", button_style="primary")
    upload6_out = widgets.Output()

    btn_desde_l2 = widgets.Button(
        description="📥 Usar matriz de Línea 2",
        button_style="warning",
        layout=widgets.Layout(width="260px")
    )
    btn_desde_l2_out = widgets.Output()

    def _cargar_desde_l2(b):
        with btn_desde_l2_out:
            clear_output()
            try:
                import __main__
                if not hasattr(__main__, "L2"):
                    print("❌ No se encontró L2. ¿Ejecutaste la celda de Normalización?")
                    return
                df_l2 = __main__.L2.get("df_show")
            except Exception as ex:
                print(f"❌ Error al acceder a L2: {ex}")
                return
            if df_l2 is None or (hasattr(df_l2, "empty") and df_l2.empty):
                print("❌ No hay matriz normalizada en Línea 2. Ejecutá primero ▶ Normalizar.")
                return
            L6["df_norm"] = df_l2.copy()
            cols = list(df_l2.columns)
            col_alt6.options = cols
            col_crit6.options = cols
            print(f"✅ Matriz importada desde Línea 2 | {df_l2.shape[0]} filas × {df_l2.shape[1]} columnas")
            display(df_l2.head())

    btn_desde_l2.on_click(_cargar_desde_l2)

    col_alt6 = widgets.Dropdown(description="Alternativas:", options=[],
                                 style={"description_width": "110px"},
                                 layout=widgets.Layout(width="320px"))
    col_crit6 = widgets.SelectMultiple(description="Criterios:", options=[],
                                        layout=widgets.Layout(height="140px", width="380px"),
                                        style={"description_width": "80px"})
    pesos_box = widgets.VBox([])
    pesos_widgets = {}
    btn_generar_pesos = widgets.Button(description="🔄 Actualizar pesos",
                                       button_style="info",
                                       layout=widgets.Layout(width="220px"))
    rim_config_box = widgets.VBox([])
    rim_config_widgets = {}
    btn_config_rim = widgets.Button(description="⚙️ Configurar rangos ideales [b,d]",
                                   button_style="warning",
                                   layout=widgets.Layout(width="280px"))
    rim_config_out = widgets.Output()
    distancia6 = widgets.Dropdown(
        options=[
            ("Euclidea (p=2)", "euclidea"),
            ("Ciudad/Manhattan (p=1)", "ciudad"),
            ("Tchebycheff (p=∞)", "tchebycheff")
        ],
        value="euclidea",
        description="Distancia:",
        style={"description_width": "130px"},
        layout=widgets.Layout(width="380px")
    )
    run6_btn = widgets.Button(description="▶ Ejecutar RIM", button_style="success",
                              layout=widgets.Layout(width="240px"))
    run6_out = widgets.Output()

    def _actualizar_campos_pesos(criterios):
        nonlocal pesos_widgets
        pesos_widgets.clear()
        n = len(criterios)
        valor_inicial = 1.0 / n if n > 0 else 0
        children = []
        for crit in criterios:
            w = widgets.FloatText(value=round(valor_inicial, 4),
                                  min=0, max=1e6, step=0.01,
                                  description=f'{crit[:15]}:',
                                  layout=widgets.Layout(width='300px'))
            pesos_widgets[crit] = w
            children.append(w)
        pesos_box.children = children

    def _on_generar_pesos_click(b):
        criterios = list(col_crit6.value)
        if not criterios:
            with run6_out:
                clear_output()
                print("⚠️ Seleccioná al menos un criterio.")
            return
        _actualizar_campos_pesos(criterios)

    btn_generar_pesos.on_click(_on_generar_pesos_click)

    def _actualizar_config_rim(criterios):
        nonlocal rim_config_widgets
        rim_config_widgets.clear()
        if L6["df_norm"] is None:
            return
        df_c = L6["df_norm"][criterios].apply(pd.to_numeric, errors="coerce").fillna(0)
        children = [
            widgets.HTML("""
            <b>Rango ideal [b, d] para cada criterio</b><br>
            <i>b = límite inferior del rango ideal | d = límite superior del rango ideal</i><br>
            <i>Valores dentro de [b, d] reciben normalización = 1.0</i><br>
            <i>Valores fuera se penalizan por distancia mínima</i><br><br>
            """)
        ]
        for crit in criterios:
            a_min = df_c[crit].min()
            a_max = df_c[crit].max()
            b_widget = widgets.FloatText(
                value=round(a_min, 4),
                description=f"{crit} (b):",
                layout=widgets.Layout(width="350px"),
                style={"description_width": "120px"}
            )
            d_widget = widgets.FloatText(
                value=round(a_max, 4),
                description=f"{crit} (d):",
                layout=widgets.Layout(width="350px"),
                style={"description_width": "120px"}
            )
            rim_config_widgets[crit] = {"b": b_widget, "d": d_widget, "a_min": a_min, "a_max": a_max}
            range_html = widgets.HTML(f"<i>Rango datos: [{a_min:.4f}, {a_max:.4f}]</i>")
            children.append(widgets.VBox([
                widgets.HTML(f"<b>Criterio: {crit}</b>"),
                range_html,
                b_widget,
                d_widget
            ]))
        rim_config_box.children = children

    def _on_config_rim_click(b):
        criterios = list(col_crit6.value)
        if not criterios:
            with rim_config_out:
                clear_output()
                print("⚠️ Seleccioná criterios primero.")
            return
        _actualizar_config_rim(criterios)

    btn_config_rim.on_click(_on_config_rim_click)

    def _load6(change):
        with upload6_out:
            clear_output()
            if not upload6.value:
                return
            key = list(upload6.value.keys())[0]
            fdata = upload6.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L6["df_norm"] = df
                cols = list(df.columns)
                col_alt6.options = cols
                col_crit6.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload6.observe(_load6, names="value")

    def _run6(b):
        with run6_out:
            clear_output()
            if L6["df_norm"] is None:
                print("❌ No hay matriz cargada.")
                return
            df_norm = L6["df_norm"]
            crit_cols = list(col_crit6.value)
            if not crit_cols:
                print("❌ Seleccioná al menos un criterio.")
                return
            alt_col = col_alt6.value
            if not alt_col or alt_col not in df_norm.columns:
                print("❌ Seleccioná una columna de alternativas válida.")
                return
            if not pesos_widgets:
                print("❌ Primero actualizá los pesos.")
                return
            try:
                pesos_dict = {c: pesos_widgets[c].value for c in crit_cols}
            except KeyError:
                print("❌ Los criterios cambiaron. Volvé a actualizar pesos.")
                return
            suma_pesos = sum(pesos_dict.values())
            if suma_pesos == 0:
                print("❌ La suma de pesos no puede ser 0.")
                return
            pesos_norm = np.array([pesos_dict[c] / suma_pesos for c in crit_cols])
            if not rim_config_widgets:
                print("❌ Primero configurá los rangos ideales.")
                return
            rim_config = {}
            for crit in crit_cols:
                if crit in rim_config_widgets:
                    rim_config[crit] = {
                        'b': rim_config_widgets[crit]['b'].value,
                        'd': rim_config_widgets[crit]['d'].value
                    }
            L6["pesos"] = pd.Series(pesos_norm, index=crit_cols)
            L6["crit_cols"] = crit_cols
            L6["alternativas"] = df_norm[alt_col].values
            L6["rim_config"] = rim_config
            distancia = distancia6.value
            L6["distancia_type"] = distancia

            try:
                df_result, r_mat, v_mat, v_p, v_m, df_dist_p, df_dist_m = ejecutar_rim(
                    df_norm, crit_cols, alt_col, pesos_norm, rim_config, distancia
                )
                L6["resultados"] = df_result
                L6["matriz_r"] = r_mat
                L6["matriz_v"] = v_mat
                L6["v_plus"] = v_p
                L6["v_minus"] = v_m
                L6["distancias_ideal"] = df_dist_p
                L6["distancias_antideal"] = df_dist_m

                display(HTML("<h2>RIM - Cálculo Detallado</h2>"))
                display(HTML("<h3>Paso 1: Identificar el intervalo de variación y el ideal de referencia de cada criterio</h3>"))
                df_original = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
                df_paso1 = df_original.copy()
                df_paso1.insert(0, alt_col, df_norm[alt_col].values)
                stats_data = {}
                stats_data[alt_col] = ["aᵢⁱ (mín)", "aᵢⁱ (máx)", "b", "d", "|aᵢⁱ - b|", "|d - aᵢⁱ|"]
                for crit in crit_cols:
                    col_vals = df_original[crit].values
                    a_min = col_vals.min()
                    a_max = col_vals.max()
                    b = rim_config[crit]['b']
                    d = rim_config[crit]['d']
                    stats_data[crit] = [
                        round(a_min, 4),
                        round(a_max, 4),
                        round(b, 4),
                        round(d, 4),
                        round(abs(a_min - b), 4),
                        round(abs(d - a_max), 4)
                    ]
                display(df_paso1.round(4))
                df_stats = pd.DataFrame(stats_data).T
                df_stats.columns = ["aᵢⁱ (mín)", "aᵢⁱ (máx)", "b", "d", "|aᵢⁱ - b|", "|d - aᵢⁱ|"]
                display(df_stats.round(4))
                display(HTML("<h3>Paso 2: Matriz Normalizada (R) - RIM</h3>"))
                df_r = pd.DataFrame(r_mat, columns=crit_cols, index=L6["alternativas"])
                display(df_r.round(4))
                display(HTML("<h3>Paso 3: Pesos Normalizados</h3>"))
                df_pesos = L6["pesos"].to_frame("Peso normalizado").T
                display(df_pesos.round(4))
                display(HTML("<h3>Paso 4: Matriz Ponderada (V = W·R)</h3>"))
                df_v = pd.DataFrame(v_mat, columns=crit_cols, index=L6["alternativas"])
                display(df_v.round(4))
                display(HTML("<h3>Paso 5: Alternativa Ideal (v+) y Anti-Ideal (v-)</h3>"))
                display(HTML("<i><b>En RIM:</b> v+ = vector de pesos | v- = vector de ceros</i>"))
                df_ideales = pd.DataFrame({"Criterio": crit_cols, "v+": v_p, "v-": v_m})
                display(df_ideales.round(4))
                display(HTML("<h3>Paso 6A: Calcular las distancias a la alternativa Ideal (S⁺)</h3>"))
                display(HTML("<b>Fórmula:</b> S<sub>i</sub><sup>+</sup> = √[ Σ<sub>j=1</sub><sup>n</sup> (v<sub>ij</sub> - w<sub>j</sub>)<sup>2</sup> ]"))
                display(HTML("<b>Matriz V:</b>"))
                display(df_v.round(4))
                display(HTML("<b>Alternativa v⁺:</b>"))
                display(pd.DataFrame({"Criterio": crit_cols, "v⁺": v_p}).T.round(4))
                display(HTML("<b>S⁺:</b>"))
                display(pd.DataFrame({
                    "Alternativa": L6["alternativas"],
                    "S⁺": df_result.set_index("Alternativa").loc[L6["alternativas"], "S+"]
                }).round(4))
                display(HTML("<h3>Paso 6B: Calcular las distancias a la alternativa Anti-ideal (S⁻)</h3>"))
                display(HTML("<b>Fórmula:</b> S<sub>i</sub><sup>-</sup> = √[ Σ<sub>j=1</sub><sup>n</sup> (v<sub>ij</sub>)<sup>2</sup> ]"))
                display(HTML("<b>Matriz V:</b>"))
                display(df_v.round(4))
                display(HTML("<b>Alternativa v⁻:</b>"))
                display(pd.DataFrame({"Criterio": crit_cols, "v⁻": v_m}).T.round(4))
                display(HTML("<b>S⁻:</b>"))
                display(pd.DataFrame({
                    "Alternativa": L6["alternativas"],
                    "S⁻": df_result.set_index("Alternativa").loc[L6["alternativas"], "S-"]
                }).round(4))
                display(HTML("<h3>Paso 7: Cálculo del índice y ordenamiento</h3>"))
                display(HTML("<i>Fórmula: I<sub>i</sub> = S<sub>i</sub><sup>-</sup> / (S<sub>i</sub><sup>+</sup> + S<sub>i</sub><sup>-</sup>)</i>"))
                display(df_result[["Alternativa", "S+", "S-", "I(i)", "Ranking"]].round(4))
                display(HTML("<h3>✅ Alternativas Ordenadas por Ranking (de mejor a peor)</h3>"))
                ranking_final = df_result[["Ranking", "Alternativa", "I(i)"]].sort_values("Ranking")
                display(ranking_final.round(4))
            except Exception as e:
                print(f"❌ Error en cálculos: {e}")
                import traceback
                traceback.print_exc()

    run6_btn.on_click(_run6)

    display(widgets.HTML("<h2 style='color: #2ca02c;'>📊 LÍNEA 6 – RIM</h2>"))
    display(widgets.HTML("<p><i>Reference Ideal Method</i></p>"))
    display(_sep("1️⃣ Cargar archivo"))
    display(upload6, upload6_out)
    display(widgets.HTML("<i>— o bien —</i>"))
    display(btn_desde_l2, btn_desde_l2_out)
    display(_sep("2️⃣ Seleccionar columnas"))
    display(widgets.HBox([col_alt6, col_crit6]))
    display(_sep("3️⃣ Asignar pesos"))
    display(btn_generar_pesos)
    display(pesos_box)
    display(_sep("4️⃣ Configurar rango ideal [b, d]"))
    display(widgets.HTML("""
    <i>RIM permite definir un rango ideal para cada criterio.<br>
    Los valores dentro de [b, d] son considerados óptimos.<br>
    Los valores fuera se penalizan según su distancia mínima al rango.</i>
    """))
    display(btn_config_rim)
    display(rim_config_box)
    display(_sep("5️⃣ Seleccionar función de distancia"))
    display(distancia6)
    display(_sep("6️⃣ Ejecutar"))
    display(run6_btn, run6_out)


__all__ = [
    'run_estadistica',
    'run_normalizacion',
    'run_ponderacion',
    'run_agregacion',
    'run_topsis',
    'run_rim'
]
