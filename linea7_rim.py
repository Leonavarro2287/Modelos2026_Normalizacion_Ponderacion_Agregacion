import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import io, warnings
warnings.filterwarnings("ignore")

pd.options.display.float_format = '{:.4f}'.format

def normalizar_rim(matriz_vals, crit_cols, rim_config):
    n_rows, n_cols = matriz_vals.shape
    r_matriz = np.zeros_like(matriz_vals, dtype=float)
    for j, crit in enumerate(crit_cols):
        col_vals = matriz_vals[:, j]
        a_minus = col_vals.min(); a_plus = col_vals.max()
        config = rim_config.get(crit, {})
        b = config.get('b', a_minus); d = config.get('d', a_plus)
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
    return np.clip(r_matriz, 0, 1)

def dist_euclidea(v_i, v_ref):
    d = v_i - v_ref; return np.sqrt((d**2).sum(axis=1)), d**2

def dist_ciudad(v_i, v_ref):
    d = np.abs(v_i - v_ref); return d.sum(axis=1), d**2

def dist_tchebycheff(v_i, v_ref):
    d = np.abs(v_i - v_ref); return np.max(d, axis=1), d**2

def obtener_dist(v_i, v_ref, tipo):
    return {"euclidea": dist_euclidea, "ciudad": dist_ciudad,
            "tchebycheff": dist_tchebycheff}.get(tipo, dist_euclidea)(v_i, v_ref)

