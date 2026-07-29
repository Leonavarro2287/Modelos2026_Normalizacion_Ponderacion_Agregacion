import io, base64, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML

warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:.4f}'.format

L4 = {"df_norm": None, "df_show": None, "pesos": None, "df_agreg": None, "matriz_transform": None,
      "crit_cols": None, "alternativas": None}

def _sep(texto=""): return widgets.HTML(f"<hr><b>{texto}</b>")

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

def run_agregacion():
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
            try:
                from .normalizacion import L2
                df_l2 = L2.get("df_show")
            except ImportError:
                df_l2 = None

            if df_l2 is not None:
                df_l2 = df_l2.copy()
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
                    print("⚠️ No se encontró L2. Ejecutá primero la función de Normalización.")

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
                    df_trans = pd.DataFrame(L4["matriz_transform"], columns=crit_cols, index=alternativas).round(4)
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
