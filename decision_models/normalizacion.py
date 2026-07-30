import io, base64, warnings
import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML

warnings.filterwarnings("ignore")
pd.options.display.float_format = '{:.4f}'.format

def _norm_fraccion_max(df): 
    return df.div(df.max())

def _norm_fraccion_suma(df): 
    return df.div(df.sum())

def _norm_fraccion_rango(df, min_values=None, max_values=None):
    """
    Normalización de rango con opción de valores mín/máx personalizados.
    
    Si min_values y max_values son None, usa los valores reales de los datos.
    Si se proporcionan, usa esos valores personalizados.
    """
    if min_values is None:
        min_vals = df.min()
    else:
        min_vals = pd.Series(min_values)
    
    if max_values is None:
        max_vals = df.max()
    else:
        max_vals = pd.Series(max_values)
    
    rango = max_vals - min_vals
    return (df - min_vals).div(rango.replace(0, np.nan))

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

def run_normalizacion():
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

    # Nuevo: Box para parámetros de Fracción del Rango
    rango_box = widgets.VBox([])
    rango_inputs = {}

    # Antiguo: Box para parámetros de Ideal de referencia (RIM)
    rim_box = widgets.VBox([])
    rim_inputs = {}

    def _crear_rango_inputs(criterios):
        """Crea inputs para valores mín/máx personalizados en Fracción del Rango"""
        nonlocal rango_inputs
        children = []
        rango_inputs = {}
        
        for crit in criterios:
            if L2["df"] is not None and crit in L2["df"].columns:
                col_data = L2["df"][crit].dropna()
                sugerido_min = col_data.min() if len(col_data) else 0.0
                sugerido_max = col_data.max() if len(col_data) else 1.0
            else:
                sugerido_min, sugerido_max = 0.0, 1.0
            
            w_min = widgets.BoundedFloatText(value=round(sugerido_min, 4),
                                             min=-1e6, max=1e6, step=0.01,
                                             description=f'{crit[:15]} Mín:',
                                             layout=widgets.Layout(width='280px'))
            w_max = widgets.BoundedFloatText(value=round(sugerido_max, 4),
                                             min=-1e6, max=1e6, step=0.01,
                                             description='Máx:',
                                             layout=widgets.Layout(width='280px'))
            rango_inputs[crit] = (w_min, w_max)
            children.append(widgets.HBox([w_min, w_max]))
        
        rango_box.children = children

    def _crear_rim_inputs(criterios):
        """Crea inputs para parámetros Ideal de referencia (RIM)"""
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

    def _actualizar_visibilidad_parametros(*args):
        """Actualiza qué parámetros se muestran según el método seleccionado"""
        metodo = norm_method2.value
        
        # Mostrar Fracción del Rango si se selecciona ese método
        if metodo == "Fracción del rango":
            _crear_rango_inputs(col_crit2.value)
            rango_box.layout.display = ""
        else:
            rango_box.layout.display = "none"
        
        # Mostrar RIM si se selecciona ese método
        if metodo == "Ideal de referencia":
            _crear_rim_inputs(col_crit2.value)
            rim_box.layout.display = ""
        else:
            rim_box.layout.display = "none"

    norm_method2.observe(_actualizar_visibilidad_parametros, names="value")
    col_crit2.observe(_actualizar_visibilidad_parametros, names="value")

    def _load2(change):
        with upload2_out:
            clear_output()
            if not upload2.value: 
                return
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
                _actualizar_visibilidad_parametros()
            except Exception as e:
                print(f"❌ Error: {e}")

    upload2.observe(_load2, names="value")

    def _run2(b):
        with run2_out:
            clear_output()
            df = L2["df"]
            if df is None: 
                print("❌ Cargá un archivo primero.")
                return
            crit_cols = list(col_crit2.value)
            if not crit_cols: 
                print("❌ Seleccioná al menos un criterio.")
                return
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
                
                elif metodo == "Fracción del rango":
                    # Capturar valores personalizados de mín/máx
                    min_dict = {}
                    max_dict = {}
                    for crit in crit_cols:
                        w_min, w_max = rango_inputs[crit]
                        min_dict[crit] = w_min.value
                        max_dict[crit] = w_max.value
                    df_norm = _norm_fraccion_rango(df_c, min_values=min_dict, max_values=max_dict)
                
                else:
                    df_norm = NORM_METODOS[metodo](df_c)
            except Exception as e:
                print(f"❌ Error al normalizar: {e}")
                return

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
            if df_show is None: 
                print("❌ Normalizá primero.")
                return
            metodo = norm_method2.value
            display(_descargar_enlace(df_show, "matriz_normalizada.xlsx", "Normalizada", metodo))

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
    display(_sep("Parámetros para Fracción del Rango (valores mín/máx personalizados)"))
    display(rango_box)
    display(_sep("Parámetros para Ideal de referencia (RIM)"))
    display(rim_box)
    display(_sep("4. Normalizar"))
    display(run2_btn, run2_out)
    display(dl2_btn, dl2_out)
