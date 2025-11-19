import streamlit as st

def render_uploader():
   
    st.subheader("Subir dataset")

    uploaded_file = st.file_uploader(
        "Sube tu archivo", 
        type=['csv', 'xlsx'], 
        label_visibility="collapsed"
    )

    # Lógica visual: Mostrar tarjeta si hay archivo (real o simulado)
    if uploaded_file is not None:
        st.subheader("Archivo subido")
        st.info(f"📄 {uploaded_file.name}", icon="✅")
    
    return uploaded_file