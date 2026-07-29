import io, warnings
import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML

warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:.4f}'.format

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
        if col not in metas_rim: continue
        c, d = metas_rim[col]
        a, b = df[col].min(), df[col].max()
        x = df[col].values
        v = np.where(x < c, np.maximum(0, (x - a) / (c - a)) if c != a else 0,
                     np.where(x <= d, 1.0, np.maximum(0, (b - x) / (b - d)) if b != d else 0))
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
    distancia_total = np.sqrt(diferencias.sum(axis=1))
    return distancia_total, diferencias_cuadrado

def distancia_tchebycheff_detallada(v_i, v_ref):
    diferencias = np.abs(v_i - v_ref)
    diferencias_cuadrado = diferencias ** 2
    distancia_total = np.max(diferencias, axis=1)
    return distancia_total, diferencias_cuadrado

def obtener_distancia_detallada(v_i, v_ref, tipo):
    if tipo == "ciudad": return distancia_ciudad_detallada(v_i, v_ref)
    elif tipo == "tchebycheff": return distancia_tchebycheff_detallada(v_i, v_ref)
    elif tipo == "raiz_manhattan": return distancia_raiz_manhattan_detallada(v_i, v_ref)
    else: return distancia_euclidea_detallada(v_i, v_ref)

def _obtener_normalizacion(df, tipo, rim_config=None):
    if tipo == "Ideal de referencia": return _norm_ideal_ref(df, rim_config or {})
    elif tipo in NORM_METODOS and NORM_METODOS[tipo] is not None: return NORM_METODOS[tipo](df)
    else: return _norm_vector(df)

# --- TOPSIS ---
def run_topsis():
    L5 = {"df_norm": None, "pesos": None}
    upload5 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False, description="📂 Subir matriz", button_style="primary")
    upload5_out = widgets.Output()

    btn_desde_l2 = widgets.Button(description="📥 Usar matriz de Línea 2", button_style="warning", layout=widgets.Layout(width="260px"))
    btn_desde_l2_out = widgets.Output()

    col_alt5 = widgets.Dropdown(description="Alternativas:", options=[], style={"description_width": "110px"}, layout=widgets.Layout(width="320px"))
    col_crit5 = widgets.SelectMultiple(description="Criterios:", options=[], layout=widgets.Layout(height="140px", width="380px"), style={"description_width": "80px"})

    tipo_crit_box = widgets.VBox([])
    tipo_crit_widgets = {}
    btn_actualizar_tipos = widgets.Button(description="🔄 Actualizar tipos", button_style="info", layout=widgets.Layout(width="220px"))

    pesos_box = widgets.VBox([])
    pesos_widgets = {}
    btn_generar_pesos = widgets.Button(description="🔄 Actualizar pesos", button_style="info", layout=widgets.Layout(width="220px"))

    normalizacion5 = widgets.Dropdown(description="Normalización:", options=list(NORM_METODOS.keys()), value="Del vector", style={"description_width": "130px"}, layout=widgets.Layout(width="380px"))
    distancia5 = widgets.Dropdown(
        options=[("Euclidea (p=2)", "euclidea"), ("Ciudad/Manhattan (p=1)", "ciudad"), ("Raíz de Manhattan", "raiz_manhattan"), ("Tchebycheff (p=∞)", "tchebycheff")],
        value="euclidea", description="Distancia:", style={"description_width": "130px"}, layout=widgets.Layout(width="380px")
    )

    run5_btn = widgets.Button(description="▶ Ejecutar TOPSIS", button_style="success", layout=widgets.Layout(width="240px"))
    run5_out = widgets.Output()

    def _cargar_desde_l2(b):
        with btn_desde_l2_out:
            clear_output()
            try:
                from .normalizacion import L2
                df_l2 = L2.get("df_show")
            except ImportError:
                df_l2 = None

            if df_l2 is None:
                print("❌ No hay matriz normalizada en Línea 2.")
                return

            L5["df_norm"] = df_l2.copy()
            cols = list(df_l2.columns)
            col_alt5.options = cols; col_crit5.options = cols
            print(f"✅ Matriz importada desde Línea 2 | {df_l2.shape[0]} filas × {df_l2.shape[1]} columnas")
            display(df_l2.head())

    btn_desde_l2.on_click(_cargar_desde_l2)

    def _on_actualizar_tipos_click(b):
        nonlocal tipo_crit_widgets
        tipo_crit_widgets.clear()
        criterios = list(col_crit5.value)
        children = [widgets.Dropdown(options=["max", "min"], value="max", description=f"{crit[:12]}:", style={"description_width": "120px"}, layout=widgets.Layout(width="250px")) for crit in criterios]
        for crit, w in zip(criterios, children): tipo_crit_widgets[crit] = w
        tipo_crit_box.children = children

    btn_actualizar_tipos.on_click(_on_actualizar_tipos_click)

    def _on_generar_pesos_click(b):
        nonlocal pesos_widgets
        pesos_widgets.clear()
        criterios = list(col_crit5.value)
        n = len(criterios)
        valor_inicial = 1.0 / n if n > 0 else 0
        children = [widgets.FloatText(value=round(valor_inicial, 4), min=0, max=1e6, step=0.01, description=f'{crit[:15]}:', layout=widgets.Layout(width='300px')) for crit in criterios]
        for crit, w in zip(criterios, children): pesos_widgets[crit] = w
        pesos_box.children = children

    btn_generar_pesos.on_click(_on_generar_pesos_click)

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
            alt_col = col_alt5.value
            if not crit_cols or not alt_col: print("❌ Seleccioná criterios y alternativas."); return
            if not tipo_crit_widgets or not pesos_widgets: print("❌ Actualizá tipos de criterio y pesos."); return

            tipo_criterio = {c: tipo_crit_widgets[c].value for c in crit_cols}
            pesos_dict = {c: pesos_widgets[c].value for c in crit_cols}
            suma_pesos = sum(pesos_dict.values())
            if suma_pesos == 0: print("❌ Suma de pesos es 0."); return
            pesos_norm = np.array([pesos_dict[c] / suma_pesos for c in crit_cols])

            df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
            df_c_norm = _obtener_normalizacion(df_c, normalizacion5.value)

            r_matriz = df_c_norm.values
            v_matriz = r_matriz * pesos_norm
            alternativas = df_norm[alt_col].values

            v_plus = np.zeros(len(crit_cols))
            v_minus = np.zeros(len(crit_cols))
            for j, crit in enumerate(crit_cols):
                if tipo_criterio.get(crit, "max") == "max":
                    v_plus[j] = v_matriz[:, j].max(); v_minus[j] = v_matriz[:, j].min()
                else:
                    v_plus[j] = v_matriz[:, j].min(); v_minus[j] = v_matriz[:, j].max()

            s_plus, _ = obtener_distancia_detallada(v_matriz, v_plus, distancia5.value)
            s_minus, _ = obtener_distancia_detallada(v_matriz, v_minus, distancia5.value)

            c_i = s_minus / (s_plus + s_minus + 1e-9)
            df_result = pd.DataFrame({"Alternativa": alternativas, "S+": s_plus, "S-": s_minus, "C(i)": c_i})
            df_result["Ranking"] = df_result["C(i)"].rank(ascending=False, method="min").astype(int)
            df_result = df_result.sort_values("Ranking")

            display(HTML("<h2>Resultados TOPSIS</h2>"))
            display(df_result.round(4))

    run5_btn.on_click(_run5)

    display(widgets.HTML("<h2>📊 LÍNEA 5 – TOPSIS</h2>"))
    display(upload5, upload5_out, btn_desde_l2, btn_desde_l2_out)
    display(widgets.HBox([col_alt5, col_crit5]))
    display(btn_actualizar_tipos, tipo_crit_box)
    display(btn_generar_pesos, pesos_box)
    display(normalizacion5, distancia5)
    display(run5_btn, run5_out)

