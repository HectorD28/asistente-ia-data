import streamlit as st

def render_input_area():
    prompt = st.text_area(
        "Input", 
        placeholder="¿Qué te gustaría visualizar? Ej: Muéstrame las ventas por mes", 
        label_visibility="collapsed",
        height=100
    )

    col_spacer, col_btn = st.columns([0.75, 0.25])
    with col_btn:
        clicked = st.button("Generar ➤", type="primary", use_container_width=True)
    
    st.write("") # Espaciador
    
    return prompt, clicked