from django.core.management.base import BaseCommand
from tecnocasa.services.pisoscrape import TecnocasaScraper

class Command(BaseCommand):
    help = 'Scrape Tecnocasa website for apartments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--silent',
            action='store_true',
            help='Ejecutar en modo silencioso (sin output)'
        )

    def handle(self, *args, **options):
        scraper = TecnocasaScraper()
        try:
            for message in scraper.scrape():
                self.stdout.write(self.style.SUCCESS(message))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error durante el scraping: {str(e)}'))
        finally:
            scraper.close()