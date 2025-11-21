import streamlit as st
from styles import load_css
from components.header import render_header
from components.sidebar import render_sidebar
from components.uploader import render_uploader
from backend import cargar_dataset_local, inicializar_chat, procesar_mensaje, generar_prompt_inicial_automatico, run_python_tool
import pandas as pd

# Configuración
st.set_page_config(page_title="Data Assistant Colab-Style", page_icon="🤖", layout="wide")
load_css("assets/style.css")

# Estado
if "dataframes" not in st.session_state: st.session_state.dataframes = {}
if "analisis_realizado" not in st.session_state: st.session_state.analisis_realizado = False
if "history_images" not in st.session_state: st.session_state.history_images = []

def main():
    render_header()
    render_sidebar() # Mantiene las instrucciones originales del repo
    
    # 1. Zona de Carga
    uploaded_file = render_uploader()
    if uploaded_file:
        # Usamos la función del backend para procesar el archivo
        name, df, error = cargar_dataset_local(uploaded_file)
        
        if error:
            st.error(error)
        elif name and name not in st.session_state.dataframes:
            # Guardar en memoria
            st.session_state.dataframes[name] = df
            st.toast(f"✅ Dataset '{name}' cargado exitosamente")
            
            # Reiniciar el flujo para simular el inicio del Colab
            st.session_state.messages = []
            st.session_state.analisis_realizado = False
            inicializar_chat()
            st.rerun() # Recargar para detectar el cambio de estado

    # 2. Lógica de Análisis Automático (Simulación del bloque inicial del Colab)
    if st.session_state.dataframes and not st.session_state.analisis_realizado:
        with st.spinner("🤖 Realizando análisis exploratorio y generando sugerencias..."):
            prompt_inicial = generar_prompt_inicial_automatico()
            # Procesamos este mensaje internamente sin que el usuario lo escriba
            procesar_mensaje(prompt_inicial) 
            st.session_state.analisis_realizado = True
            st.rerun()

    # 3. Interfaz de Chat (Estilo Colab)
    st.divider()
    
    # Mostrar historial
    if "messages" in st.session_state:
        for msg in st.session_state.messages:
            # Ignorar mensajes del sistema y prompts automáticos
            if msg["role"] == "system" or (msg["role"] == "user" and "He cargado los siguientes datasets" in msg["content"]):
                continue

            # Ignorar los mensajes de resultado de la herramienta (el "T") y de intención (el "None")
            if msg.get("role") == "tool":
                continue
            if msg.get("role") == "assistant" and not msg.get("content"):
                continue
            
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                # Si el mensaje del asistente tiene imágenes, muéstralas aquí
                if msg["role"] == "assistant" and "images" in msg and msg["images"]:
                    for img in msg["images"]:
                        st.image(img)
    
    # 4. Input del Usuario
    if prompt := st.chat_input("Haz una pregunta o pide una visualización sugerida..."):
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.spinner("Analizando..."):
            response = procesar_mensaje(prompt)
        
        st.rerun()

if __name__ == "__main__":
    main()