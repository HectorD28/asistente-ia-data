import streamlit as st
from styles import load_css
from components.header import render_header
from components.uploader import render_uploader
from components.input_area import render_input_area
from components.visualization import render_visualization
from components.sidebar import render_sidebar  
from components.suggestions import render_suggestions
from backend import subir_archivo_openai, crear_asistente, crear_hilo, procesar_mensaje

# 1. Configuración (Debe ser siempre lo primero)
st.set_page_config(
    page_title="Asistente de Datos IA",
    page_icon="📊",
    layout="wide"
)

# 2. Cargar Estilos
load_css("assets/style.css")

# 3. Inicializar estado de sesión
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "response" not in st.session_state:
    st.session_state.response = None

# 4. Renderizar componentes en orden
def main():
    render_header()
    render_sidebar()

    archivo = render_uploader()
    
    # Si se sube un nuevo archivo, crear asistente e hilo
    if archivo and not st.session_state.assistant_id:
        with st.spinner("Preparando asistente..."):
            file_id = subir_archivo_openai(archivo)
            if file_id:
                st.session_state.assistant_id = crear_asistente(file_id)
                st.session_state.thread_id = crear_hilo()
                st.success("Asistente listo. ¡Ya puedes hacer preguntas!")

    # Inicializar historial de sugerencias en session_state si no existe
    if "current_suggestions" not in st.session_state:
        st.session_state.current_suggestions = []

    # Mostrar respuesta anterior si existe
    if st.session_state.response:
        st.subheader("Respuesta del Asistente")
        
        # Mostrar texto
        st.write(st.session_state.response["text"])
        
        # Mostrar imágenes
        if st.session_state.response["images"]:
            for img in st.session_state.response["images"]:
                st.image(img)
        
        # Guardar las sugerencias recibidas en el estado
        st.session_state.current_suggestions = st.session_state.response.get("suggestions", [])

    else:
        render_visualization()

    # Renderizar Tarjetas de Sugerencias (SIEMPRE DEBAJO DEL GRÁFICO/RESPUESTA)
    suggestion_clicked = render_suggestions(st.session_state.current_suggestions)

    # Renderizar Input de Texto
    prompt_text, generar_btn = render_input_area()
    
    # --- LOGICA UNIFICADA DE EJECUCIÓN ---
    # Determinamos qué input usar: ¿Clic en sugerencia o Botón generar?
    final_prompt = None
    
    if suggestion_clicked:
        final_prompt = suggestion_clicked
    elif generar_btn and prompt_text:
        final_prompt = prompt_text
    
    # Ejecutar procesamiento si hay un prompt definido
    if final_prompt:
        if not st.session_state.assistant_id:
             st.warning("Por favor, sube un archivo antes.", icon="⚠️")
        else:
            # Procesamos el mensaje
            st.session_state.response = procesar_mensaje(
                st.session_state.thread_id,
                st.session_state.assistant_id,
                final_prompt
            )
            # Forzamos la recarga para mostrar los resultados inmediatamente
            st.rerun()

if __name__ == "__main__":
    main()