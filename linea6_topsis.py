import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import io, warnings
warnings.filterwarnings("ignore")

pd.options.display.float_format = '{:.4f}'.format

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
        if col not in metas_rim: result[col] = df[col]; continue
        c, d = metas_rim[col]; a = df[col].min(); b = df[col].max(); x = df[col].values
        v = np.where(x < c, np.maximum(0, (x-a)/(c-a)) if c != a else 0,
                     np.where(x <= d, 1.0, np.maximum(0, (b-x)/(b-d)) if b != d else 0))
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

# ─── Distancias ─────────────────────────────────────────────
def distancia_euclidea(v_i, v_ref):
    d = v_i - v_ref; return np.sqrt((d**2).sum(axis=1)), d**2

def distancia_ciudad(v_i, v_ref):
    d = np.abs(v_i - v_ref); return d.sum(axis=1), d**2

def distancia_raiz_manhattan(v_i, v_ref):
    d = np.abs(v_i - v_ref); return np.sqrt(d.sum(axis=1)), d**2

def distancia_tchebycheff(v_i, v_ref):
    d = np.abs(v_i - v_ref); return np.max(d, axis=1), d**2

def obtener_distancia(v_i, v_ref, tipo):
    return {"euclidea": distancia_euclidea, "ciudad": distancia_ciudad,
            "raiz_manhattan": distancia_raiz_manhattan,
            "tchebycheff": distancia_tchebycheff}.get(tipo, distancia_euclidea)(v_i, v_ref)

def obtener_normalizacion(df, tipo, rim_config=None):
    if tipo == "Ideal de referencia": return _norm_ideal_ref(df, rim_config or {})
    fn = NORM_METODOS.get(tipo)
    return fn(df) if fn else _norm_vector(df)

def ejecutar_topsis_calc(df_norm, crit_cols, alt_col, pesos_norm, tipo_criterio, distancia_opt):
    df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    alternativas = df_norm[alt_col].values
    if np.any(df_c.values < 0): df_c = df_c - df_c.min() + 1
    r_mat = df_c.values
    v_mat = np.round(r_mat * pesos_norm, 4)
    v_plus = np.array([v_mat[:, j].max() if tipo_criterio.get(crit_cols[j], "max") == "max"
                       else v_mat[:, j].min() for j in range(len(crit_cols))])
    v_minus = np.array([v_mat[:, j].min() if tipo_criterio.get(crit_cols[j], "max") == "max"
                        else v_mat[:, j].max() for j in range(len(crit_cols))])
    v_plus = np.round(v_plus, 4); v_minus = np.round(v_minus, 4)
    s_plus, dp = obtener_distancia(v_mat, v_plus, distancia_opt)
    s_minus, dm = obtener_distancia(v_mat, v_minus, distancia_opt)
    c_i = s_minus / (s_plus + s_minus + 1e-9)
    df_result = pd.DataFrame({"Alternativa": alternativas, "S+": s_plus, "S-": s_minus, "C(i)": c_i})
    df_result["Ranking"] = df_result["C(i)"].rank(ascending=False, method="min").astype(int)
    df_result = df_result.sort_values("Ranking")
    return df_result, r_mat, v_mat, v_plus, v_minus, pd.DataFrame(dp, columns=crit_cols, index=alternativas), pd.DataFrame(dm, columns=crit_cols, index=alternativas)

