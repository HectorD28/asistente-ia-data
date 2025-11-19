import streamlit as st

def render_uploader():
    # Inicializar estado de sesión si no existe
    if 'archivo_cargado' not in st.session_state:
        st.session_state.archivo_cargado = True  # Simulación inicial

    uploaded_file = st.file_uploader(
        "Sube tu archivo", 
        type=['csv', 'xlsx'], 
        label_visibility="collapsed"
    )

    # Lógica visual: Mostrar tarjeta si hay archivo (real o simulado)
    if st.session_state.archivo_cargado or uploaded_file:
        st.info("📄 ventas_2023.csv", icon="✅")
    
    return uploaded_file