import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import io, warnings
import matplotlib.pyplot as plt
from itertools import combinations
warnings.filterwarnings("ignore")

pd.options.display.float_format = '{:.4f}'.format

def run_ahp():
    AHP = {
        'criterios': [], 'alternativas': [],
        'matriz_criterios': None, 'pesos_criterios': None,
        'consistencia_criterios': None, 'matrices_alternativas': {},
        'pesos_alternativas': {}, 'global': None,
        'ia_table': {1:0.00,2:0.00,3:0.58,4:0.90,5:1.12,6:1.24,7:1.32,
                     8:1.41,9:1.45,10:1.49,11:1.51,12:1.54,13:1.56,14:1.57,15:1.59},
        'comparaciones_criterios': {}, 'comparaciones_alternativas': {}
    }

    escala_html = HTML("""
<b>Escala Fundamental de Saaty:</b><br>
1 = Igualmente importante | 3 = Moderadamente importante | 5 = Notablemente importante<br>
7 = Muchísimo más importante | 9 = Absolutamente más importante<br>
(2, 4, 6, 8 = valores intermedios)
""")

    def construir_matriz_desde_pares(elementos, pares_info):
        n = len(elementos)
        matriz = np.ones((n, n))
        for (i, j), (mas_imp, val) in pares_info.items():
            if val <= 0: val = 1.0
            if mas_imp == 0:
                matriz[i, j] = val; matriz[j, i] = 1.0 / val
            else:
                matriz[i, j] = 1.0 / val; matriz[j, i] = val
        return matriz

    def calcular_pesos_y_normalizacion(matriz):
        col_sums = matriz.sum(axis=0)
        col_sums[col_sums == 0] = 1e-9
        norm_mat = matriz / col_sums
        pesos = norm_mat.mean(axis=1)
        return pesos, col_sums, norm_mat

    def calcular_consistencia(matriz, pesos):
        n = len(matriz)
        Aw = matriz @ pesos
        lambda_max = np.mean(Aw / pesos)
        IC = (lambda_max - n) / (n - 1) if n > 1 else 0
        IA = AHP['ia_table'].get(n, 1.59)
        RC = IC / IA if IA != 0 else 0
        return {'lambda_max': lambda_max, 'IC': IC, 'RC': RC, 'n': n, 'IA': IA}

    def mostrar_matriz_completa(matriz, elementos, titulo):
        pesos, col_sums, norm_mat = calcular_pesos_y_normalizacion(matriz)
        display(HTML(f"<b>{titulo}</b>"))
        display(HTML("<b>Matriz de comparación:</b>"))
        display(pd.DataFrame(matriz, index=elementos, columns=elementos).round(4))
        display(HTML("<b>Sumas por columna:</b>"))
        display(pd.DataFrame(col_sums.reshape(1, -1), columns=elementos).round(4))
        display(HTML("<b>Matriz normalizada:</b>"))
        display(pd.DataFrame(norm_mat, index=elementos, columns=elementos).round(4))
        display(HTML("<b>Pesos (promedio de filas):</b>"))
        display(pd.DataFrame(pesos, index=elementos, columns=["Peso"]).round(4))
        return pesos

    upload_file = widgets.FileUpload(accept=".xlsx,.xls,.csv", multiple=False, description="Subir archivo")
    upload_out = widgets.Output()
    propósito_input = widgets.Text(value="Selección de la mejor alternativa", description="Propósito:")
    btn_confirmar = widgets.Button(description="Confirmar y construir árbol", button_style="info")
    arbol_out = widgets.Output()
    btn_criterios = widgets.Button(description="📝 Comparación de criterios", button_style="warning")
    crit_out = widgets.Output()
    btn_alternativas = widgets.Button(description="📝 Comparación de alternativas", button_style="warning")
    alt_out = widgets.Output()
    btn_ejecutar = widgets.Button(description="▶ Ejecutar AHP", button_style="success")
    resultados_out = widgets.Output()

    def on_upload(change):
        with upload_out:
            clear_output()
            if not upload_file.value: return
            key = list(upload_file.value.keys())[0]
            fdata = upload_file.value[key]["content"]
            try:
                df = pd.read_csv(io.BytesIO(fdata), header=None) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata), header=None)
            except:
                df = pd.read_csv(io.BytesIO(fdata)) if key.endswith(".csv") else pd.read_excel(io.BytesIO(fdata))
            display(HTML("<b>Vista del archivo cargado:</b>"))
            display(df.head())
            display(HTML("<i>Primera columna: alternativas | Segunda columna: criterios (uno por fila).</i>"))
            upload_file.df = df
            print("✅ Archivo cargado. Ingresá el propósito y presioná 'Confirmar y construir árbol'.")

    upload_file.observe(on_upload, names='value')

    def construir_arbol(b):
        with arbol_out:
            clear_output()
            if not hasattr(upload_file, 'df'): print("❌ Primero subí un archivo."); return
            df = upload_file.df
            alternativas = list(dict.fromkeys([a.strip() for a in df.iloc[:, 0].dropna().astype(str).tolist() if a.strip()]))
            criterios = list(dict.fromkeys([c.strip() for c in df.iloc[:, 1].dropna().astype(str).tolist() if c.strip()]))
            if not alternativas or not criterios: print("❌ No se encontraron suficientes datos."); return
            AHP['alternativas'] = alternativas; AHP['criterios'] = criterios
            display(HTML(f"<h3>Árbol jerárquico</h3>"))
            display(HTML(f"<b>Propósito:</b> {propósito_input.value}"))
            display(HTML(f"<b>Criterios ({len(criterios)}):</b> {', '.join(criterios)}"))
            display(HTML(f"<b>Alternativas ({len(alternativas)}):</b> {', '.join(alternativas)}"))

    btn_confirmar.on_click(construir_arbol)

    def crear_interfaz_dropdown(elementos, titulo, callback_guardar, tipo, crit_nombre=None):
        n = len(elementos)
        pares = list(combinations(range(n), 2))
        pares_nombres = [(elementos[i], elementos[j]) for i, j in pares]
        widgets_info = {}; rows = []
        header = widgets.HBox([
            widgets.Label(value="Comparación en pares", layout=widgets.Layout(width='350px')),
            widgets.Label(value="Criterio más importante", layout=widgets.Layout(width='200px')),
            widgets.Label(value="Intensidad (1-9)", layout=widgets.Layout(width='150px'))
        ])
        rows.append(header)
        for (i, j), (nom_i, nom_j) in zip(pares, pares_nombres):
            label = widgets.Label(value=f"{nom_i} - {nom_j}", layout=widgets.Layout(width='350px'))
            dropdown = widgets.Dropdown(options=[(nom_i, 0), (nom_j, 1)], value=0, layout=widgets.Layout(width='200px'))
            intensidad = widgets.FloatText(value=1.0, min=1, max=9, step=1.0, layout=widgets.Layout(width='150px'))
            rows.append(widgets.HBox([label, dropdown, intensidad]))
            widgets_info[(i, j)] = (dropdown, intensidad)
        boton = widgets.Button(description="Generar matriz", button_style="success")
        output_area = widgets.Output()
        display(widgets.VBox([widgets.VBox(rows), boton, output_area]))

        def on_click(b):
            with output_area:
                clear_output()
                pares_data = {}
                comparaciones_guardado = {}
                for (i, j), (drop, val) in widgets_info.items():
                    mas_imp = drop.value
                    nombre_mas_imp = elementos[i] if mas_imp == 0 else elementos[j]
                    comparaciones_guardado[(elementos[i], elementos[j])] = (nombre_mas_imp, val.value)
                    pares_data[(i, j)] = (mas_imp, val.value)
                if tipo == 'criterios':
                    AHP['comparaciones_criterios'] = comparaciones_guardado
                else:
                    AHP['comparaciones_alternativas'][crit_nombre] = comparaciones_guardado
                matriz = construir_matriz_desde_pares(elementos, pares_data)
                pesos = mostrar_matriz_completa(matriz, elementos, f"Matriz de comparación {titulo}")
                cons = calcular_consistencia(matriz, pesos)
                print(f"λmax = {cons['lambda_max']:.4f}, IC = {cons['IC']:.4f}, RC = {cons['RC']:.4f}")
                if cons['RC'] <= 0.10: print("✅ RC ≤ 0.10 → Juicios consistentes.")
                else: print("⚠️ RC > 0.10 → Juicios inconsistentes. Revisar las comparaciones.")
                callback_guardar(matriz, pesos, cons)

        boton.on_click(on_click)

    def ingresar_criterios(b):
        with crit_out:
            clear_output()
            crits = AHP.get('criterios', [])
            if not crits: print("❌ Primero construye el árbol."); return
            display(HTML("<h3>Comparaciones pareadas de criterios</h3>"))
            display(escala_html)
            def guardar_crit(matriz, pesos, cons):
                AHP['matriz_criterios'] = matriz
                AHP['pesos_criterios'] = pesos
                AHP['consistencia_criterios'] = cons
            crear_interfaz_dropdown(crits, "de criterios", guardar_crit, tipo='criterios')

    btn_criterios.on_click(ingresar_criterios)

    def ingresar_alternativas(b):
        with alt_out:
            clear_output()
            crits = AHP.get('criterios', []); alts = AHP.get('alternativas', [])
            if not crits or not alts: print("❌ Primero construye el árbol."); return
            display(HTML("<h3>Comparaciones de alternativas por cada criterio</h3>"))
            display(escala_html)
            outputs_por_criterio = []
            for crit in crits:
                out_crit = widgets.Output()
                with out_crit:
                    clear_output()
                    display(HTML(f"<h4>Criterio: {crit}</h4>"))
                    def guardar_alt(matriz, pesos, cons, c=crit):
                        AHP['matrices_alternativas'][c] = matriz
                        AHP['pesos_alternativas'][c] = pesos
                        AHP.setdefault('consistencia_alternativas', {})[c] = cons
                    crear_interfaz_dropdown(alts, f"de alternativas para {crit}", guardar_alt, tipo='alternativas', crit_nombre=crit)
                    display(HTML("<hr>"))
                outputs_por_criterio.append(out_crit)
            display(widgets.VBox(outputs_por_criterio))

    btn_alternativas.on_click(ingresar_alternativas)

    def ejecutar_ahp(b):
        with resultados_out:
            clear_output()
            if AHP['pesos_criterios'] is None:
                print("❌ Primero genera la matriz de criterios."); return
            criterios_faltantes = [c for c in AHP['criterios'] if c not in AHP['pesos_alternativas']]
            if criterios_faltantes:
                print(f"❌ Faltan matrices de alternativas para: {', '.join(criterios_faltantes)}"); return
            crits = AHP['criterios']; alts = AHP['alternativas']
            pesos_crit = AHP['pesos_criterios']
            prioridades_locales = np.zeros((len(alts), len(crits)))
            for j, crit in enumerate(crits):
                prioridades_locales[:, j] = AHP['pesos_alternativas'][crit]
            puntuacion = prioridades_locales @ pesos_crit
            df = pd.DataFrame({"Alternativa": alts, "Puntuación": puntuacion})
            df["Ranking"] = df["Puntuación"].rank(ascending=False, method="min").astype(int)
            df = df.sort_values("Ranking")
            AHP['global'] = df
            display(HTML("<h2>Resultado final AHP</h2>"))
            display(df.round(4))
            fig, ax = plt.subplots(figsize=(8, max(4, len(alts)*0.4)))
            colores = plt.cm.viridis(np.linspace(0.2, 0.9, len(df)))
            ax.barh(df["Alternativa"], df["Puntuación"], color=colores)
            ax.set_xlabel("Prioridad global"); ax.set_title("Ranking AHP"); ax.invert_yaxis()
            for i, (val, alt) in enumerate(zip(df["Puntuación"], df["Alternativa"])):
                ax.text(val + 0.01*df["Puntuación"].max(), i, f"{val:.4f}", va="center")
            plt.tight_layout(); plt.show()

    btn_ejecutar.on_click(ejecutar_ahp)

    display(HTML("<h1>📊 LÍNEA 5 – Proceso Analítico Jerárquico (AHP)</h1>"))
    display(HTML("<b>1. Cargar archivo y definir propósito</b>"))
    display(HTML("<i>Archivo: dos columnas sin encabezado. Primera: alternativas, segunda: criterios.</i>"))
    display(upload_file, upload_out)
    display(HTML("Propósito del árbol:"))
    display(propósito_input)
    display(btn_confirmar, arbol_out)
    display(HTML("<b>2. Comparación de criterios</b>"))
    display(btn_criterios, crit_out)
    display(HTML("<b>3. Comparación de alternativas por cada criterio</b>"))
    display(btn_alternativas, alt_out)
    display(HTML("<b>4. Resultados</b>"))
    display(btn_ejecutar, resultados_out)
