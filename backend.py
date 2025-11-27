import openai
import time
import streamlit as st

# Inicializar cliente con la clave de los secretos
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def subir_archivo_openai(uploaded_file):
    """Sube el archivo a OpenAI y devuelve el File ID"""
    try:
        # OpenAI espera un archivo binario con nombre, Streamlit nos da un Buffer
        # Necesitamos pasarle el nombre y los bytes
        file_obj = client.files.create(
            file=(uploaded_file.name, uploaded_file.getvalue()),
            purpose='assistants'
        )
        return file_obj.id
    except Exception as e:
        st.error(f"Error subiendo archivo: {e}")
        return None

def crear_asistente(file_id):
    """Crea el asistente configurado con Code Interpreter"""
    asistente_prompt = """
    Eres DataInsight, un asistente de IA analítico y colaborativo especializado en Análisis Exploratorio de Datos (EDA) interactivo.

    Tu rol principal es cargar, procesar y analizar archivos CSV proporcionados por el usuario.

    Tu público objetivo son científicos de datos, analistas de negocio y estudiantes que necesitan extraer rápidamente insights y visualizaciones de sus datos sin escribir código.

    Cuando el usuario pida un análisis, estás preparado para responder con las siguientes capacidades:

    Resumen General: Proporciona una visión estructural del dataset, incluyendo la lista de nombres de columnas, sus tipos de datos y el recuento de valores faltantes (nulos) para cada una.

    Resumen Estadístico: Genera estadísticas descriptivas para todas las columnas numéricas, incluyendo media, mediana, desviación estándar, mín, máx y cuartiles clave.

    Visualización de Datos (Gráficos): Genera visualizaciones claras y precisas bajo petición. Tus capacidades deben incluir:
    * **Histogramas** (para mostrar la distribución de datos)
    * **Gráficos de Barras** (para comparar categorías)
    * **Gráficos de Dispersión / Scatter Plots** (para mostrar relaciones entre dos variables)
    * **Gráficos de Caja / Box Plots** (para identificar rangos y valores atípicos)

    Análisis de Correlación: Calcula y presenta una matriz de correlación, idealmente visualizada como un mapa de calor (heatmap), para explicar las relaciones entre diferentes variables numéricas.

    Consultas Específicas: Responde preguntas directas consultando el dataset. (ej. "¿Cuál es el promedio de 'ColumnaA'?", "Muéstrame las filas donde 'ColumnaB' es 'ValorX'", "Cuenta los valores únicos en 'ColumnaC'").

    Identificación de Patrones (Conclusiones): Si el usuario pide "insights" o "conclusiones", puedes señalar patrones significativos, correlaciones fuertes o agrupaciones notables descubiertas durante el análisis.

    Disponibilidad para Q&A: Prepárate para responder cualquier pregunta de seguimiento que el usuario pueda tener sobre los datos, un gráfico generado o un análisis específico.

    Asegúrate de que tus explicaciones sean claras, concisas y directas, evitando jergas innecesarias. Cuando generes un gráfico, acompáñalo con una breve descripción de una frase sobre lo que muestra.

    Tu objetivo es hacer del análisis de datos un proceso accesible, interactivo y conversacional, permitiendo a los usuarios explorar su dataset de forma eficaz.
    
    ESTRUCTURA DE RESPUESTA OBLIGATORIA:
    1. Responde a la consulta del usuario con texto y/o gráficos normalmente.
    2. SIEMPRE al final de tu respuesta, añade un bloque de sugerencias oculto separado por "---SUGERENCIAS---".
    3. Genera exactamente 3 sugerencias breves (máximo 6 palabras) para análisis posteriores relacionados con los datos actuales.
    4. Separa cada sugerencia con una barra vertical "|".
    
    Ejemplo de formato final de tu respuesta:
    Aquí tienes el histograma de salarios que pediste. Se observa un sesgo a la derecha.
    ---SUGERENCIAS---
    Ver boxplot de salarios por rol | Analizar correlación experiencia-salario | Top 10 salarios más altos
    """
    
    assistant = client.beta.assistants.create(
        name="DataInsight Streamlit",
        instructions=asistente_prompt,
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}],
        tool_resources={
            "code_interpreter": {
                "file_ids": [file_id]
            }
        }
    )
    return assistant.id

def crear_hilo():
    """Crea un nuevo hilo de conversación"""
    thread = client.beta.threads.create()
    return thread.id

def procesar_mensaje(thread_id, assistant_id, user_message):
    """Envía mensaje, ejecuta el run y espera la respuesta"""
    
    # 1. Añadir mensaje
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    # 2. Ejecutar (Run)
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # 3. Polling (Esperar a que termine)
    with st.spinner('Analizando datos y generando gráficos...'):
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run.status == "failed":
                return {"text": "Error en la ejecución del asistente.", "images": []}
            time.sleep(2)
            
    # 4. Recuperar mensajes
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    last_msg = messages.data[0]

    # Inicializamos estructura de respuesta con lista de sugerencias vacía
    response_data = {"text": "", "images": [], "suggestions": []}

    if last_msg.role == "assistant":
        full_text = ""
        
        # Recopilar todo el texto primero
        for content in last_msg.content:
            if content.type == 'text':
                full_text += content.text.value
            elif content.type == 'image_file':
                file_id = content.image_file.file_id
                image_data = client.files.content(file_id).read()
                response_data["images"].append(image_data)

        # LÓGICA DE PARSEO DE SUGERENCIAS
        if "---SUGERENCIAS---" in full_text:
            parts = full_text.split("---SUGERENCIAS---")
            response_data["text"] = parts[0].strip() # Texto limpio para el usuario
            
            # Extraer las sugerencias separadas por "|"
            raw_suggestions = parts[1].strip().split("|")
            response_data["suggestions"] = [s.strip() for s in raw_suggestions if s.strip()]
        else:
            response_data["text"] = full_text
                
    return response_data