def run_rim():
    L6 = {"df_norm": None}

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

    upload6 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                  description="📂 Subir matriz", button_style="primary")
    upload6_out = widgets.Output()

    col_alt6 = widgets.Dropdown(description="Alternativas:", options=[],
                                 style={"description_width": "110px"},
                                 layout=widgets.Layout(width="320px"))
    col_crit6 = widgets.SelectMultiple(description="Criterios:", options=[],
                                        layout=widgets.Layout(height="140px", width="380px"),
                                        style={"description_width": "80px"})

    pesos_box = widgets.VBox([])
    pesos_widgets = {}
    btn_generar_pesos = widgets.Button(description="🔄 Actualizar pesos", button_style="info",
                                       layout=widgets.Layout(width="220px"))

    rim_config_box = widgets.VBox([])
    rim_config_widgets = {}
    btn_config_rim = widgets.Button(description="⚙️ Configurar rangos ideales [b,d]",
                                   button_style="warning", layout=widgets.Layout(width="280px"))

    distancia6 = widgets.Dropdown(
        options=[("Euclidea (p=2)", "euclidea"),
                 ("Ciudad/Manhattan (p=1)", "ciudad"),
                 ("Tchebycheff (p=∞)", "tchebycheff")],
        value="euclidea", description="Distancia:",
        style={"description_width": "130px"}, layout=widgets.Layout(width="380px"))

    run6_btn = widgets.Button(description="▶ Ejecutar RIM", button_style="success",
                              layout=widgets.Layout(width="240px"))
    run6_out = widgets.Output()

    def _actualizar_campos_pesos(criterios):
        pesos_widgets.clear()
        n = len(criterios); valor_inicial = 1.0 / n if n > 0 else 0
        children = []
        for crit in criterios:
            w = widgets.FloatText(value=round(valor_inicial, 4), min=0, max=1e6, step=0.01,
                                  description=f'{crit[:15]}:', layout=widgets.Layout(width='300px'))
            pesos_widgets[crit] = w; children.append(w)
        pesos_box.children = children

    btn_generar_pesos.on_click(lambda b: _actualizar_campos_pesos(list(col_crit6.value)) if col_crit6.value else None)

    def _actualizar_config_rim(criterios):
        nonlocal rim_config_widgets
        rim_config_widgets = {}
        if L6["df_norm"] is None: return
        df_c = L6["df_norm"][criterios].apply(pd.to_numeric, errors="coerce").fillna(0)
        children = [widgets.HTML("<b>Rango ideal [b, d] por criterio</b><br>"
                                 "<i>Valores dentro de [b, d] → normalización = 1.0</i><br>")]
        for crit in criterios:
            a_min = df_c[crit].min(); a_max = df_c[crit].max()
            b_widget = widgets.FloatText(value=round(a_min, 4), description=f"{crit} (b):",
                                         layout=widgets.Layout(width="350px"), style={"description_width": "120px"})
            d_widget = widgets.FloatText(value=round(a_max, 4), description=f"{crit} (d):",
                                         layout=widgets.Layout(width="350px"), style={"description_width": "120px"})
            rim_config_widgets[crit] = {"b": b_widget, "d": d_widget}
            children.append(widgets.VBox([
                widgets.HTML(f"<b>{crit}</b> — Rango datos: [{a_min:.4f}, {a_max:.4f}]"),
                b_widget, d_widget]))
        rim_config_box.children = children

    btn_config_rim.on_click(lambda b: _actualizar_config_rim(list(col_crit6.value)) if col_crit6.value else None)

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
            if not crit_cols: print("❌ Seleccioná al menos un criterio."); return
            alt_col = col_alt6.value
            if not alt_col or alt_col not in df_norm.columns: print("❌ Seleccioná alternativas válidas."); return
            if not pesos_widgets: print("❌ Primero actualizá los pesos."); return
            try:
                pesos_dict = {c: pesos_widgets[c].value for c in crit_cols}
            except KeyError:
                print("❌ Los criterios cambiaron. Volvé a actualizar pesos."); return
            suma_pesos = sum(pesos_dict.values())
            if suma_pesos == 0: print("❌ La suma de pesos no puede ser 0."); return
            pesos_norm = np.array([pesos_dict[c] / suma_pesos for c in crit_cols])
            if not rim_config_widgets: print("❌ Primero configurá los rangos ideales."); return
            rim_config = {crit: {'b': rim_config_widgets[crit]['b'].value,
                                  'd': rim_config_widgets[crit]['d'].value}
                          for crit in crit_cols if crit in rim_config_widgets}
            distancia = distancia6.value

            try:
                df_c = df_norm[crit_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
                if np.any(df_c.values < 0): df_c = df_c - df_c.min() + 1
                alternativas = df_norm[alt_col].values
                r_mat = normalizar_rim(df_c.values, crit_cols, rim_config)
                v_mat = r_mat * pesos_norm
                v_plus = pesos_norm.copy(); v_minus = np.zeros(len(crit_cols))
                s_plus, dp = obtener_dist(v_mat, v_plus, distancia)
                s_minus, dm = obtener_dist(v_mat, v_minus, distancia)
                i_index = s_minus / (s_plus + s_minus + 1e-9)
                df_result = pd.DataFrame({"Alternativa": alternativas, "S+": s_plus, "S-": s_minus, "I(i)": i_index})
                df_result["Ranking"] = df_result["I(i)"].rank(ascending=False, method="min").astype(int)
                df_result = df_result.sort_values("Ranking")

                display(HTML("<h2>RIM – Cálculo Detallado</h2>"))
                display(HTML("<h3>Paso 1: Datos originales y rangos ideales</h3>"))
                df_paso1 = df_c.copy(); df_paso1.insert(0, alt_col, alternativas)
                display(df_paso1.round(4))
                stats_data = {alt_col: ["aᵢ (mín)", "aᵢ (máx)", "b", "d"]}
                for crit in crit_cols:
                    b = rim_config[crit]['b']; d = rim_config[crit]['d']
                    stats_data[crit] = [round(df_c[crit].min(),4), round(df_c[crit].max(),4), round(b,4), round(d,4)]
                df_stats = pd.DataFrame(stats_data).T; df_stats.columns = ["aᵢ (mín)", "aᵢ (máx)", "b", "d"]
                display(df_stats.round(4))

                display(HTML("<h3>Paso 2: Matriz Normalizada (R) – RIM</h3>"))
                display(pd.DataFrame(r_mat, columns=crit_cols, index=alternativas).round(4))
                display(HTML("<h3>Paso 3: Pesos Normalizados</h3>"))
                display(pd.DataFrame(pesos_norm.reshape(1,-1), columns=crit_cols).round(4))
                display(HTML("<h3>Paso 4: Matriz Ponderada (V = W·R)</h3>"))
                display(pd.DataFrame(v_mat, columns=crit_cols, index=alternativas).round(4))
                display(HTML("<h3>Paso 5: v+ (pesos) y v- (ceros)</h3>"))
                display(pd.DataFrame({"Criterio": crit_cols, "v+": v_plus, "v-": v_minus}).round(4))
                display(HTML("<h3>Paso 6: Distancias S+ y S-</h3>"))
                display(pd.DataFrame({"Alternativa": alternativas, "S+": s_plus, "S-": s_minus}).round(4))
                display(HTML("<h3>Paso 7: Índice I(i) y Ranking</h3>"))
                display(HTML("<i>I(i) = S⁻ / (S⁺ + S⁻)</i>"))
                display(df_result[["Alternativa","S+","S-","I(i)","Ranking"]].round(4))
                display(HTML("<h3>✅ Ranking Final</h3>"))
                display(df_result[["Ranking","Alternativa","I(i)"]].sort_values("Ranking").round(4))
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback; traceback.print_exc()

    run6_btn.on_click(_run6)

    display(widgets.HTML("""
<h2 style='color: #2ca02c;'>📊 LÍNEA 7 – RIM</h2>
<p><i>Reference Ideal Method – Variante de TOPSIS con rango ideal [b, d] por criterio</i></p>
"""))
    display(_sep("1️⃣ Cargar archivo"))
    display(upload6, upload6_out)
    display(_sep("2️⃣ Seleccionar columnas"))
    display(widgets.HBox([col_alt6, col_crit6]))
    display(_sep("3️⃣ Pesos"))
    display(btn_generar_pesos); display(pesos_box)
    display(_sep("4️⃣ Configurar rango ideal [b, d]"))
    display(btn_config_rim); display(rim_config_box)
    display(_sep("5️⃣ Distancia"))
    display(distancia6)
    display(_sep("6️⃣ Ejecutar"))
    display(run6_btn, run6_out)
