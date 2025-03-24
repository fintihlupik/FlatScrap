# import streamlit as st
# import time
# import django
# import os
# import sys
# import requests
# import subprocess


# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flatscrap.settings')
# django.setup()
# from tecnocasa.services.pisoscrape import TecnocasaScraper 


# if "changes" not in st.session_state:
#     st.session_state["changes"] = []  # Inicializar!
# if "scraper_running" not in st.session_state:
#     st.session_state["scraper_running"] = False  
# if "scraper_initiated" not in st.session_state:
#     st.session_state["scraper_initiated"] = False

# # Función personalizada para manejar los logs de cambios en la base de datos
# def custom_log_handler(message):
#     if "New property added" in message or "Property updated" in message:
#         # Añadir el mensaje al session_state para poder visualizarlo en Streamlit
#         st.session_state["changes"].append(message)

# # Función para ejecutar el scraper
# def run_scraper():
#     st.session_state["scraper_running"] = True 
#     st.session_state["scraper_initiated"] = True
#     scraper = TecnocasaScraper()
    
#     # Sobrescribir el logger del scraper para almacenar cambios en session_state
#     scraper.logger.info = custom_log_handler  # Aquí sustituyo info por mi función custom_log_handler
#     scraper.scrape()
#     st.session_state["scraper_running"] = False 

# st.title("Tecnocasa Property Scraper")

# # Botón para iniciar el scraping
# if st.button("Iniciar scraping"):
#     with st.spinner("Ejecutando scraping..."):
#         run_scraper()

# def display_changes():
#     if st.session_state["changes"]:
#         st.write("### Cambios en la base de datos:")
#         for change in st.session_state["changes"]:
#             st.write(f"- {change}")

# # Ciclo para actualizar la vista de los cambios solo si el scraper está corriendo
# while st.session_state["scraper_running"]:
#     display_changes()  # Mostrar los cambios en la interfaz
#     time.sleep(1)  # Esperar 1 segundo para volver a comprobar cambios

# # Una vez que el scraper ha terminado, mostramos los cambios finales
# if st.session_state["scraper_initiated"] and not st.session_state["scraper_running"]:
#     display_changes()
#     st.write("### Scraping completado")


# if st.button("Mostrar Database"):
#     st.write('Estos son mis pisos desde mi API:')
#     response = requests.get('http://localhost:8000/tecnocasa/')
    
#     if response.status_code == 200:
#         properties = response.json()
#         for prop in properties:
#             st.write(f"**Precio**: {prop['price']}") 
#             st.write(f"**Ubicación**: {prop['location']}")
#             st.write(f"**Superficie**: {prop['surface']}")
#             st.write(f"**Tipo**: {prop['type']}")
#             st.write(f"**Agencia**: {prop['agency']}")
#             st.write(f"**URL**: {prop['url']}")
#             st.write(f"**Fecha de primera publicación**: {prop['first_seen']}")
#             st.write(f"**Última actualización**: {prop['last_updated']}")
#             st.write("---")  # Separador entre propiedades
#     else:
#         st.write('No se encontraron pisos') 



#  NO MUESTRA EN LA WEVWEB
import streamlit as st
import time
import django
import os
import sys
import requests
import subprocess
import time


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flatscrap.settings')
django.setup()
from tecnocasa.services.pisoscrape import TecnocasaScraper 


if "changes" not in st.session_state:
    st.session_state["changes"] = []  # Inicializar!
if "scraper_running" not in st.session_state:
    st.session_state["scraper_running"] = False  
if "scraper_initiated" not in st.session_state:
    st.session_state["scraper_initiated"] = False

# Función personalizada para manejar los logs de cambios en la base de datos
def custom_log_handler(message):
    if "New property added" in message or "Property updated" in message:
        # Añadir el mensaje al session_state para poder visualizarlo en Streamlit
        st.session_state["changes"].append(message)

def display_changes():
    if st.session_state["changes"]:
        st.write("### Cambios en la base de datos:")
        for change in st.session_state["changes"]:
            st.write(f"- {change}")

# Función para ejecutar el scraper
def run_scraper():
    st.session_state["scraper_running"] = True 
    st.session_state["scraper_initiated"] = True

    # Ejecutar el scraper como un proceso en segundo plano
    scraper_process = subprocess.Popen(["python", "manage.py", "tecnopiso"])  # Esto ejecuta el comando en un proceso separado

    # Mientras el scraper esté corriendo, puedes seguir mostrando los cambios
    while scraper_process.poll() is None:  # Mientras el proceso del scraper esté activo
        time.sleep(1)  # Espera 1 segundo
        display_changes()  # Mostrar los cambios en la interfaz

    st.session_state["scraper_running"] = False
    display_changes()

