import streamlit as st
from styles import load_css
from components.header import render_header
from components.uploader import render_uploader
from components.input_area import render_input_area
from components.visualization import render_visualization
from backend import subir_archivo_openai, crear_asistente, crear_hilo, procesar_mensaje

# 1. Configuración (Debe ser siempre lo primero)
st.set_page_config(
    page_title="Asistente de Datos IA",
    page_icon="Pf",
    layout="centered"
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
    
    archivo = render_uploader()
    
    # Si se sube un nuevo archivo, crear asistente e hilo
    if archivo and not st.session_state.assistant_id:
        with st.spinner("Preparando asistente..."):
            file_id = subir_archivo_openai(archivo)
            if file_id:
                st.session_state.assistant_id = crear_asistente(file_id)
                st.session_state.thread_id = crear_hilo()
                st.success("Asistente listo. ¡Ya puedes hacer preguntas!")

    prompt_text, generar_btn = render_input_area()
    
    if generar_btn and prompt_text and st.session_state.assistant_id:
        st.session_state.response = procesar_mensaje(
            st.session_state.thread_id,
            st.session_state.assistant_id,
            prompt_text
        )
    
    # Mostrar la respuesta del asistente o la visualización por defecto
    if st.session_state.response:
        st.subheader("Respuesta del Asistente")
        response_data = st.session_state.response
        st.write(response_data["text"])
        if response_data["images"]:
            for img in response_data["images"]:
                st.image(img)
    else:
        render_visualization()

if __name__ == "__main__":
    main()