def run_topsis():
    L5 = {"df_norm": None}

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

    upload5 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                  description="📂 Subir matriz", button_style="primary")
    upload5_out = widgets.Output()

    col_alt5 = widgets.Dropdown(description="Alternativas:", options=[],
                                 style={"description_width": "110px"},
                                 layout=widgets.Layout(width="320px"))
    col_crit5 = widgets.SelectMultiple(description="Criterios:", options=[],
                                        layout=widgets.Layout(height="140px", width="380px"),
                                        style={"description_width": "80px"})

    tipo_crit_box = widgets.VBox([])
    tipo_crit_widgets = {}
    btn_actualizar_tipos = widgets.Button(description="🔄 Actualizar tipos", button_style="info",
                                          layout=widgets.Layout(width="220px"))

    pesos_box = widgets.VBox([])
    pesos_widgets = {}
    btn_generar_pesos = widgets.Button(description="🔄 Actualizar pesos", button_style="info",
                                       layout=widgets.Layout(width="220px"))

    normalizacion5 = widgets.Dropdown(
        description="Normalización:",
        options=list(NORM_METODOS.keys()), value="Del vector",
        style={"description_width": "130px"}, layout=widgets.Layout(width="380px"))

    distancia5 = widgets.Dropdown(
        options=[("Euclidea (p=2): √Σ(dif²)", "euclidea"),
                 ("Ciudad/Manhattan (p=1): Σ|dif|", "ciudad"),
                 ("Raíz de Manhattan: √(Σ|dif|)", "raiz_manhattan"),
                 ("Tchebycheff (p=∞): max|dif|", "tchebycheff")],
        value="euclidea", description="Distancia:",
        style={"description_width": "130px"}, layout=widgets.Layout(width="380px"))

    rim_box = widgets.VBox([])
    rim_inputs = {}

    def _crear_rim_inputs(criterios):
        nonlocal rim_inputs
        children = []; rim_inputs = {}
        for crit in criterios:
            if L5["df_norm"] is not None and crit in L5["df_norm"].columns:
                col_data = L5["df_norm"][crit].apply(pd.to_numeric, errors="coerce").dropna()
                sugerido_c = col_data.quantile(0.75) if len(col_data) > 0 else 0.0
                sugerido_d = col_data.max() if len(col_data) > 0 else 1.0
            else:
                sugerido_c, sugerido_d = 0.0, 1.0
            w_c = widgets.BoundedFloatText(value=round(sugerido_c, 4), min=-1e6, max=1e6, step=0.01,
                                           description=f'{crit[:15]} C:', layout=widgets.Layout(width='280px'))
            w_d = widgets.BoundedFloatText(value=round(sugerido_d, 4), min=-1e6, max=1e6, step=0.01,
                                           description='D:', layout=widgets.Layout(width='280px'))
            rim_inputs[crit] = (w_c, w_d); children.append(widgets.HBox([w_c, w_d]))
        rim_box.children = children

    def _actualizar_visibilidad_rim(*args):
        if normalizacion5.value == "Ideal de referencia":
            _crear_rim_inputs(col_crit5.value); rim_box.layout.display = ""
        else:
            rim_box.layout.display = "none"

    normalizacion5.observe(_actualizar_visibilidad_rim, names="value")
    col_crit5.observe(_actualizar_visibilidad_rim, names="value")

    run5_btn = widgets.Button(description="▶ Ejecutar TOPSIS", button_style="success",
                              layout=widgets.Layout(width="240px"))
    run5_out = widgets.Output()

    def _actualizar_tipos_criterio(criterios):
        tipo_crit_widgets.clear()
        children = []
        for crit in criterios:
            dd = widgets.Dropdown(options=["max", "min"], value="max",
                                  description=f"{crit[:12]}:",
                                  style={"description_width": "120px"},
                                  layout=widgets.Layout(width="250px"))
            tipo_crit_widgets[crit] = dd; children.append(dd)
        tipo_crit_box.children = children

    btn_actualizar_tipos.on_click(lambda b: _actualizar_tipos_criterio(list(col_crit5.value)) if col_crit5.value else None)

    def _actualizar_campos_pesos(criterios):
        pesos_widgets.clear()
        n = len(criterios); valor_inicial = 1.0 / n if n > 0 else 0
        children = []
        for crit in criterios:
            w = widgets.FloatText(value=round(valor_inicial, 4), min=0, max=1e6, step=0.01,
                                  description=f'{crit[:15]}:', layout=widgets.Layout(width='300px'))
            pesos_widgets[crit] = w; children.append(w)
        pesos_box.children = children

    btn_generar_pesos.on_click(lambda b: _actualizar_campos_pesos(list(col_crit5.value)) if col_crit5.value else None)

    def _load5(change):
        with upload5_out:
            clear_output()
            if not upload5.value: return
            key = list(upload5.value.keys())[0]
            fdata = upload5.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L5["df_norm"] = df
                cols = list(df.columns)
                col_alt5.options = cols; col_crit5.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload5.observe(_load5, names="value")

    def _run5(b):
        with run5_out:
            clear_output()
            if L5["df_norm"] is None: print("❌ No hay matriz cargada."); return
            df_norm = L5["df_norm"]
            crit_cols = list(col_crit5.value)
            if not crit_cols: print("❌ Seleccioná al menos un criterio."); return
            alt_col = col_alt5.value
            if not alt_col or alt_col not in df_norm.columns: print("❌ Seleccioná alternativas válidas."); return
            if not tipo_crit_widgets: print("❌ Primero actualizá los tipos de criterio."); return
            tipo_criterio = {c: tipo_crit_widgets[c].value for c in crit_cols}
            if not pesos_widgets: print("❌ Primero actualizá los pesos."); return
            try:
                pesos_dict = {c: pesos_widgets[c].value for c in crit_cols}
            except KeyError:
                print("❌ Los criterios cambiaron. Volvé a actualizar pesos."); return
            suma_pesos = sum(pesos_dict.values())
            if suma_pesos == 0: print("❌ La suma de pesos no puede ser 0."); return
            pesos_norm = np.array([pesos_dict[c] / suma_pesos for c in crit_cols])

            normalizacion = normalizacion5.value; distancia_opt = distancia5.value
            df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
            rim_config = None
            if normalizacion == "Ideal de referencia":
                rim_config = {crit: (rim_inputs[crit][0].value, rim_inputs[crit][1].value) for crit in crit_cols if crit in rim_inputs}
            df_c_norm = obtener_normalizacion(df_c, normalizacion, rim_config).round(4)
            df_norm_topsis = df_c_norm.copy()
            df_norm_topsis.insert(0, alt_col, df_norm[alt_col].values)

            try:
                df_result, r_mat, v_mat, v_p, v_m, df_dp, df_dm = ejecutar_topsis_calc(
                    df_norm_topsis, crit_cols, alt_col, pesos_norm, tipo_criterio, distancia_opt)
                alternativas = df_norm[alt_col].values

                display(HTML("<h2>TOPSIS – Cálculo Detallado</h2>"))
                display(HTML(f"<b>Normalización:</b> {normalizacion} | <b>Distancia:</b> {distancia_opt}"))
                display(HTML("<h3>Paso 1: Matriz Original</h3>")); display(df_c.round(4))
                display(HTML(f"<h3>Paso 2: Matriz Normalizada ({normalizacion})</h3>"))
                display(pd.DataFrame(r_mat, columns=crit_cols, index=alternativas).round(4))
                display(HTML("<h3>Paso 3: Pesos Normalizados</h3>"))
                display(pd.DataFrame(pesos_norm.reshape(1,-1), columns=crit_cols).round(4))
                display(HTML("<h3>Paso 4: Matriz Ponderada (V = W·R)</h3>"))
                display(pd.DataFrame(v_mat, columns=crit_cols, index=alternativas).round(4))
                display(HTML("<h3>Paso 5: Ideal (v+) y Anti-Ideal (v-)</h3>"))
                display(pd.DataFrame({"Criterio": crit_cols, "Tipo": [tipo_criterio.get(c,"max") for c in crit_cols], "v+": v_p, "v-": v_m}).round(4))
                display(HTML("<h3>Paso 6: Distancias S+ y S-</h3>"))
                display(HTML("<h3>Paso 7: Índice C(i) y Ranking</h3>"))
                display(df_result[["Alternativa","S+","S-","C(i)","Ranking"]].round(4))
                display(HTML("<h3>✅ Ranking Final</h3>"))
                display(df_result[["Ranking","Alternativa","C(i)"]].sort_values("Ranking").round(4))
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback; traceback.print_exc()

    run5_btn.on_click(_run5)

    display(widgets.HTML("""
<h2 style='color: #1f77b4;'>📊 LÍNEA 6 – TOPSIS</h2>
<p><i>Technique for Order Preference by Similarity to Ideal Solution</i></p>
"""))
    display(_sep("1️⃣ Cargar archivo"))
    display(upload5, upload5_out)
    display(_sep("2️⃣ Seleccionar columnas"))
    display(widgets.HBox([col_alt5, col_crit5]))
    display(_sep("3️⃣ Tipo de criterio (max/min)"))
    display(btn_actualizar_tipos); display(tipo_crit_box)
    display(_sep("4️⃣ Pesos"))
    display(btn_generar_pesos); display(pesos_box)
    display(_sep("5️⃣ Opciones"))
    display(normalizacion5)
    display(widgets.HTML("<i>Parámetros RIM:</i>")); display(rim_box)
    display(distancia5)
    display(_sep("6️⃣ Ejecutar"))
    display(run5_btn, run5_out)
