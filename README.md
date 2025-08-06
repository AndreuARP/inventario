# Sistema de Consulta de Stock - Distribuciones Lucero

## Descripción
Sistema web de gestión de inventario para Distribuciones Lucero, desarrollado con Streamlit. Permite consultar, gestionar y actualizar automáticamente el stock de productos.

## Características Principales
- 🔐 **Autenticación dual**: Admin y viewer
- 📊 **Gestión de inventario**: CRUD completo de productos
- 🔄 **Actualizaciones automáticas**: Integración SFTP programada
- 📈 **Dashboard visual**: Métricas y estadísticas en tiempo real
- 🎨 **Diseño corporativo**: Colores y branding de Distribuciones Lucero
- 📱 **Responsivo**: Interfaz adaptable a dispositivos móviles

## Deployment en Railway

Este proyecto está optimizado para deployment en Railway. Los archivos de configuración incluyen:

- `railway_app.py`: Launcher principal para Railway
- `Procfile`: Configuración del proceso web
- `nixpacks.toml`: Configuración de build
- `railway.json`: Configuración específica de Railway
- `runtime.txt`: Versión de Python

### Variables de Entorno
Railway configura automáticamente:
- `PORT`: Puerto dinámico asignado por Railway
- Configuraciones adicionales de Streamlit

## Instalación Local

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `streamlit run app.py`

## Credenciales por defecto
- Admin: `stock2025`
- Viewer: `lucero`

## Tecnologías
- **Python 3.11**
- **Streamlit**: Framework web
- **Pandas**: Manipulación de datos
- **Paramiko**: Conexiones SFTP/SSH
- **Schedule**: Tareas programadas