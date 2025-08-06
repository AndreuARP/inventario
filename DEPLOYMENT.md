# Guía de Deployment en Railway

## Archivos creados para Railway

### 1. Archivos principales:
- `app_railway.py` - Versión optimizada para Railway (funcionalidad reducida, más estable)
- `railway_app.py` - Launcher principal que maneja el puerto dinámico
- `Procfile` - Configuración del proceso web
- `runtime.txt` - Especifica Python 3.11

### 2. Archivos de configuración:
- `nixpacks.toml` - Configuración de build para Nixpacks
- `railway.json` - Configuración específica de Railway  
- `setup.py` - Configuración del paquete Python

### 3. Configuración de Streamlit:
- `.streamlit/config.toml` - Configuración actualizada para Railway

## Problemas corregidos

### 1. Puerto dinámico:
- Railway asigna puertos dinámicos via `$PORT`
- `railway_app.py` lee y configura automáticamente

### 2. Variables de entorno:
- `ADMIN_PASSWORD` - Contraseña de admin (por defecto: stock2025)
- `VIEWER_PASSWORD` - Contraseña de viewer (por defecto: lucero)
- `PORT` - Puerto asignado por Railway

### 3. Errores de código corregidos:
- Manejo seguro de pandas DataFrames
- Verificaciones de null values
- Manejo de errores en métricas

### 4. Optimizaciones:
- Código simplificado en `app_railway.py`
- Manejo de errores mejorado
- Detección automática de entorno Railway

## Instrucciones de deployment

### 1. En Railway:
1. Conectar repositorio GitHub
2. Railway detectará automáticamente los archivos de configuración
3. Las variables de entorno se configuran automáticamente

### 2. Variables de entorno opcionales:
```
ADMIN_PASSWORD=tu_contraseña_admin
VIEWER_PASSWORD=tu_contraseña_viewer
```

### 3. Comando de inicio:
```bash
python railway_app.py
```

## Funcionalidades disponibles en Railway:

### ✅ Funciona:
- Autenticación dual (admin/viewer)
- Visualización de productos
- Búsqueda y filtros
- Exportación CSV
- Métricas básicas
- Interfaz responsive

### ❌ Deshabilitado para Railway:
- Scheduler automático (puede causar problemas de recursos)
- Conexiones SFTP/FTP (puede necesitar configuración adicional)
- Hilos en background (limitados en Railway)

## Recomendaciones:

1. **Para desarrollo local**: usar `app.py` (versión completa)
2. **Para Railway**: usar `app_railway.py` (versión estable)
3. **Variables de entorno**: configurar contraseñas personalizadas
4. **Datos**: subir archivo CSV inicial via interfaz admin