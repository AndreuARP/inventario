# Forzar Actualización Manual del Stock

## 🔄 Métodos para forzar actualizaciones

### 1. **Desde la aplicación web (Recomendado)**

**Para usuarios Admin:**
- En el sidebar aparece "Control Manual"
- Botón "⚡ Forzar Actualización"
- Click ejecuta actualización inmediata
- Muestra progreso y resultado

### 2. **Script de línea de comandos**

```bash
# Forzar actualización inmediata
python manual_update.py update

# Verificar configuración SFTP
python manual_update.py config

# Ver estado de última actualización
python manual_update.py status
```

### 3. **Railway Dashboard**

**Ejecutar comando directo:**
- Ve a tu proyecto Railway
- "Settings" → "Variables"  
- Temporalmente cambiar `UPDATE_SCHEDULE_TIME` a hora actual
- Reiniciar aplicación

### 4. **API endpoint (avanzado)**

Crear endpoint POST para triggering:
```python
# En app_railway.py agregar:
if st.button("API Update"):
    requests.post(f"http://tu-app.railway.app/trigger-update")
```

## 🚀 **Método más fácil - Botón en la app:**

1. Login como **admin** (contraseña: stock2025)
2. En sidebar verás "🔄 Control Manual"
3. Click "⚡ Forzar Actualización"
4. Espera 10-30 segundos
5. Los datos se actualizarán automáticamente

## ⏰ **Para testing rápido:**

### Cambiar horario temporalmente:
En Railway variables:
```
UPDATE_SCHEDULE_TIME=14:35  # Cambiar a hora actual + 2 minutos
```

La aplicación programará la próxima actualización para esa hora.

## 📊 **Verificación de resultados:**

Después de forzar actualización, verifica:
- **Sidebar:** "Última actualización" mostrará nueva fecha
- **Total productos:** Número actualizado
- **Railway logs:** Mensajes de éxito
- **Métricas:** Stock bajo/medio/alto recalculado

## 🔧 **Troubleshooting:**

### Si falla la actualización forzada:
1. Verificar configuración SFTP con: `python manual_update.py config`
2. Revisar logs de Railway para errores
3. Confirmar que `ENABLE_SCHEDULER=true`
4. Verificar conectividad del servidor

### Logs típicos de éxito:
```
⚡ ACTUALIZACIÓN MANUAL SOLICITADA
🔄 Iniciando actualización automática SFTP...
✅ Archivo descargado exitosamente
🎉 Actualización automática exitosa: 2025-XX-XX XX:XX:XX
📊 Productos actualizados: XXXX
```

## 🎯 **Recomendación:**

**Usa el botón en la aplicación web** - es la forma más fácil y segura de forzar actualizaciones. Solo necesitas ser admin y hacer click.