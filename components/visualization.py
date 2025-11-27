import streamlit as st

def render_visualization():
    col_title, col_btn1, col_btn2 = st.columns([0.5, 0.25, 0.25])

    with col_title:
        st.subheader("Visualización")

    # Renderizar el placeholder HTML
    st.markdown("""
        <div class="visualization-box">
            <h3>Tu visualización aparecerá aquí</h3>
            <p style="font-size: 14px;">Sube un archivo CSV y haz una pregunta para comenzar.</p>
        </div>
    """, unsafe_allow_html=True)