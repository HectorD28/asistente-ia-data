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
    assistant = client.beta.assistants.create(
        name="DataInsight Streamlit",
        instructions="Eres DataInsight, un experto en ciencia de datos... (TU PROMPT COMPLETO AQUÍ)...",
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
    
    # Procesar la última respuesta del asistente
    last_msg = messages.data[0]
    response_data = {"text": "", "images": []}

    if last_msg.role == "assistant":
        for content in last_msg.content:
            if content.type == 'text':
                response_data["text"] += content.text.value
            elif content.type == 'image_file':
                # Descargar la imagen de la memoria de OpenAI
                file_id = content.image_file.file_id
                image_data = client.files.content(file_id).read()
                response_data["images"].append(image_data)
                
    return response_data