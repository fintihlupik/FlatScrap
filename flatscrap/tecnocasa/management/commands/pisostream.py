import subprocess
from django.core.management.base import BaseCommand
import time

class Command(BaseCommand):
    help = 'Inicia tanto el scraper de Streamlit como el servidor Django'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando el scraper de Streamlit..."))

        # Ejecutar Streamlit
        streamlit_process = subprocess.Popen(
            ['streamlit', 'run', 'streamlit/scraper_streamlit.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Un pequeño retraso para asegurar que Streamlit se ha iniciado correctamente
        time.sleep(5)  # Puedes ajustar este tiempo si es necesario

        self.stdout.write(self.style.SUCCESS("Streamlit iniciado correctamente."))

        self.stdout.write(self.style.SUCCESS("Iniciando el servidor de Django..."))

        # Ejecutar el servidor de Django
        server_process = subprocess.Popen(
            ['python', 'manage.py', 'runserver', '0.0.0.0:8000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self.stdout.write(self.style.SUCCESS("Servidor Django iniciado correctamente."))

        # Esperar a que los dos procesos terminen
        try:
            # Esperar a que Streamlit termine
            streamlit_stdout, streamlit_stderr = streamlit_process.communicate()
            if streamlit_process.returncode != 0:
                self.stdout.write(self.style.ERROR(f"Streamlit error: {streamlit_stderr.decode()}"))
            
            # Esperar a que el servidor de Django termine
            server_stdout, server_stderr = server_process.communicate()
            if server_process.returncode != 0:
                self.stdout.write(self.style.ERROR(f"Django server error: {server_stderr.decode()}"))
        
        except KeyboardInterrupt:
            # Si el usuario presiona Ctrl+C, cerrar ambos procesos
            self.stdout.write(self.style.SUCCESS("Interrupción manual, cerrando ambos procesos..."))
            streamlit_process.terminate()
            server_process.terminate()
