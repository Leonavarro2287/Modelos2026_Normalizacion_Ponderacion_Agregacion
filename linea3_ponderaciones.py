import numpy as np
import pandas as pd
from itertools import combinations
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import io, warnings
warnings.filterwarnings("ignore")

pd.options.display.float_format = '{:.4f}'.format

# ─── Funciones de ponderación ───────────────────────────────
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

# ─── Normalizaciones ────────────────────────────────────────
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
        a = df[col].min(); b = df[col].max(); x = df[col].values
        v = np.where(x < c,
                     np.maximum(0, (x - a) / (c - a)) if c != a else 0,
                     np.where(x <= d, 1.0,
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

def run_ponderaciones():
    L3 = {"df": None, "crit_cols": None}

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

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
        nonlocal rim3_inputs
        df = L3["df"]
        crit_cols = list(col_crit3.value) if col_crit3.value else []
        if df is None or not crit_cols:
            rim3_box.children = [widgets.HTML("<small>Seleccioná criterios para definir C y D.</small>")]
            return
        rim3_inputs = {}
        children = []
        for crit in crit_cols:
            col_data = pd.to_numeric(df[crit], errors="coerce").dropna()
            sugerido_c = col_data.quantile(0.75) if len(col_data) > 0 else 0.0
            sugerido_d = col_data.max() if len(col_data) > 0 else 1.0
            w_c = widgets.BoundedFloatText(value=round(sugerido_c, 4), min=-1e6, max=1e6, step=0.01,
                                           description=f'{crit[:15]} C:', layout=widgets.Layout(width='280px'))
            w_d = widgets.BoundedFloatText(value=round(sugerido_d, 4), min=-1e6, max=1e6, step=0.01,
                                           description='D:', layout=widgets.Layout(width='280px'))
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
        if L3["df"] is None or not L3.get("crit_cols"): return
        cols = L3["crit_cols"]; wmap = {}; rows = []
        for c in cols:
            w = widgets.IntText(value=1, description=f"{c}:",
                                style={"description_width":"200px"}, layout=widgets.Layout(width="320px"))
            wmap[c] = w; rows.append(w)
        L3["ord_widgets"] = wmap
        with ord3_out:
            clear_output(); display(widgets.VBox(rows))

    def _render3_tas():
        if L3["df"] is None or not L3.get("crit_cols"): return
        cols = L3["crit_cols"]; wmap = {}; rows = []
        for c in cols:
            w = widgets.FloatText(value=1.0, description=f"{c}:",
                                  style={"description_width":"200px"}, layout=widgets.Layout(width="320px"))
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
            _render3_rim(); rim3_box.layout.display = ""
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
                    print("❌ No se definieron parámetros C y D para RIM."); return
                metas = {crit: (rim3_inputs[crit][0].value, rim3_inputs[crit][1].value) for crit in crit_cols}
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
