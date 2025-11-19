import streamlit as st

def render_header():
    col1, col2 = st.columns([0.9, 0.1])
    
    with col1:
        st.markdown("### 📊 **Asistente de Datos IA**")
    
    with col2:
        st.button("⚙️", key="settings_btn", help="Configuración")
    
    st.divider()