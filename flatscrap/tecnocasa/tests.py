from django.test import TestCase
from unittest.mock import patch, MagicMock
from .services.pisoscrape import TecnocasaScraper
from tecnocasa.models import Property
import logging
from selenium.common.exceptions import TimeoutException
from unittest.mock import patch, MagicMock
from selenium import webdriver

class TecnocasaScraperTestCase(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL) # Deshabilita logging durante la ejecución de los tests
        self.scraper = TecnocasaScraper()

        with patch.object(TecnocasaScraper, 'configure_driver', return_value=self.mock_firefox_driver()):
            self.scraper = TecnocasaScraper()

    def tearDown(self):
        logging.disable(logging.NOTSET) # Habilita logging después de la ejecución de cada test

    def mock_firefox_driver(self):
        mock_driver = MagicMock(spec=webdriver.Firefox) #Crea un mock del driver de Firefox.
        return mock_driver

    @patch('tecnocasa.services.pisoscrape.WebDriverWait')
    def test_handle_cookies(self, mock_wait):
        self.scraper.handle_cookies()
        mock_wait.assert_called_once()

    # @patch('tecnocasa.services.pisoscrape.WebDriverWait')
    # def test_order_by_newest(self, mock_wait):
    #     self.scraper.order_by_newest()
    #     self.assertEqual(mock_wait.call_count, 2)

    @patch('tecnocasa.services.pisoscrape.WebDriverWait')
    @patch('tecnocasa.services.pisoscrape.EC')
    def test_process_page(self, mock_ec, mock_wait):
        mock_driver = MagicMock()
        mock_driver.find_elements.return_value = [MagicMock()]
        self.scraper.driver = mock_driver
        self.scraper.process_page()
        self.assertEqual(mock_driver.find_elements.call_count, 2)

    @patch('tecnocasa.services.pisoscrape.WebDriverWait')
    def test_go_to_next_page(self, mock_wait):
        mock_driver = MagicMock()
        mock_driver.current_url = "https://www.tecnocasa.es/venta/piso/comunidad-de-madrid/madrid.html?min_price=50000&max_price=150000"  
        self.scraper.driver = mock_driver
        
        mock_wait.return_value.until.side_effect = TimeoutException  
        
        result = self.scraper.go_to_next_page()
        self.assertFalse(result)  
        mock_wait.assert_called()

    @patch.object(TecnocasaScraper, 'process_page')
    @patch.object(TecnocasaScraper, 'go_to_next_page')
    def test_scrape(self, mock_go_to_next_page, mock_process_page):
        mock_go_to_next_page.side_effect = [True, False]
        self.scraper.scrape()
        self.assertEqual(mock_process_page.call_count, 2)
        self.assertEqual(mock_go_to_next_page.call_count, 2)

    def test_update_or_create_property(self):
        property_data = {
            "price": "100000",
            "location": "Madrid",
            "surface": "50",
            "type": "Apartment",
            "agency": "Tecnocasa",
            "url": "https://example.com"
        }
        result = self.scraper.update_or_create_property(**property_data)
        self.assertIn("property added", result)
        self.assertEqual(Property.objects.count(), 1)

    def test_close(self):
        mock_driver = MagicMock()
        self.scraper.driver = mock_driver
        self.scraper.close()
        mock_driver.quit.assert_called_once()