st.title("Tecnocasa Property Scraper")

# Botón para iniciar el scraping
if st.button("Iniciar scraping"):
    with st.spinner("Ejecutando scraping..."):
        run_scraper()

# Ciclo para actualizar la vista de los cambios solo si el scraper está corriendo
while st.session_state["scraper_running"]:
    display_changes()  # Mostrar los cambios en la interfaz
    time.sleep(1)  # Esperar 1 segundo para volver a comprobar cambios

# Una vez que el scraper ha terminado, mostramos los cambios finales
if st.session_state["scraper_initiated"] and not st.session_state["scraper_running"]:
    display_changes()
    st.write("### Scraping completado")


if st.button("Mostrar Database"):
    st.write('Estos son mis pisos desde mi API:')
    response = requests.get('http://localhost:8000/tecnocasa/')
    
    if response.status_code == 200:
        properties = response.json()
        for prop in properties:
            st.write(f"**Precio**: {prop['price']}") 
            st.write(f"**Ubicación**: {prop['location']}")
            st.write(f"**Superficie**: {prop['surface']}")
            st.write(f"**Tipo**: {prop['type']}")
            st.write(f"**Agencia**: {prop['agency']}")
            st.write(f"**URL**: {prop['url']}")
            st.write(f"**Fecha de primera publicación**: {prop['first_seen']}")
            st.write(f"**Última actualización**: {prop['last_updated']}")
            st.write("---")  # Separador entre propiedades
    else:
        st.write('No se encontraron pisos') 

# GEMINI NO VA
# import streamlit as st
# import time
# import django
# import os
# import sys
# import requests

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flatscrap.settings')
# django.setup()
# from tecnocasa.services.pisoscrape import TecnocasaScraper

# if "changes" not in st.session_state:
#     st.session_state["changes"] = []
# if "scraper_running" not in st.session_state:
#     st.session_state["scraper_running"] = False
# if "scraper_initiated" not in st.session_state:
#     st.session_state["scraper_initiated"] = False

# # Función personalizada para manejar los logs de cambios en la base de datos
# def custom_log_handler(message):
#     if "New property added" in message or "Property updated" in message:
#         st.session_state["changes"].append(message)

# @st.cache_resource
# def get_scraper():
#     return TecnocasaScraper()

# # Función para ejecutar el scraper
# def run_scraper():
#     st.session_state["scraper_running"] = True
#     st.session_state["scraper_initiated"] = True
#     scraper = get_scraper()

#     # Sobrescribir el logger del scraper para almacenar cambios en session_state
#     scraper.logger.info = custom_log_handler
#     try:
#         scraper.scrape()
#     finally:
#         scraper.close()  # Asegurar el cierre del navegador
#     st.session_state["scraper_running"] = False

# st.title("Tecnocasa Property Scraper")

# # Botón para iniciar el scraping
# if st.button("Iniciar scraping"):
#     with st.spinner("Ejecutando scraping..."):
#         run_scraper()

# def display_changes():
#     if st.session_state["changes"]:
#         st.write("### Cambios en la base de datos:")
#         for change in st.session_state["changes"]:
#             st.write(f"- {change}")

# # Ciclo para actualizar la vista de los cambios solo si el scraper está corriendo
# while st.session_state["scraper_running"]:
#     display_changes()
#     time.sleep(1)

# # Una vez que el scraper ha terminado, mostramos los cambios finales
# if st.session_state["scraper_initiated"] and not st.session_state["scraper_running"]:
#     display_changes()
#     st.write("### Scraping completado")

# if st.button("Mostrar Database"):
#     st.write('Estos son mis pisos desde mi API:')
#     response = requests.get('http://localhost:8000/tecnocasa/')

#     if response.status_code == 200:
#         properties = response.json()
#         for prop in properties:
#             st.write(f"**Precio**: {prop['price']}")
#             st.write(f"**Ubicación**: {prop['location']}")
#             st.write(f"**Superficie**: {prop['surface']}")
#             st.write(f"**Tipo**: {prop['type']}")
#             st.write(f"**Agencia**: {prop['agency']}")
#             st.write(f"**URL**: {prop['url']}")
#             st.write(f"**Fecha de primera publicación**: {prop['first_seen']}")
#             st.write(f"**Última actualización**: {prop['last_updated']}")
#             st.write("---")
#     else:
#         st.write('No se encontraron pisos')











