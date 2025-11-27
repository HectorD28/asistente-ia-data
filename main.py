import streamlit as st
from styles import load_css
from components.header import render_header
from components.uploader import render_uploader
from components.input_area import render_input_area
from components.visualization import render_visualization
from components.sidebar import render_sidebar  
from components.suggestions import render_suggestions
from utils.report_generator import generar_pdf_bytes
from backend import subir_archivo_openai, crear_asistente, crear_hilo, procesar_mensaje

# 1. Configuración (Debe ser siempre lo primero)
st.set_page_config(
    page_title="Asistente de Datos IA",
    page_icon="📊",
    layout="wide"
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
if "report_queue" not in st.session_state: 
    st.session_state.report_queue = []

# 4. Renderizar componentes en orden
def main():
    render_header()
    with st.sidebar:
        render_sidebar() # Tu sidebar original
        
        st.divider()
        st.subheader(f"📄 Reporte ({len(st.session_state.report_queue)} items)")
        
        if st.session_state.report_queue:
            if st.button("🗑️ Limpiar reporte", use_container_width=True):
                st.session_state.report_queue = []
                st.rerun()
            
            # Botón de Descarga
            # Generamos el PDF al vuelo
            pdf_data = generar_pdf_bytes(st.session_state.report_queue)
            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_data,
                file_name="reporte_data_insight.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            st.info("Agrega análisis para exportar.")

    archivo = render_uploader()
    
    # Si se sube un nuevo archivo, crear asistente e hilo
    if archivo and not st.session_state.assistant_id:
        with st.spinner("Preparando asistente..."):
            file_id = subir_archivo_openai(archivo)
            if file_id:
                st.session_state.assistant_id = crear_asistente(file_id)
                st.session_state.thread_id = crear_hilo()
                st.success("Asistente listo. ¡Ya puedes hacer preguntas!")

    # Inicializar historial de sugerencias en session_state si no existe
    if "current_suggestions" not in st.session_state:
        st.session_state.current_suggestions = []

    # --- LÓGICA DE VISUALIZACIÓN Y "AGREGAR AL REPORTE" ---
    if st.session_state.response:
        st.subheader("Respuesta del Asistente")
        
        # Creamos columnas: Contenido (80%) | Acciones (20%)
        col_content, col_actions = st.columns([0.85, 0.15])
        
        with col_content:
            st.write(st.session_state.response["text"])
            if st.session_state.response["images"]:
                for img in st.session_state.response["images"]:
                    st.image(img)
        
        with col_actions:
            # Botón para añadir este análisis específico al reporte
            # Usamos un key único basado en la longitud del historial para evitar duplicados
            btn_key = f"add_btn_{len(st.session_state.report_queue)}"
            
            if st.button("➕ Incluir en Reporte", key="add_to_report", help="Guardar este análisis para el PDF final"):
                # Guardamos el estado actual en la cola
                item = {
                    "text": st.session_state.response["text"],
                    "images": st.session_state.response["images"],
                    # Podrías guardar también el prompt si lo tienes disponible en el estado
                    "query": "Análisis Generado" 
                }
                st.session_state.report_queue.append(item)
                st.toast("✅ Agregado al reporte", icon="📄")
                st.rerun()

        st.session_state.current_suggestions = st.session_state.response.get("suggestions", [])

    else:
        render_visualization()

    # Renderizar Tarjetas de Sugerencias (SIEMPRE DEBAJO DEL GRÁFICO/RESPUESTA)
    suggestion_clicked = render_suggestions(st.session_state.current_suggestions)

    # Renderizar Input de Texto
    prompt_text, generar_btn = render_input_area()
    
    # --- LOGICA UNIFICADA DE EJECUCIÓN ---
    # Determinamos qué input usar: ¿Clic en sugerencia o Botón generar?
    final_prompt = None
    
    if suggestion_clicked:
        final_prompt = suggestion_clicked
    elif generar_btn and prompt_text:
        final_prompt = prompt_text
    
    # Ejecutar procesamiento si hay un prompt definido
    if final_prompt:
        if not st.session_state.assistant_id:
             st.warning("Por favor, sube un archivo antes.", icon="⚠️")
        else:
            # Procesamos el mensaje
            st.session_state.response = procesar_mensaje(
                st.session_state.thread_id,
                st.session_state.assistant_id,
                final_prompt
            )
            # Forzamos la recarga para mostrar los resultados inmediatamente
            st.rerun()

if __name__ == "__main__":
    main()