# --- RIM ---
def run_rim():
    L6 = {"df_norm": None}
    upload6 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False, description="📂 Subir matriz", button_style="primary")
    upload6_out = widgets.Output()

    col_alt6 = widgets.Dropdown(description="Alternativas:", options=[], style={"description_width": "110px"}, layout=widgets.Layout(width="320px"))
    col_crit6 = widgets.SelectMultiple(description="Criterios:", options=[], layout=widgets.Layout(height="140px", width="380px"), style={"description_width": "80px"})

    pesos_box = widgets.VBox([])
    pesos_widgets = {}
    btn_generar_pesos = widgets.Button(description="🔄 Actualizar pesos", button_style="info", layout=widgets.Layout(width="220px"))

    rim_config_box = widgets.VBox([])
    rim_config_widgets = {}
    btn_config_rim = widgets.Button(description="⚙️ Configurar rangos ideales [b,d]", button_style="warning", layout=widgets.Layout(width="280px"))

    distancia6 = widgets.Dropdown(
        options=[("Euclidea (p=2)", "euclidea"), ("Ciudad/Manhattan (p=1)", "ciudad"), ("Tchebycheff (p=∞)", "tchebycheff")],
        value="euclidea", description="Distancia:", style={"description_width": "130px"}, layout=widgets.Layout(width="380px")
    )

    run6_btn = widgets.Button(description="▶ Ejecutar RIM", button_style="success", layout=widgets.Layout(width="240px"))
    run6_out = widgets.Output()

    def _on_generar_pesos_click(b):
        nonlocal pesos_widgets
        pesos_widgets.clear()
        criterios = list(col_crit6.value)
        n = len(criterios)
        valor_inicial = 1.0 / n if n > 0 else 0
        children = [widgets.FloatText(value=round(valor_inicial, 4), min=0, max=1e6, step=0.01, description=f'{crit[:15]}:', layout=widgets.Layout(width='300px')) for crit in criterios]
        for crit, w in zip(criterios, children): pesos_widgets[crit] = w
        pesos_box.children = children

    btn_generar_pesos.on_click(_on_generar_pesos_click)

    def _on_config_rim_click(b):
        nonlocal rim_config_widgets
        rim_config_widgets.clear()
        if L6["df_norm"] is None: return
        criterios = list(col_crit6.value)
        df_c = L6["df_norm"][criterios].apply(pd.to_numeric, errors="coerce").fillna(0)
        children = []
        for crit in criterios:
            a_min, a_max = df_c[crit].min(), df_c[crit].max()
            bw = widgets.FloatText(value=round(a_min, 4), description=f"{crit} (b):", layout=widgets.Layout(width="350px"), style={"description_width": "120px"})
            dw = widgets.FloatText(value=round(a_max, 4), description=f"{crit} (d):", layout=widgets.Layout(width="350px"), style={"description_width": "120px"})
            rim_config_widgets[crit] = {"b": bw, "d": dw}
            children.append(widgets.VBox([widgets.HTML(f"<b>{crit}</b> [mín={a_min:.4f}, máx={a_max:.4f}]"), bw, dw]))
        rim_config_box.children = children

    btn_config_rim.on_click(_on_config_rim_click)

    def _load6(change):
        with upload6_out:
            clear_output()
            if not upload6.value: return
            key = list(upload6.value.keys())[0]
            fdata = upload6.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
                L6["df_norm"] = df
                cols = list(df.columns)
                col_alt6.options = cols; col_crit6.options = cols
                print(f"✅ {key}  |  {df.shape[0]} filas × {df.shape[1]} columnas")
                display(df.head())
            except Exception as e:
                print(f"❌ Error: {e}")

    upload6.observe(_load6, names="value")

    def _run6(b):
        with run6_out:
            clear_output()
            if L6["df_norm"] is None: print("❌ No hay matriz cargada."); return
            df_norm = L6["df_norm"]
            crit_cols = list(col_crit6.value)
            alt_col = col_alt6.value
            if not crit_cols or not alt_col: print("❌ Seleccioná criterios y alternativas."); return
            if not pesos_widgets or not rim_config_widgets: print("❌ Actualizá pesos y rangos ideales."); return

            pesos_dict = {c: pesos_widgets[c].value for c in crit_cols}
            suma_pesos = sum(pesos_dict.values())
            if suma_pesos == 0: print("❌ Suma de pesos es 0."); return
            pesos_norm = np.array([pesos_dict[c] / suma_pesos for c in crit_cols])

            df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
            matriz_vals = df_c.values
            r_matriz = np.zeros_like(matriz_vals, dtype=float)

            for j, crit in enumerate(crit_cols):
                col_vals = matriz_vals[:, j]
                a_minus, a_plus = col_vals.min(), col_vals.max()
                b_val = rim_config_widgets[crit]['b'].value
                d_val = rim_config_widgets[crit]['d'].value

                for i, val in enumerate(col_vals):
                    if b_val <= val <= d_val:
                        r_matriz[i, j] = 1.0
                    elif val < b_val:
                        r_matriz[i, j] = 1.0 - (b_val - val) / (b_val - a_minus) if a_minus != b_val else 1.0
                    elif val > d_val:
                        r_matriz[i, j] = 1.0 - (val - d_val) / (a_plus - d_val) if a_plus != d_val else 1.0

            r_matriz = np.clip(r_matriz, 0, 1)
            v_matriz = r_matriz * pesos_norm
            v_plus = pesos_norm.copy()
            v_minus = np.zeros(len(crit_cols))

            s_plus, _ = obtener_distancia_detallada(v_matriz, v_plus, distancia6.value)
            s_minus, _ = obtener_distancia_detallada(v_matriz, v_minus, distancia6.value)

            i_index = s_minus / (s_plus + s_minus + 1e-9)
            df_result = pd.DataFrame({"Alternativa": df_norm[alt_col].values, "S+": s_plus, "S-": s_minus, "I(i)": i_index})
            df_result["Ranking"] = df_result["I(i)"].rank(ascending=False, method="min").astype(int)
            df_result = df_result.sort_values("Ranking")

            display(HTML("<h2>Resultados RIM</h2>"))
            display(df_result.round(4))

    run6_btn.on_click(_run6)

    display(widgets.HTML("<h2>📊 LÍNEA 6 – RIM</h2>"))
    display(upload6, upload6_out)
    display(widgets.HBox([col_alt6, col_crit6]))
    display(btn_generar_pesos, pesos_box)
    display(btn_config_rim, rim_config_box)
    display(distancia6)
    display(run6_btn, run6_out)
