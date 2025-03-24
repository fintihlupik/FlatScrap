# FlatScrap

FlatScrap es un proyecto diseñado para facilitar la busqueda de propiedades económicas en la comunidad de Madrid.

## Instalación

1. Clona este repositorio:
    ```bash
    git clone https://github.com/fintihlupik/FlatScrap.git
    ```
2. Navega al directorio del proyecto:
    ```bash
    cd FlatScrap
    ```
3. Arranca el Docker:
    ```bash
    docker-compose up --build
    ```
4. Comprueba en otro terminal que se han levantado 2 contenedores: de aplicación en sí y de MySQL.
    ```bash
    docker ps
    ```

## Uso

Antes de nada solicitame las variables de entorno y guardalas en un .env en la raíz del proyecto.
Este proyecto tiene 3 formas de ejecución:

1. Un simple webscraper:
    ```bash
    docker exec -it flatscrap-server-1 bash
    cd flatscrap
    python manage.py migrate
    python manage.py tecnopiso
    ```
    para ver la base de datos (contraseña root):
    ```bash
    docker exec -it flatscrap-server-1 bash
    mysql -h db -u root -p
    ```
2. Un cron:
    ```bash
    docker exec -it flatscrap-server-1 service cron start
    ```
    para ver los logs:
    ```bash
    docker exec -it flatscrap-server-1 bash
    cat /var/log/cron.log
    ```

3. Una humilde interfaz web:
    ```bash
    docker exec -it flatscrap-server-1 bash
    cd flatscrap
    streamlit run streamlit/scraper_streamlit.py & python manage.py runserver 0.0.0.0:8000
    ```
    Abre tu navegador en `http://localhost:8501/`.

## Contribución

¡Las contribuciones son bienvenidas! Por favor, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad:
    ```bash
    git checkout -b nueva-funcionalidad
    ```
3. Realiza tus cambios y haz un commit:
    ```bash
    git commit -m "Añadir nueva funcionalidad"
    ```
4. Envía un pull request.

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
