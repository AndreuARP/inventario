# Monitoreo de Actualizaciones de Stock en Railway

## 🔍 Cómo verificar actualizaciones automáticas

### 1. **Railway Dashboard - Logs**
- Ve a tu proyecto en Railway
- Click en "Deployments" → "View Logs"
- Busca estos mensajes:

```
🔄 Iniciando actualización automática SFTP...
✅ Archivo descargado exitosamente
🎉 Actualización automática exitosa: 2025-XX-XX XX:XX:XX
📊 Productos actualizados: XXXX
```

### 2. **En la aplicación web**
- **Sidebar izquierdo**: Muestra "Total de productos" actualizado
- **Admin panel**: "Última actualización" con fecha y hora
- **Configuración SFTP**: Estado de última sincronización

### 3. **Horarios programados**
- Por defecto: **2:00 AM diariamente**
- Personalizable con variable `UPDATE_SCHEDULE_TIME`
- Logs cada 6 horas confirmando que está activo

### 4. **Variables de entorno Railway**
```
ENABLE_SCHEDULER=true          # Habilitar actualizaciones automáticas
UPDATE_SCHEDULE_TIME=02:00     # Cambiar horario (opcional)
```

## 📊 Indicadores en la aplicación:

### Sidebar (siempre visible):
- **📦 Total**: Número actualizado de productos
- **🔴 Stock Bajo**: Productos con stock crítico
- **🟡 Stock Medio**: Productos con stock moderado  
- **🟢 Stock Alto**: Productos con stock abundante

### Panel de Admin:
- **Última actualización SFTP**: Fecha y hora exacta
- **Estado de conexión**: Éxito o error
- **Productos sincronizados**: Cantidad actualizada

## ⏰ Cronograma típico:

```
02:00 AM - Descarga automática desde SFTP
02:01 AM - Validación del archivo CSV
02:01 AM - Actualización de base de datos
02:01 AM - Confirmación en logs
```

## 🚨 Detección de problemas:

### En Railway Logs buscar:
- ❌ **Error en descarga SFTP**: Problema de conexión
- ❌ **Error en validación CSV**: Archivo corrupto
- ❌ **Error guardando datos**: Problema de escritura

### Recuperación automática:
- Detecta actualizaciones perdidas al reiniciar
- Si han pasado >25 horas, ejecuta actualización inmediata
- Logs de recuperación disponibles

## 📈 Dashboard en tiempo real:

La aplicación muestra siempre el estado actual:
- **Productos totales**
- **Distribución por categorías de stock**
- **Última fecha de sincronización**
- **Estado del scheduler** (si está habilitado)