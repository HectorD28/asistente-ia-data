import streamlit as st

def render_sidebar():
    """
    Renderiza la barra lateral con el flujo de ejecución para el usuario.
    """
    with st.sidebar:
        st.markdown("## 🚀 Cómo Empezar")
        st.markdown(
            """
            Sigue estos pasos para generar visualizaciones a partir de tus datos:

            **1. Carga tu archivo:**
            Utiliza el cargador de archivos para subir un documento `.csv` o `.xlsx`.

            **2. Espera al asistente:**
            El sistema preparará un asistente de IA para analizar tus datos. Verás un mensaje cuando esté listo.

            **3. Realiza tu consulta:**
            Escribe en el área de texto qué información o gráfico deseas obtener.

            **4. Genera la visualización:**
            Haz clic en el botón "Generar" y espera la respuesta del asistente.
            """
        )
        
        st.markdown("---")
        st.success(
            "**¡Listo!** El asistente mostrará la visualización o la información solicitada."
        )