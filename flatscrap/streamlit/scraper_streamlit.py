import streamlit as st
import subprocess
import re
import requests
import os
import sys
import django

# Configuración de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flatscrap.settings')
django.setup()

# Inicializar session state
if "new_properties" not in st.session_state:
    st.session_state["new_properties"] = []
if "scraper_running" not in st.session_state:
    st.session_state["scraper_running"] = False

def parse_new_properties_from_log(log_line):
    pattern = r'New property added: (.+)'
    match = re.search(pattern, log_line)
    
    if match:
        return match.group(1).strip()
    return None

def run_scraper():
    # Reiniciar lista de propiedades nuevas
    st.session_state["new_properties"] = []
    st.session_state["scraper_running"] = True

    try:
        # Ejecutar el comando de scraping y capturar la salida
        result = subprocess.run(
            ["python", "manage.py", "tecnopiso"], 
            capture_output=True, 
            text=True,
            check=True
        )

        # Procesar cada línea de log
        for line in result.stdout.split('\n'):
            new_prop = parse_new_properties_from_log(line)
            if new_prop:
                st.session_state["new_properties"].append(new_prop)

    except subprocess.CalledProcessError as e:
        st.error(f"Error durante el scraping: {e}")
        st.error(f"Salida de error: {e.stderr}")
    finally:
        st.session_state["scraper_running"] = False

# Título de la aplicación
st.title("Tecnocasa Property Scraper")

# Botón para iniciar scraping
if st.button("Iniciar scraping"):
    with st.spinner("Ejecutando scraping..."):
        run_scraper()

# Mostrar propiedades nuevas
if st.session_state.get("new_properties"):
    st.write("### Nuevas Propiedades:")
    for prop in st.session_state["new_properties"]:
        st.write(f"- {prop}")

# Botón para mostrar base de datos completa
if st.button("Mostrar Todos los Pisos"):
    try:
        response = requests.get('http://localhost:8000/tecnocasa/')
        
        if response.status_code == 200:
            properties = response.json()
            st.write(f"Total de propiedades: {len(properties)}")
            
            for prop in properties:
                with st.expander(f"Piso en {prop.get('location', 'Sin ubicación')}"):
                    st.write(f"**Precio**: {prop.get('price', 'No disponible')}") 
                    st.write(f"**Ubicación**: {prop.get('location', 'No disponible')}")
                    st.write(f"**Superficie**: {prop.get('surface', 'No disponible')}")
                    st.write(f"**Tipo**: {prop.get('type', 'No disponible')}")
        else:
            st.error(f'Error al recuperar propiedades: {response.status_code}')
    except Exception as e:
        st.error(f'Error de conexión: {e}')







