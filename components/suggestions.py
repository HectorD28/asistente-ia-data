import streamlit as st

def render_suggestions(suggestions):
    """
    Renderiza tarjetas de sugerencia y devuelve el texto de la seleccionada.
    """
    if not suggestions:
        return None

    st.markdown("### 💡 Quizás te interese visualizar...")
    
    # Usamos columnas para poner las tarjetas una al lado de la otra
    cols = st.columns(len(suggestions))
    selected_suggestion = None

    for i, suggestion in enumerate(suggestions):
        # Si el usuario hace click, capturamos ese texto
        if cols[i].button(suggestion, use_container_width=True):
            selected_suggestion = suggestion

    # Mensaje adicional solicitado
    st.caption("O continúa escribiendo una nueva consulta en el chat de abajo 👇")
    st.divider()
    
    return selected_suggestion