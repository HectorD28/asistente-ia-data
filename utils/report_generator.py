import tempfile
from fpdf import FPDF
import os
import re
import markdown

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Reporte de Análisis de Datos - DataInsight', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

# --- NUEVA FUNCIÓN DE AYUDA ---
def markdown_to_text(markdown_string):
    """Convierte una cadena de Markdown a texto plano."""
    # 1. Convertir Markdown a HTML
    html = markdown.markdown(markdown_string)
    # 2. Eliminar todas las etiquetas HTML
    text = re.sub(r'<[^>]+>', '', html)
    # 3. Limpiar espacios en blanco y saltos de línea extra
    text = re.sub(r'\n\s*\n', '\n\n', text).strip()
    return text

def generar_pdf_bytes(report_items):
    """
    Toma una lista de diccionarios con formato:
    {'text': str, 'images': [bytes]}
    Devuelve los bytes del PDF generado.
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, item in enumerate(report_items):
        # 1. Agregar el texto de la consulta/análisis
        # Usamos multi_cell para texto que puede ocupar varias líneas
        query_text = item.get('query', 'Análisis')
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Item #{i+1}: {query_text}", ln=True)
        
        pdf.set_font("Arial", size=11)
        # Limpiamos el texto de Markdown ANTES de pasarlo al PDF
        plain_text = markdown_to_text(item['text'])
        
        # Usamos el texto ya limpio y lo codificamos de forma segura
        clean_text = plain_text.encode('latin-1', 'replace').decode('latin-1')

        pdf.multi_cell(0, 10, clean_text)
        pdf.ln(5)

        # 2. Agregar imágenes
        if item.get('images'):
            for img_bytes in item['images']:
                # FPDF necesita un archivo físico o un stream muy específico.
                # Lo más robusto es crear un temporal.
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
                    temp_img.write(img_bytes)
                    temp_img_path = temp_img.name
                
                # Intentamos centrar la imagen
                try:
                    # Ajustar ancho a 150mm (A4 es 210mm)
                    pdf.image(temp_img_path, x=30, w=150) 
                    pdf.ln(10)
                except Exception as e:
                    pdf.cell(0, 10, f"[No se pudo renderizar la imagen: {e}]", ln=True)

        pdf.ln(10) # Espacio entre items del reporte
        # Línea separadora
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

    # Devolver bytes
    return bytes(pdf.output(dest='S'))