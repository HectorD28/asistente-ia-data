import streamlit as st

def render_header():
    """
    Renderiza una barra de navegación superior personalizada con sintaxis de Streamlit.
    """
    # Usar columnas para alinear el título a la izquierda y el enlace a la derecha
    col1, col2 = st.columns([3, 1])

    with col1:
        # Usamos markdown para poder incluir el emoji y controlar el nivel del título
        st.markdown("### 📊 Asistente de datos IA", unsafe_allow_html=False)

    with col2:
        # Para alinear el enlace a la derecha, lo envolvemos en un div con estilo.
        # El markdown es necesario para crear el hipervínculo.
        st.markdown(
            '<p style="text-align: right;"><a href="https://github.com/HectorD28/asistente-ia-data" style="color: white;"target="_blank">Docs</a></p>',
            unsafe_allow_html=True
        )
    
    # Añadir un divisor visual
    st.divider()