def run_topsis():
    #@title 📊 TOPSIS - Technique for Order Preference by Similarity to Ideal Solution
    # !pip install openpyxl -q  (dependencia ya incluida en el paquete)

    import numpy as np
    import pandas as pd
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    import io, base64, warnings
    warnings.filterwarnings("ignore")

    pd.options.display.float_format = '{:.4f}'.format

    # ============================================================
    # VARIABLES GLOBALES
    # ============================================================
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

    # ============================================================
    # FUNCIONES DE NORMALIZACIÓN
    # ============================================================
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

    # ============================================================
    # FUNCIONES DE DISTANCIA CON DETALLE
    # ============================================================
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
        """Distancia: sqrt( Σ |dif| ) """
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

    # ============================================================
    # FUNCIÓN PRINCIPAL TOPSIS
    # ============================================================
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

    # ============================================================
    # WIDGETS Y CONTROLES
    # ============================================================
    upload5 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                  description="📂 Subir matriz", button_style="primary")
    upload5_out = widgets.Output()

    # ============================================================
    # BOTÓN PARA IMPORTAR DESDE LÍNEA 2
    # ============================================================
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

    # ============================================================
    # RESTO DE WIDGETS
    # ============================================================
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

    # Widget de recomendaciones
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
        global rim_inputs
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

    # ============================================================
    # CALLBACKS
    # ============================================================
    def _actualizar_tipos_criterio(criterios):
        global tipo_crit_widgets
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
        global pesos_widgets
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

            # Usar la misma distancia para ambos lados
            dist_ideal = distancia_opt
            dist_antideal = distancia_opt

            # Etiqueta para mostrar
            if distancia_opt == "raiz_manhattan":
                etiqueta_dist = "Raíz de Manhattan: S = √( Σ|Vij - Vj| )"
            elif distancia_opt == "euclidea":
                etiqueta_dist = "Euclídea: S = √( Σ (Vij - Vj)² )"
            elif distancia_opt == "ciudad":
                etiqueta_dist = "Manhattan: S = Σ |Vij - Vj|"
            elif distancia_opt == "tchebycheff":
                etiqueta_dist = "Tchebycheff: S = max|Vij - Vj|"
            else:
                etiqueta_dist = distancia_opt

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

                # ===== PASO 6A: Cálculo de Distancias al Ideal =====
                display(HTML("<h3>Paso 6A: Calcular las distancias a la alternativa Ideal (S⁺)</h3>"))
                display(HTML("""<b>Fórmula:</b> S<sub>i</sub><sup>+</sup> = √[ Σ<sub>j=1</sub><sup>n</sup> (V<sub>ij</sub> - V<sub>j</sub><sup>+</sup>)<sup>2</sup> ]"""))

                display(HTML("<b>Matriz V:</b>"))
                display(df_v.round(4))

                display(HTML("<b>Alternativa v⁺:</b>"))
                display(pd.DataFrame({
                    "Criterio": crit_cols,
                    "v⁺": v_p
                }).T.round(4))

                display(HTML("<b>S⁺:</b>"))
                display(pd.DataFrame({
                    "Alternativa": L5["alternativas"],
                    "S⁺": df_result.set_index("Alternativa").loc[L5["alternativas"], "S+"]
                }).round(4))

                # ===== PASO 6B: Cálculo de Distancias al Anti-Ideal =====
                display(HTML("<h3>Paso 6B: Calcular las distancias a la alternativa Anti-ideal (S⁻)</h3>"))
                display(HTML("""<b>Fórmula:</b> S<sub>i</sub><sup>-</sup> = √[ Σ<sub>j=1</sub><sup>n</sup> (V<sub>ij</sub> - V<sub>j</sub><sup>-</sup>)<sup>2</sup> ]"""))

                display(HTML("<b>Matriz V:</b>"))
                display(df_v.round(4))

                display(HTML("<b>Alternativa v⁻:</b>"))
                display(pd.DataFrame({
                    "Criterio": crit_cols,
                    "v⁻": v_m
                }).T.round(4))

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

    def obtener_normalizacion(df, tipo, rim_config=None):
        """Aplica el método de normalización seleccionado"""
        if tipo == "Ideal de referencia":
            return _norm_ideal_ref(df, rim_config or {})
        elif tipo in NORM_METODOS and NORM_METODOS[tipo] is not None:
            return NORM_METODOS[tipo](df)
        else:
            return _norm_vector(df)

    # ============================================================
    # MOSTRAR INTERFAZ
    # ============================================================
    display(widgets.HTML("""
    <h2 style='color: #1f77b4;'>📊 LÍNEA 5 – TOPSIS</h2>
    <p><i>Technique for Order Preference by Similarity to Ideal Solution</i></p>
    <p>Elige la mejor alternativa encontrando la más cercana a la solución ideal y la más lejana de la anti-ideal.</p>
    """))

    def _sep(texto=""):
        return widgets.HTML(f"<hr><b>{texto}</b>")

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

