# Scheduler Automático en Railway

## Opciones para habilitar el scheduler

### Opción 1: Variable de entorno (Recomendado)

1. **En Railway Dashboard:**
   - Ve a tu proyecto → Variables
   - Añadir variable: `ENABLE_SCHEDULER=true`
   - Redeploy automático

2. **Configuraciones adicionales:**
   ```
   ENABLE_SCHEDULER=true
   UPDATE_SCHEDULE_TIME=02:00    # Opcional: cambiar horario
   ADMIN_PASSWORD=tu_contraseña  # Opcional: contraseña personalizada
   ```

### Opción 2: Railway Cron Jobs (Más estable)

Railway soporta trabajos programados separados:

1. **Crear nuevo servicio en Railway:**
   - Mismo repositorio
   - Tipo: "Cron Job"
   - Comando: `python scheduler_railway.py`
   - Schedule: `0 2 * * *` (diariamente a las 2:00 AM)

### Opción 3: Webhook externo

Usar servicios como:
- **Railway Cron**: Configurar webhook
- **GitHub Actions**: Programar llamadas HTTP
- **Zapier**: Automatización externa

## Archivos creados:

### `scheduler_railway.py`
- Scheduler optimizado para Railway
- Manejo de variables de entorno
- Logs compatibles con Railway
- Verificación de actualizaciones perdidas
- Thread daemon para no bloquear la app principal

### Variables de entorno soportadas:
- `ENABLE_SCHEDULER` - Habilitar/deshabilitar (true/false)
- `UPDATE_SCHEDULE_TIME` - Horario personalizado (formato HH:MM)
- Credenciales SFTP (ya configuradas en el código)

## Recomendación:

**Para Railway**: Usar **Opción 1** (variable de entorno) es la más simple:

1. En Railway Dashboard → tu proyecto → Variables
2. Añadir: `ENABLE_SCHEDULER=true`
3. La aplicación se reiniciará automáticamente
4. El scheduler iniciará en un thread separado

## Verificación:

Una vez habilitado, verás en los logs de Railway:
```
[2025-XX-XX XX:XX:XX] 🔧 ENABLE_SCHEDULER=true detectado, iniciando scheduler...
[2025-XX-XX XX:XX:XX] ✅ Railway scheduler iniciado en thread separado
[2025-XX-XX XX:XX:XX] 🚀 Railway Scheduler iniciado
[2025-XX-XX XX:XX:XX] ⏰ Scheduler activo - próxima ejecución: 2025-XX-XX 02:00:00
```

## Limitaciones en Railway:

- Los contenedores pueden reiniciarse
- El scheduler se reinicia con cada deploy
- Para máxima estabilidad, considera usar Cron Jobs separados (Opción 2)

## Testing:

Para probar inmediatamente:
```bash
python scheduler_railway.py
```