def run_rim():
    #@title 📊 RIM - Reference Ideal Method
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

    # ============================================================
    # FUNCIONES AUXILIARES
    # ============================================================
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

    # ============================================================
    # WIDGETS Y CONTROLES
    # ============================================================
    upload6 = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False,
                                  description="📂 Subir matriz", button_style="primary")
    upload6_out = widgets.Output()

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

            L6["df_norm"] = df_l2.copy()
            cols = list(df_l2.columns)
            col_alt6.options = cols
            col_crit6.options = cols
            print(f"✅ Matriz importada desde Línea 2 | {df_l2.shape[0]} filas × {df_l2.shape[1]} columnas")
            display(df_l2.head())

    btn_desde_l2.on_click(_cargar_desde_l2)

    # ============================================================
    # RESTO DE WIDGETS
    # ============================================================
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

    # ============================================================
    # CALLBACKS
    # ============================================================
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
        criterios = list(col_crit6.value)
        if not criterios:
            with run6_out:
                clear_output()
                print("⚠️ Seleccioná al menos un criterio.")
            return
        _actualizar_campos_pesos(criterios)

    btn_generar_pesos.on_click(_on_generar_pesos_click)

    def _actualizar_config_rim(criterios):
        global rim_config_widgets
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
                df_ideales = pd.DataFrame({
                    "Criterio": crit_cols,
                    "v+": v_p,
                    "v-": v_m
                })
                display(df_ideales.round(4))

                display(HTML("<h3>Paso 6A: Calcular las distancias a la alternativa Ideal (S⁺)</h3>"))
                display(HTML("""<b>Fórmula:</b> S<sub>i</sub><sup>+</sup> = √[ Σ<sub>j=1</sub><sup>n</sup> (v<sub>ij</sub> - w<sub>j</sub>)<sup>2</sup> ]"""))

                display(HTML("<b>Matriz V:</b>"))
                display(df_v.round(4))

                display(HTML("<b>Alternativa v⁺:</b>"))
                display(pd.DataFrame({
                    "Criterio": crit_cols,
                    "v⁺": v_p
                }).T.round(4))

                display(HTML("<b>S⁺:</b>"))
                display(pd.DataFrame({
                    "Alternativa": L6["alternativas"],
                    "S⁺": df_result.set_index("Alternativa").loc[L6["alternativas"], "S+"]
                }).round(4))

                display(HTML("<h3>Paso 6B: Calcular las distancias a la alternativa Anti-ideal (S⁻)</h3>"))
                display(HTML("""<b>Fórmula:</b> S<sub>i</sub><sup>-</sup> = √[ Σ<sub>j=1</sub><sup>n</sup> (v<sub>ij</sub>)<sup>2</sup> ]"""))

                display(HTML("<b>Matriz V:</b>"))
                display(df_v.round(4))

                display(HTML("<b>Alternativa v⁻:</b>"))
                display(pd.DataFrame({
                    "Criterio": crit_cols,
                    "v⁻": v_m
                }).T.round(4))

                display(HTML("<b>S⁻:</b>"))
                display(pd.DataFrame({
                    "Alternativa": L6["alternativas"],
                    "S⁻": df_result.set_index("Alternativa").loc[L6["alternativas"], "S-"]
                }).round(4))

                display(HTML("<h3>Paso 7: Cálculo del índice y ordenamiento</h3>"))
                display(HTML("<i>Fórmula: I<sub>i</sub> = S<sub>i</sub><sup>-</sup> / (S<sub>i</sub><sup>+</sup> + S<sub>i</sub><sup>-</sup>)</i>"))
                display(HTML("<b>Índices y ranking:</b>"))
                display(df_result[["Alternativa", "S+", "S-", "I(i)", "Ranking"]].round(4))

                display(HTML("<h3>✅ Alternativas Ordenadas por Ranking (de mejor a peor)</h3>"))
                ranking_final = df_result[["Ranking", "Alternativa", "I(i)"]].sort_values("Ranking")
                display(ranking_final.round(4))

            except Exception as e:
                print(f"❌ Error en cálculos: {e}")
                import traceback
                traceback.print_exc()

    run6_btn.on_click(_run6)

    # ============================================================
    # MOSTRAR INTERFAZ
    # ============================================================
    display(widgets.HTML("""
    <h2 style='color: #2ca02c;'>📊 LÍNEA 6 – RIM</h2>
    <p><i>Reference Ideal Method</i></p>
    <p>Variante de TOPSIS que considera un rango ideal [b, d] para cada criterio.</p>
    """))

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

