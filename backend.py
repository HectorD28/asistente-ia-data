import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import json
import contextlib
import traceback
import textwrap

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================================
# 1. HERRAMIENTA DE EJECUCIÓN (Igual que en el Notebook)
# =========================================
def run_python_tool(code: str):
    local_dfs = st.session_state.get("dataframes", {})
    global_namespace = {"dataframes": local_dfs, "pd": pd, "plt": plt}
    local_namespace = {}
    buf = io.StringIO()
    generated_images = []

    try:
        plt.clf()
        plt.close('all')
        with contextlib.redirect_stdout(buf):
            exec(code, global_namespace, local_namespace)
            if plt.get_fignums():
                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png', bbox_inches='tight')
                img_buf.seek(0)
                generated_images.append(img_buf)
                plt.close('all')
    except Exception:
        return f"❌ Error:\n{traceback.format_exc()}", []

    output_text = buf.getvalue()
    if not output_text.strip() and not generated_images:
        output_text = "(Código ejecutado sin salida)."
    return output_text, generated_images

# Definición de la herramienta
tools = [{
    "type": "function",
    "function": {
        "name": "run_python",
        "description": "Ejecuta código Python sobre 'dataframes'.",
        "parameters": {
            "type": "object",
            "properties": {"code": {"type": "string", "description": "Código Python."}},
            "required": ["code"],
        },
    },
}]

# =========================================
# 2. GESTIÓN DE ESTADO Y MENSAJES
# =========================================

def inicializar_chat():
    """Configura el prompt del sistema idéntico al Colab"""
    if "messages" not in st.session_state:
        # Tomado textualmente del Notebook subido
        system_prompt = textwrap.dedent("""
            Eres un asistente virtual de ciencia de datos que trabaja dentro de un cuaderno de Google Colab.
            Dispones de una herramienta llamada 'run_python' que ejecuta código Python sobre los datasets
            cargados en la variable global 'dataframes' (dict nombre->DataFrame).

            OBJETIVO GENERAL:
            - Ayudar al usuario a explorar, entender y visualizar datasets en formato CSV.

            COMPORTAMIENTO:

            1. ANÁLISIS EXPLORATORIO INICIAL
            Cuando se cargue un nuevo dataset y el usuario te lo indique:
            - - `dataframes['nombre_del_dataset'].info()` para tipos de datos y nulos.
            - `dataframes['nombre_del_dataset'].describe()` para estadísticas descriptivas.
            - `dataframes['nombre_del_dataset'].isnull().sum()` para un conteo claro de valores nulos.
            - `dataframes['nombre_del_dataset'].columns` para listar las columnas.
            NO intentes usar librerías como `pandas_profiling` o `ydata_profiling`. Realiza el análisis manualmente con los comandos indicados.


            2. PREGUNTAS EN LENGUAJE NATURAL
            - El usuario puede pedir distribuciones, filtros, comparaciones, correlaciones, etc.
            - Siempre que necesites un número, cálculo o gráfico, usa la herramienta 'run_python'.
            - No inventes valores; apóyate en el código ejecutado sobre 'dataframes'.
            - Después de usar la herramienta, explica en lenguaje natural lo que significan los resultados.

            3. SUGERENCIAS INTELIGENTES DE VISUALIZACIONES
            - Propón de forma proactiva gráficos adecuados según el tipo de variables:
                * Histogramas para distribuciones numéricas.
                * Boxplots para analizar outliers y comparaciones entre grupos.
                * Gráficos de barras para variables categóricas.
                * Scatter plots para relaciones entre dos variables numéricas.
                * Heatmaps de correlación cuando sea relevante.
            - Para cada gráfico sugerido, explica qué información aportaría.
            - NO generes el gráfico automáticamente: primero pregunta si el usuario quiere verlo.
            - Sólo si el usuario acepta, llama a 'run_python' con el código Python para construir el gráfico usando SIEMPRE la librería `matplotlib`.

            4. INTERACCIÓN
            - Mantén una conversación clara y pedagógica.
            - Sugiere análisis adicionales cuando sea útil, pero sin abrumar.
            - Pide aclaraciones sólo si la petición es ambigua.

            5. MULTIMODALIDAD
            - Los gráficos generados con matplotlib se mostrarán en el notebook junto a tus respuestas.
            - Describe cada gráfico que generes para que el usuario pueda relacionar texto e imagen.

            6. BUENAS PRÁCTICAS AL USAR 'run_python'
            - No instales paquetes nuevos ni accedas a internet.
            - Usa sólo pandas, numpy (si está disponible) y matplotlib.
            - Para acceder a un DataFrame, SIEMPRE usa la sintaxis de diccionario: `dataframes['nombre_del_dataset']`. Por ejemplo: `print(dataframes['ventas'].head())`.
            - Escribe código claro y comentado cuando sea posible.

            7. MANEJO DE ERRORES
            - Si la herramienta 'run_python' devuelve un error, NO te disculpes ni asumas que las librerías no están disponibles. El entorno está configurado correctamente.
            - Lee atentamente el mensaje de error (traceback) que se te proporciona como resultado de la herramienta.
            - El error se debe a un problema en el código que TÚ generaste. Tu tarea es DEPURARLO.
            - Corrige el código basándote en el error y vuelve a llamar a 'run_python' inmediatamente en el siguiente paso. Un error común es usar un nombre de variable de DataFrame incorrecto (ej. `df.head()`) en lugar de la sintaxis correcta (`dataframes['nombre_del_dataset'].head()`).
       
        """).strip()
        st.session_state.messages = [{"role": "system", "content": system_prompt}]

