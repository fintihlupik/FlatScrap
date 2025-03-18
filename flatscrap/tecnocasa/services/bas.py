import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.utils import timezone
from your_app.models import Property
import time
import random

class TecnocasaScraper:
    def __init__(self):
        self.driver = self.configure_driver()

    def configure_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        return uc.Chrome(options=options)

    def handle_cookies(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-default.deny-all-btn"))
        ).click()

    def order_by_newest(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ordina"))
        ).click() 
        self.driver.find_element(By.XPATH, "//span[text()='Más recientes']").click() 

    def process_page(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".property-listing"))
        )
        
        for card in self.driver.find_elements(By.CSS_SELECTOR, ".property-card"):
            title = card.find_element(By.CSS_SELECTOR, ".property-title").text
            price = card.find_element(By.CSS_SELECTOR, ".price").text
            location = card.find_element(By.CSS_SELECTOR, ".location").text
            url = card.find_element(By.CSS_SELECTOR, "a.property-link").get_attribute("href")
            
            self.update_or_create_property(title, price, location, url)

    def update_or_create_property(self, title, price, location, url):
        property, created = Property.objects.update_or_create(
            url=url,
            defaults={
                'title': title,
                'price': price,
                'location': location,
                'last_updated': timezone.now()
            }
        )
        if created:
            property.first_seen = timezone.now()
            property.save()
            return f"New property added: {title}"
        else:
            return f"Property updated: {title}"

    def go_to_next_page(self):
        try:
            next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.pagination-next:not(.disabled)")
            next_btn.click()
            time.sleep(random.uniform(2, 4))
            return True
        except:
            return False

    def scrape(self):
        self.driver.get("https://www.tecnocasa.es/venta/piso/comunidad-de-madrid/madrid.html/")
        self.handle_cookies()
        
        while True:
            yield from self.process_page()
            if not self.go_to_next_page():
                break

    def close(self):
        self.driver.quit()




from django.core.management.base import BaseCommand
from tecnocasa.services.pisoscrape import TecnocasaScraper

class Command(BaseCommand):
    help = 'Ejecuta el scraper de Tecnocasa para obtener propiedades'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--silent',
            action='store_true',
            help='Ejecutar en modo silencioso (sin output)'
        )

    def handle(self, *args, **options):
        scraper = TecnocasaScraper(verbose=not options['silent'])
        try:
            scraper.scrape()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error durante el scraping: {str(e)}'))
        finally:
            scraper.close()
            self.stdout.write(self.style.SUCCESS('\nOperación completada'))



def process_page(self):
    try:
        self.logger.debug("Iniciando procesamiento de página")
        
        if self.driver.current_url.endswith("/madrid.html"):
            self.logger.debug("Ordenando por más recientes")
            self.order_by_newest()
            
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".estates-list"))
        )
        self.logger.debug("Contenedor de propiedades encontrado")
        
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".estate-card")
        self.logger.info(f"Encontradas {len(cards)} propiedades en la página")
        
        if not cards:
            self.logger.warning("¡No se encontraron propiedades en la página!")
            return []

        for index, card in enumerate(cards, 1):
            try:
                self.logger.debug(f"Procesando propiedad {index}/{len(cards)}")
                
                # Captura de pantalla de depuración
                card.screenshot(f"debug_propiedad_{index}.png")
                
                # Extracción de datos con verificación
                location_element = card.find_element(By.CSS_SELECTOR, "h4.estate-card-subtitle")
                location = location_element.text if location_element else "N/A"
                
                price_element = card.find_element(By.CSS_SELECTOR, ".estate-card-current-price")
                price = price_element.text if price_element else "N/A"
                
                surface_element = card.find_element(By.CSS_SELECTOR, ".estate-card-surface span")
                surface = surface_element.text if surface_element else "N/A"
                
                url_element = card.find_element(By.CSS_SELECTOR, "a")
                url = url_element.get_attribute('href') if url_element else "N/A"
                
                self.logger.info(f"Datos extraídos - Ubicación: {location}, Precio: {price}, Superficie: {surface}, URL: {url}")
                self.update_or_create_property(price, location, surface, "Apartment", "Tecnocasa", url)
                
            except Exception as e:
                self.logger.error(f"Error procesando propiedad {index}: {str(e)}", exc_info=True)
                continue
                
        return True
        
    except Exception as e:
        self.logger.critical(f"Error crítico en process_page: {str(e)}", exc_info=True)
        self.driver.save_screenshot("error_page.png")
        raise


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



class TecnocasaScraper:
    def __init__(self):
        # self.driver = self.configure_driver()
        # self._setup_logger()
        self.driver = None  # Initialize as None
        self._setup_logger()
        self.driver = self.configure_driver()

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
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        return uc.Chrome(options=options)
    
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
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".estates-list"))
            )
            return True

        except Exception as e:
            self.logger.error(f"Error en paginación: {str(e)}", exc_info=True)
            self.driver.save_screenshot("pagination_error.png")
            return False
        
    def scrape(self):
        self.logger.info("Iniciando proceso de scraping")
        self.safe_close()  # Asegurarse de que el driver se cierre incluso si ocurre un error 

    def safe_close(self):
        """Safely close the driver and clean up resources"""
        try:
            if hasattr(self, 'driver') and self.driver is not None:
                self.logger.debug("Cerrando el navegador...")
                
                # Store a temporary reference and set self.driver to None first
                driver_tmp = self.driver
                self.driver = None
                
                # Now close the driver using the temporary reference
                driver_tmp.quit()
                self.logger.info("Navegador cerrado correctamente.")
        except Exception as e:
            self.logger.error(f"Error al cerrar el navegador: {str(e)}")
        finally:
            self.driver = None