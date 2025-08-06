"""
Panel de estado para Railway - Monitoreo de actualizaciones
"""
import os
import json
import streamlit as st
from datetime import datetime

def show_railway_status():
    """Mostrar estado del scheduler y actualizaciones en Railway"""
    if not os.environ.get("RAILWAY_ENVIRONMENT"):
        return
    
    st.markdown("### 📊 Estado Railway")
    
    # Estado del scheduler
    scheduler_enabled = os.environ.get("ENABLE_SCHEDULER", "false").lower() == "true"
    
    col1, col2 = st.columns(2)
    
    with col1:
        if scheduler_enabled:
            st.success("⏰ Scheduler Activo")
            schedule_time = os.environ.get("UPDATE_SCHEDULE_TIME", "02:00")
            st.info(f"Próxima: {schedule_time}")
        else:
            st.warning("⏰ Scheduler Deshabilitado")
            st.caption("Para habilitar: ENABLE_SCHEDULER=true")
    
    with col2:
        # Mostrar última actualización
        try:
            if os.path.exists("data/config.json"):
                with open("data/config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    last_update = config.get('last_update')
                    if last_update:
                        st.success("✅ Última actualización")
                        st.text(last_update)
                        
                        # Calcular tiempo transcurrido
                        try:
                            last_dt = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
                            now = datetime.now()
                            hours_ago = (now - last_dt).total_seconds() / 3600
                            st.caption(f"Hace {hours_ago:.1f} horas")
                        except:
                            pass
                    else:
                        st.info("⏳ Sin actualizaciones")
            else:
                st.info("⏳ Sin configuración")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Estado de conexión SFTP
    st.markdown("#### 🔗 Estado SFTP")
    try:
        if os.path.exists("data/config.json"):
            with open("data/config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
                sftp_config = config.get('sftp_config', {})
                
                if sftp_config.get('enabled'):
                    st.success("✅ SFTP Habilitado")
                    st.text(f"Host: {sftp_config.get('host', 'N/A')}")
                    st.text(f"Archivo: {sftp_config.get('file_path', 'N/A')}")
                else:
                    st.warning("⚠️ SFTP Deshabilitado")
    except:
        st.info("📋 Configuración por defecto")

def show_update_logs():
    """Mostrar logs recientes de actualización"""
    st.markdown("#### 📋 Logs Recientes")
    
    log_file = "data/scheduler.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                
            if recent_lines:
                for line in recent_lines:
                    line = line.strip()
                    if "✅" in line or "🎉" in line:
                        st.success(line)
                    elif "❌" in line or "💥" in line:
                        st.error(line)
                    elif "🔄" in line or "⏰" in line:
                        st.info(line)
                    else:
                        st.text(line)
            else:
                st.info("Sin logs disponibles")
        except Exception as e:
            st.error(f"Error leyendo logs: {str(e)}")
    else:
        st.info("Archivo de logs no encontrado")

def show_scheduler_status():
    """Mostrar estado detallado del scheduler"""
    status_file = "data/scheduler_status.json"
    
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            st.markdown("#### ⚙️ Estado del Worker")
            
            col1, col2 = st.columns(2)
            with col1:
                if status.get("worker_active"):
                    st.success("✅ Worker Activo")
                else:
                    st.error("❌ Worker Inactivo")
            
            with col2:
                last_check = status.get("last_check")
                if last_check:
                    st.info(f"Último check: {last_check}")
            
            next_run = status.get("next_run")
            if next_run:
                st.info(f"Próxima ejecución: {next_run}")
                
        except Exception as e:
            st.error(f"Error leyendo estado: {str(e)}")
    else:
        st.info("Estado del worker no disponible")