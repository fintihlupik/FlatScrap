import random
from selenium import webdriver      # Módulo principal de Selenium para controlar navegadores
from selenium.webdriver.common.by import By     # Define métodos para localizar elementos (ID, CLASS_NAME, XPATH, etc.)
from webdriver_manager.chrome import ChromeDriverManager    # Gestiona la descarga automática del ChromeDriver compatible
from selenium.webdriver.chrome.service import Service       # Configura el servicio que maneja el ChromeDriver
from selenium.webdriver.support.ui import WebDriverWait     # Permite la espera de elementos en la página
from selenium.webdriver.support import expected_conditions as EC   # Condiciones predefinidas para usar con WebDriverWait
import time
import logging
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from django.utils import timezone
from tecnocasa.models import Property
from logging.handlers import RotatingFileHandler
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options



class TecnocasaScraper:
    def __init__(self):
        self.driver = self.configure_driver()
        self._setup_logger()
    

    def _setup_logger(self):
        self.logger = logging.getLogger("TecnocasaScraper")
        self.logger.setLevel(logging.DEBUG)
        
        # Formato del logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para archivo (rotativo)
        file_handler = RotatingFileHandler(
            'tecnopiso.log',
            maxBytes=1024*1024*5,  # 5 MB
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info("Logger configurado correctamente")
        self.logger.debug("Nivel de logging establecido en DEBUG")

    def configure_driver(self):
        # options = uc.ChromeOptions()
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # return uc.Chrome(options=options)
    
        options = Options()
        options.add_argument('--headless')  # Ejecutar en modo headless
        options.add_argument('--no-sandbox')  # Requerido para algunos servidores
        options.add_argument('--disable-dev-shm-usage')  # Para evitar errores de memoria

        # Proporcionar la ruta del binario de Firefox
        #options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe" ######################## Ruta de Windows quitar
        # Configurar el servicio de GeckoDriver
        service = Service("/usr/local/bin/geckodriver")
        #service = Service("C:\\Program Files\\geckodriver\\geckodriver.exe") ######################## Ruta de Windows quitar
        # Crear el WebDriver de Firefox
        return webdriver.Firefox(service=service, options=options)
    
    def handle_cookies(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-default.deny-all-btn"))
            ).click()
        except:
            pass  # No siempre aparece el banner de cookies

    def order_by_newest(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ordina"))
        ).click() 
        self.driver.find_element(By.XPATH, "//span[text()='Más recientes']").click() 
        self.logger.debug("Ordenado por más recientes")

    def process_page(self):
        try:
            self.logger.debug("Iniciando procesamiento de página")
            # if self.driver.current_url.endswith("150000"):
            #     self.logger.debug("Ordenando por más recientes")
            #     self.order_by_newest()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".estates-list")))
            self.logger.debug("Lista de pisos encontrada")

            estate_cards = self.driver.find_elements(By.CSS_SELECTOR, ".estate-card")
            self.logger.debug(f"Se encontraron {len(estate_cards)} tarjetas de propiedades.")
        
            if not estate_cards:  # que no sea una lista vacía
                self.logger.warning("No se encontraron tarjetas de propiedades en esta página.")
                return
            
            for card in self.driver.find_elements(By.CSS_SELECTOR, ".estate-card"):
                if card:
                    try:
                        location = card.find_element(By.CSS_SELECTOR, "h4.estate-card-subtitle").text
                        price = card.find_element(By.CSS_SELECTOR, ".estate-card-current-price").text
                        surface = card.find_element(By.CSS_SELECTOR, ".estate-card-surface span").text 
                        url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                        type = "Apartment"
                        agency = "Tecnocasa"

                        self.logger.info(f"Datos extraídos - Ubicación: {location}, Precio: {price}, Superficie: {surface}, URL: {url}")
                        self.update_or_create_property(price, location, surface, type, agency, url)
                    except Exception as e:
                        self.logger.error(f"Error en tarjeta: {str(e)}", exc_info=True)
                        continue
        except Exception as e:
            self.logger.critical(f"Error crítico en process_page: {str(e)}", exc_info=True)
            #self.driver.save_screenshot("error_page.png")
            raise
        

    def update_or_create_property(self, price, location, surface, type, agency, url):
        # update_or_create es de Django ORM, objects es el gestor predeterminado para interactuar con la bd.
        property, created = Property.objects.update_or_create( # usa asignacion multiple. update_or_create() devuelve una tupla con: (objeto, booleano)
            url=url, # Campo único usado como identificador. Django lo usa para saber si el objeto ya existe, lo busca en bbdd
            defaults={
                'price': price,
                'location': location,
                'surface': surface,
                'last_updated': timezone.now()
            }
        )
        if created:
            property.first_seen = timezone.now()
            property.type = type
            property.agency = agency
            property.save()
            return f"New property added: {location}"
        else:
            return f"Property updated: {location}"

        
    def go_to_next_page(self):
        try:
            #self.logger.debug("Buscando botón de siguiente página")
            current_page = self.driver.current_url
            self.logger.debug(f"URL actual: {current_page}")

            self.logger.debug("Localizando el botón 'Siguiente'...")
        
            try:
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//li/a[contains(text(), '>')]")) ##################################################### ENTENDER
                )
                self.logger.debug("Botón 'Siguiente' encontrado.")
            except TimeoutException:
                self.logger.info("No se encontró el botón 'Siguiente'. Probablemente es la última página.")
                return False
            
            if not next_button:
                self.logger.warning("Botón 'Siguiente' no disponible.")
                return False
        
            next_url = next_button.get_attribute('href')
            self.logger.info(f"URL del botón 'Siguiente': {next_url}")

                # Desplazar hasta el botón
            self.logger.debug("Desplazando el foco al botón 'Siguiente'...")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)  # Pequeña pausa para asegurar que el desplazamiento se complete

            # Intentar hacer clic usando diferentes métodos
            try:
                self.logger.debug("Haciendo clic en el botón 'Siguiente'...")
                next_button.click()
            except ElementClickInterceptedException:
                self.logger.warning("Clic interceptado, intentando con JavaScript")
                self.driver.execute_script("arguments[0].click();", next_button)
            
            # Esperar a que la URL cambie
            WebDriverWait(self.driver, 20).until(EC.url_changes(current_page))
            self.logger.info(f"Página siguiente cargada: {self.driver.current_url}")
            
            # Verificar que realmente hemos cambiado de página
            if self.driver.current_url == current_page:
                self.logger.warning("La URL no cambió después de hacer clic en 'siguiente'")
                return False
            
            self.logger.info(f"Navegación a la página siguiente exitosa. Nueva URL: {self.driver.current_url}")
            # self.driver.get(next_url)
            #time.sleep(random.uniform(2, 4))  # Espera aleatoria para evitar detección
            # Verifica carga correcta
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".estates-list"))
            )
            return True
        # except:
        #     print("No more pages to scrape.")
        #     return False
        except Exception as e:
            self.logger.error(f"Error en paginación: {str(e)}", exc_info=True)
            self.driver.save_screenshot("pagination_error.png")
            return False
        
    def scrape(self):
        self.logger.info("Iniciando proceso de scraping")
        try:
            self.logger.info("Iniciando proceso de scraping")

            if self.driver is None:
                self.logger.error("Driver not initialized. Aborting scrape.")
                return False

            base_url = "https://www.tecnocasa.es/venta/piso/comunidad-de-madrid/madrid.html"
            min_price = "50000"
            max_price = "150000"
            url = f"{base_url}?region=cma&min_price={min_price}&max_price={max_price}"
            self.logger.debug(f"URL objetivo: {url}")
            self.driver.get(url)
            self.handle_cookies()

            while True:
                try:
                    self.process_page()
                    self.logger.debug("Procesamiento de página completado")
                    
                    # Aquí verificamos si el botón "Siguiente" es accesible
                    if not self.go_to_next_page():
                        self.logger.info("No hay más páginas. Terminando el scraping.")
                        break  # Salir del bucle si no se encuentra el botón de "Siguiente"
                except Exception as e:
                    self.logger.exception(f"Ocurrió un error durante el scraping: {str(e)}")
                    break  # Salir en caso de error crítico
        finally:
            self.close()  # Asegurarse de que el driver se cierre incluso si ocurre un error
        self.close()  # Asegurarse de que el driver se cierre incluso si ocurre un error    
        return ["Scraping process completed"]  # Return a list with a message

 

    def close(self):
        try:
            if hasattr(self, 'driver') and self.driver is not None:
                self.logger.debug("Cerrando el navegador...")
                self.driver.quit()
                self.logger.info("Navegador cerrado correctamente.")
                self.driver = None  # Inmediatamente establecer como None
        except Exception as e:
            self.logger.error(f"Error al cerrar el navegador: {e}", exc_info=True)
        finally:
            self.driver = None  # Asegurar que el driver queda como None


    # def close2(self):
    #     """Safely close the driver and clean up resources"""
    #     try:
    #         if hasattr(self, 'driver') and self.driver is not None:
    #             self.logger.debug("Cerrando el navegador...")
                
    #             # Store a temporary reference and set self.driver to None first
    #             driver_tmp = self.driver
    #             self.driver = None
                
    #             # Now close the driver using the temporary reference
    #             try:
    #                 driver_tmp.quit()
    #             except Exception as e:
    #                 self.logger.warning(f"Error al ejecutar driver_tmp.quit(): {str(e)}")
                
    #             # Clear any circular references
    #             if hasattr(driver_tmp, "service") and driver_tmp.service:
    #                 driver_tmp.service.process = None
                    
    #             self.logger.info("Navegador cerrado correctamente.")
    #     except Exception as e:
    #         self.logger.error(f"Error al cerrar el navegador: {str(e)}")
    #     finally:
    #         self.driver = None


# try:
#     url = "https://www.tecnocasa.es/venta/piso/comunidad-de-madrid/madrid.html?min_price=50000&max_price=150000"
#     #driver.get("https://www.tecnocasa.es/venta/piso/comunidad-de-madrid/madrid.html/")

#     # input_precios = driver.find_elements(By.CSS_SELECTOR, ".col-6 .my-input input.form-control")# el espacio = "dentro de"
#     # input_precios[0].send_keys("50000")
#     # input_precios[1].send_keys("150000")
#     # input_precios[1].send_keys(Keys.ENTER)
