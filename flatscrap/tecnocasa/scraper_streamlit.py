
# import streamlit as st
# import time
# import threading
# import logging
# import django
# import os
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flatscrap.settings')
# django.setup()
# from tecnocasa.services.pisoscrape import TecnocasaScraper  # Asegúrate de importar tu scraper


# if "changes" not in st.session_state:
#     st.session_state["changes"] = []  # Inicializamos correctamente "changes"
# if "scraper_running" not in st.session_state:
#     st.session_state["scraper_running"] = False  # Estado de si el scraper está corriendo

# # Función personalizada para manejar los logs de cambios en la base de datos
# def custom_log_handler(message):
#     if "New property added" in message or "Property updated" in message:
#         # Añadir el mensaje al session_state para que lo podamos visualizar en Streamlit
#         st.session_state["changes"].append(message)

# # Función para ejecutar el scraper
# def run_scraper():
#     st.session_state["scraper_running"] = True  # Indicamos que el scraper está corriendo
#     scraper = TecnocasaScraper()
    
#     # Sobrescribir el logger del scraper para almacenar cambios en session_state
#     scraper.logger.info = custom_log_handler  # Aquí sustituimos info por nuestro manejador

#     # Ejecutar el scraper (el scraping en sí)
#     scraper.scrape()
    
#     st.session_state["scraper_running"] = False  # Indicamos que el scraper ha terminado


# # Botón para iniciar el scraping
# if st.button("Iniciar scraping"):
#     with st.spinner("Ejecutando scraping..."):
#         run_scraper()

# # Mostrar los cambios de la base de datos
# def display_changes():
#     if st.session_state["changes"]:
#         st.write("### Cambios en la base de datos:")
#         for change in st.session_state["changes"]:
#             st.write(f"- {change}")
#     else:
#         st.write("### Esperando cambios en la base de datos...")

# # Ciclo para actualizar la vista de los cambios solo si el scraper está corriendo
# while st.session_state["scraper_running"]:
#     display_changes()  # Mostrar los cambios en la interfaz
#     time.sleep(1)  # Esperar 1 segundo para volver a comprobar cambios

# # Una vez que el scraper ha terminado, mostramos los cambios finales
# if not st.session_state["scraper_running"]:
#     display_changes()
#     st.write("### Scraping completado")


import streamlit as st
import time
import threading
import logging
import django
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flatscrap.settings')
django.setup()
from tecnocasa.services.pisoscrape import TecnocasaScraper  # Asegúrate de importar tu scraper


if "changes" not in st.session_state:
    st.session_state["changes"] = []  # Inicializamos correctamente "changes"
if "scraper_running" not in st.session_state:
    st.session_state["scraper_running"] = False  # Estado de si el scraper está corriendo
if "scraper_initiated" not in st.session_state:
    st.session_state["scraper_initiated"] = False

# Función personalizada para manejar los logs de cambios en la base de datos
def custom_log_handler(message):
    if "New property added" in message or "Property updated" in message:
        # Añadir el mensaje al session_state para que lo podamos visualizar en Streamlit
        st.session_state["changes"].append(message)

# Función para ejecutar el scraper
def run_scraper():
    st.session_state["scraper_running"] = True  # Indicamos que el scraper está corriendo
    st.session_state["scraper_initiated"] = True
    scraper = TecnocasaScraper()
    
    # Sobrescribir el logger del scraper para almacenar cambios en session_state
    scraper.logger.info = custom_log_handler  # Aquí sustituimos info por nuestro manejador

    # Ejecutar el scraper (el scraping en sí)
    scraper.scrape()
    
    st.session_state["scraper_running"] = False  # Indicamos que el scraper ha terminado

st.title("Tecnocasa Property Scraper")

# Botón para iniciar el scraping
if st.button("Iniciar scraping"):
    with st.spinner("Ejecutando scraping..."):
        run_scraper()

def display_changes():
    if st.session_state["changes"]:
        st.write("### Cambios en la base de datos:")
        for change in st.session_state["changes"]:
            st.write(f"- {change}")
    elif st.session_state["scraper_initiated"]:  # Solo mostrar este mensaje si se inició el scraper
        st.write("### Esperando cambios en la base de datos...")

# Ciclo para actualizar la vista de los cambios solo si el scraper está corriendo
while st.session_state["scraper_running"]:
    display_changes()  # Mostrar los cambios en la interfaz
    time.sleep(1)  # Esperar 1 segundo para volver a comprobar cambios

# Una vez que el scraper ha terminado, mostramos los cambios finales
if st.session_state["scraper_initiated"] and not st.session_state["scraper_running"]:
    display_changes()
    st.write("### Scraping completado")



