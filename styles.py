import streamlit as st

def load_css(file_path):
    """
    Carga un archivo CSS externo y lo inyecta en la app de Streamlit.
    """
    try:
        with open(file_path) as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Archivo CSS no encontrado en la ruta: {file_path}")