def generar_prompt_inicial_automatico():
    """Genera el mensaje que detona el análisis automático"""
    local_dfs = st.session_state.get("dataframes", {})
    desc = []
    for name, df in local_dfs.items():
        desc.append(f"- {name}: {df.shape[0]} filas, {df.shape[1]} columnas.")
    
    desc_texto = "\n".join(desc)
    
    # Este es el prompt que fuerza al modelo a sugerir cosas (como en el notebook)
    return f"""
    He cargado los siguientes datasets en 'dataframes':
    {desc_texto}
    
    Por favor, realiza un ANÁLISIS EXPLORATORIO INICIAL completo y sugiere 3 visualizaciones relevantes.
    Recuerda acceder a los dataframes usando la sintaxis de diccionario, por ejemplo: `dataframes['{list(local_dfs.keys())[0]}'].head()`.
    """

def procesar_mensaje(user_msg):
    st.session_state.messages.append({"role": "user", "content": user_msg})
    
    # Crear una copia de los mensajes apta para la API (sin datos de imagen)
    api_messages = []
    for msg in st.session_state.messages:
        msg_copy = msg.copy()
        msg_copy.pop("images", None) # Eliminar la clave 'images' si existe
        api_messages.append(msg_copy)

    # Lógica de Chat Completion con Bucle de Herramientas
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=api_messages,
        tools=tools,
        tool_choice="auto"
    )
    
    msg = response.choices[0].message
    tool_outputs = []
    generated_images_for_this_turn = [] # Almacena imágenes solo para esta respuesta

    if msg.tool_calls:
        st.session_state.messages.append(msg.model_dump()) # Añadir intención de tool como dict
        for tool in msg.tool_calls:
            if tool.function.name == "run_python":
                args = json.loads(tool.function.arguments)
                out_txt, imgs = run_python_tool(args["code"])
                
                # Guardar imágenes generadas en este turno
                generated_images_for_this_turn.extend(imgs)
                
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "role": "tool",
                    "name": "run_python",
                    "content": out_txt
                })
        
        st.session_state.messages.extend(tool_outputs)
        
        # Segunda llamada para que el modelo interprete la salida
        final_res = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages
        )
        final_content = final_res.choices[0].message.content
    else:
        final_content = msg.content

    # Asociar el contenido y las imágenes a un solo mensaje
    assistant_message = {"role": "assistant", "content": final_content, "images": generated_images_for_this_turn}
    st.session_state.messages.append(assistant_message)
    
    return final_content, generated_images_for_this_turn

def cargar_dataset_local(uploaded_file):
    """
    Lee un archivo subido (CSV o Excel) y lo convierte en DataFrame.
    Devuelve: (nombre_del_dataset, dataframe)
    """
    try:
        # Obtener el nombre sin extensión (ej: "ventas.csv" -> "ventas")
        name = uploaded_file.name.split('.')[0]
        
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            return None, None, "Formato no soportado. Usa CSV o Excel."
            
        return name, df, None
        
    except Exception as e:
        return None, None, f"Error al leer el archivo: {str(e)}"