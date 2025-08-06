# Dockerfile personalizado para Railway
FROM python:3.11-slim

WORKDIR /app

# Copiar archivos
COPY . .

# Instalar dependencias de forma simple
RUN pip install --no-cache-dir streamlit pandas paramiko schedule requests

# Puerto para Railway
EXPOSE 8000

# Comando de inicio
CMD ["python", "railway_app.py"]