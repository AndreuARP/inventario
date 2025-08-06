import os
import threading
import time
import schedule
import json
from datetime import datetime
import paramiko
import pandas as pd
from io import StringIO

def log_message(message):
    """Log con timestamp para Railway"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def validate_csv_content(content):
    """Validar contenido CSV descargado"""
    try:
        df = pd.read_csv(StringIO(content))
        required_columns = ['Codigo', 'Descripcion', 'Familia', 'Stock']
        
        if all(col in df.columns for col in required_columns):
            return True, df
        else:
            return False, f"Columnas faltantes: {set(required_columns) - set(df.columns)}"
    except Exception as e:
        return False, f"Error al procesar CSV: {str(e)}"

def download_sftp_file(host, port, username, password, remote_path):
    """Descargar archivo via SFTP"""
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        with sftp.open(remote_path, 'r') as remote_file:
            content = remote_file.read().decode('utf-8')
        
        sftp.close()
        transport.close()
        return True, content, "Archivo descargado exitosamente"
    except Exception as e:
        return False, "", str(e)

def save_data(df):
    """Guardar datos CSV"""
    try:
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/productos.csv", index=False)
        return True
    except Exception as e:
        log_message(f"Error guardando datos: {str(e)}")
        return False

def load_config():
    """Cargar configuración"""
    default_config = {
        'sftp_config': {
            'enabled': True,
            'host': 'home567855122.1and1-data.host',
            'port': 22,
            'user': 'acc1195143440',
            'password': '@Q&jb@kpcU(OhpQv95bN0%eI',
            'file_path': '/stock/stock.csv'
        },
        'last_update': None
    }
    
    try:
        if os.path.exists("data/config.json"):
            with open("data/config.json", 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
                default_config.update(saved_config)
    except Exception as e:
        log_message(f"Error cargando config: {str(e)}")
    
    return default_config

def save_config(config):
    """Guardar configuración"""
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_message(f"Error guardando config: {str(e)}")

def run_scheduled_update():
    """Ejecutar actualización programada"""
    try:
        log_message("🔄 Iniciando actualización automática SFTP...")
        config = load_config()
        sftp_config = config.get('sftp_config', {})
        
        if not sftp_config.get('enabled', False):
            log_message("❌ SFTP deshabilitado en configuración")
            return
        
        success, content, message = download_sftp_file(
            sftp_config.get('host'),
            sftp_config.get('port', 22),
            sftp_config.get('user'),
            sftp_config.get('password'),
            sftp_config.get('file_path')
        )
        
        if success:
            log_message("✅ Archivo descargado exitosamente")
            is_valid, result = validate_csv_content(content)
            if is_valid:
                if save_data(result):
                    config['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_config(config)
                    log_message(f"🎉 Actualización automática exitosa: {config['last_update']}")
                    log_message(f"📊 Productos actualizados: {len(result)}")
                else:
                    log_message("❌ Error guardando datos")
            else:
                log_message(f"❌ Error en validación CSV: {result}")
        else:
            log_message(f"❌ Error en descarga SFTP: {message}")
            
    except Exception as e:
        log_message(f"💥 Error crítico en actualización automática: {str(e)}")

def railway_scheduler():
    """Scheduler optimizado para Railway"""
    log_message("🚀 Railway Scheduler iniciado")
    
    # Programar actualización a las 2:00 AM
    schedule.every().day.at("02:00").do(run_scheduled_update)
    
    # En Railway, usar variables de entorno para horarios personalizados
    custom_time = os.environ.get("UPDATE_SCHEDULE_TIME", "02:00")
    if custom_time != "02:00":
        schedule.clear()
        schedule.every().day.at(custom_time).do(run_scheduled_update)
        log_message(f"⏰ Horario personalizado configurado: {custom_time}")
    
    # Ejecutar verificación de actualizaciones perdidas al inicio
    check_missed_updates()
    
    while True:
        try:
            schedule.run_pending()
            
            # Log cada 6 horas para Railway logs
            current_time = datetime.now()
            if current_time.minute == 0 and current_time.hour % 6 == 0:
                next_run = schedule.next_run()
                if next_run:
                    log_message(f"⏰ Scheduler activo - próxima ejecución: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            time.sleep(60)  # Revisar cada minuto
            
        except Exception as e:
            log_message(f"💥 Error en scheduler: {str(e)}")
            time.sleep(300)  # Esperar 5 minutos antes de reintentar

def check_missed_updates():
    """Verificar actualizaciones perdidas - optimizado para Railway"""
    try:
        config = load_config()
        last_update_str = config.get('last_update', '')
        now = datetime.now()
        
        if last_update_str:
            last_update = datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S")
            hours_since = (now - last_update).total_seconds() / 3600
            
            # En Railway, verificar si han pasado más de 25 horas (considerando reinicio de contenedores)
            if hours_since > 25:
                log_message(f"🔍 Última actualización hace {hours_since:.1f} horas. Ejecutando actualización de recuperación...")
                run_scheduled_update()
        else:
            log_message("🔍 No hay registro de actualizaciones previas. Ejecutando primera actualización...")
            run_scheduled_update()
            
    except Exception as e:
        log_message(f"💥 Error verificando actualizaciones perdidas: {str(e)}")

def start_railway_scheduler():
    """Inicializar scheduler para Railway"""
    if os.environ.get("ENABLE_SCHEDULER", "false").lower() == "true":
        log_message("🔧 ENABLE_SCHEDULER=true detectado, iniciando scheduler...")
        scheduler_thread = threading.Thread(target=railway_scheduler, daemon=True)
        scheduler_thread.start()
        log_message("✅ Railway scheduler iniciado en thread separado")
        return scheduler_thread
    else:
        log_message("ℹ️ Scheduler deshabilitado. Para habilitar, configurar ENABLE_SCHEDULER=true")
        return None

if __name__ == "__main__":
    # Ejecutar solo el scheduler (útil para testing)
    railway_scheduler()