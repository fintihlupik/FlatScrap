# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.11
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files and keeps Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Create a non-privileged user that the app will run under
# ARG UID=10001
# RUN adduser \
#     --disabled-password \
#     --gecos "" \
#     --home "/nonexistent" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid "${UID}" \
#     appuser

# Switch to root to install system dependencies,  libmysqlclient-dev es librería necesaria para mysqlclient
USER root
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    firefox-esr \
    libx11-xcb1 \
    libxtst6 \
    libxrender1 \
    libdbus-glib-1-2 \
    libgtk-3-0 \
    libasound2 \
    fonts-liberation \
    libgl1-mesa-dri \
    libpci3 \
    pkg-config \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \ 
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/* 

# Instalar cron y herramientas adicionales
RUN apt-get update && apt-get install -y \
cron \
vim \
&& rm -rf /var/lib/apt/lists/*

# Crear directorios necesarios y asignar permisos para cron
RUN mkdir -p /var/run /var/log && \
chmod 0755 /var/run /var/log && \
touch /var/run/crond.pid && \
chmod 0644 /var/run/crond.pid && \
touch /var/log/cron.log && \
chmod 0644 /var/log/cron.log

# Copia el archivo local cronfile (que contiene las reglas de cron) al directorio /etc/cron.d/ con el nombre crape-cron.
COPY cronfile /etc/cron.d/scrape-cron

# Dar permisos adecuados al cronfile
RUN chmod 0644 /etc/cron.d/scrape-cron

# Registrar el cronjob
RUN crontab /etc/cron.d/scrape-cron

# Configure Fontconfig to avoid cache errors
RUN mkdir -p /tmp/cache/fontconfig && chmod 777 /tmp/cache/fontconfig
ENV FONTCONFIG_PATH=/tmp/cache/fontconfig

# Assign a valid home directory to appuser
# RUN usermod -d /home/appuser appuser && mkdir -p /home/appuser && chown appuser:appuser /home/appuser

# Download and install GeckoDriver
RUN case $(dpkg --print-architecture) in \
    amd64) ARCH=linux64 ;; \
    arm64) ARCH=linux-aarch64 ;; \
    *) echo "Unsupported architecture" && exit 1 ;; \
    esac && \
    wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-$ARCH.tar.gz && \
    tar -xvzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Install Python dependencies
COPY requirements.txt /app/
RUN python -m pip install --no-cache-dir -r requirements.txt

# Ensure permissions for MySQL database and source code
RUN mkdir -p /app/flatscrap && \
    # touch /app/flatscrap/db.sqlite3 && \
    chmod -R 777 /app/flatscrap && \
    chmod -R 777 /app

# Copy application source code
COPY . .

# Switch to non-privileged user
#USER appuser

# Expose the port used by the application
EXPOSE 8000
EXPOSE 8501 

# Default command to keep the container running
CMD ["tail", "-f", "/dev/null"]

# Uncomment to run cron when the container starts (and comment the previous CMD)
#CMD ["cron", "-f"]

# El comando predeterminado será iniciar ambos servicios (Django y Streamlit)
#CMD ["sh", "-c", "streamlit run streamlit/scraper_streamlit.py & python manage.py runserver 0.0.0.0:8000"]
