# 📊 Asistente de Datos IA con Streamlit y OpenAI

Este proyecto es una aplicación web construida con Streamlit que actúa como un asistente inteligente para el análisis de datos. Permite a los usuarios subir archivos de datos (como CSV o XLSX) y realizar preguntas en lenguaje natural para obtener análisis, resúmenes y visualizaciones generadas por la API de Asistentes de OpenAI.

## ✨ Características

-   **Carga de Archivos**: Soporte para subir archivos `.csv` y `.xlsx`.
-   **Procesamiento Inteligente**: Utiliza el `Code Interpreter` de la API de Asistentes de OpenAI para analizar los datos.
-   **Interfaz Interactiva**: Un área de chat para que los usuarios escriban sus consultas.
-   **Respuestas Multimodales**: El asistente puede generar tanto respuestas de texto como visualizaciones (gráficos, tablas).
-   **Diseño Modular**: La interfaz de usuario está dividida en componentes reutilizables para facilitar el mantenimiento.

## 🛠️ Tecnologías Utilizadas

-   **Frontend**: [Streamlit](https://streamlit.io/)
-   **Backend**: Python
-   **Inteligencia Artificial**: [OpenAI Assistants API (gpt-4o)](https://platform.openai.com/docs/assistants/overview)

## 🚀 Configuración y Ejecución Local

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

### 1. Prerrequisitos

-   Python 3.8 o superior.
-   Git.

### 2. Clonar el Repositorio

```bash
git clone https://github.com/HectorD28/asistente-ia-data.git
cd asistente-ia-data
```

### 3. Crear y Activar un Entorno Virtual

Es una buena práctica aislar las dependencias del proyecto.

```bash
# Crear el entorno
python -m venv .venv

# Activar en Windows (PowerShell/CMD)
.\.venv\Scripts\Activate

# Activar en macOS/Linux
source .venv/bin/activate
```

### 4. Instalar Dependencias

Instala todas las librerías necesarias desde el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5. Configurar la Clave de API

La aplicación necesita una clave de API de OpenAI para funcionar.

1.  Crea una carpeta llamada `.streamlit` en la raíz del proyecto si no existe.
2.  Dentro de `.streamlit`, crea un archivo llamado `secrets.toml`.
3.  Añade tu clave de API al archivo con el siguiente formato:

    ```toml
    # .streamlit/secrets.toml
    OPENAI_API_KEY = "sk-..." # ¡Pega aquí tu clave secreta de OpenAI!
    ```

    > **⚠️ ¡Importante!** El archivo `.gitignore` está configurado para ignorar `secrets.toml`, por lo que tu clave nunca se subirá a GitHub. **Nunca compartas tus claves de API públicamente.**

### 6. Ejecutar la Aplicación

Una vez completados los pasos anteriores, inicia la aplicación con Streamlit.

```bash
streamlit run main.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

## ☁️ Despliegue

Este proyecto está listo para ser desplegado en plataformas como **Streamlit Community Cloud** o **Render**.

-   **Dependencias**: El archivo `requirements.txt` le indica a la plataforma qué librerías instalar.
-   **Secretos**: En lugar de usar el archivo `secrets.toml` local, debes configurar tus secretos (como `OPENAI_API_KEY`) como **variables de entorno** o en la sección de "Secrets" del panel de control de la plataforma de despliegue. El código está preparado para leerlos de forma segura.