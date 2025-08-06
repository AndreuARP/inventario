#!/usr/bin/env python3
"""
Script para forzar actualización manual del stock
Útil para testing o actualizaciones inmediatas
"""

import sys
import os
from datetime import datetime

def manual_update():
    """Ejecutar actualización manual"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Iniciando actualización manual...")
    
    try:
        # Importar scheduler
        from scheduler_railway import run_scheduled_update, log_message
        
        log_message("⚡ ACTUALIZACIÓN MANUAL SOLICITADA")
        
        # Ejecutar actualización
        run_scheduled_update()
        
        print("✅ Actualización manual completada")
        return True
        
    except ImportError:
        print("❌ Error: No se pudo importar scheduler_railway.py")
        return False
    except Exception as e:
        print(f"❌ Error en actualización manual: {str(e)}")
        return False

def check_config():
    """Verificar configuración SFTP"""
    try:
        from scheduler_railway import load_config
        config = load_config()
        sftp_config = config.get('sftp_config', {})
        
        print("📋 Configuración SFTP:")
        print(f"  Habilitado: {sftp_config.get('enabled', False)}")
        print(f"  Host: {sftp_config.get('host', 'N/A')}")
        print(f"  Puerto: {sftp_config.get('port', 'N/A')}")
        print(f"  Usuario: {sftp_config.get('user', 'N/A')}")
        print(f"  Archivo: {sftp_config.get('file_path', 'N/A')}")
        
        return sftp_config.get('enabled', False)
        
    except Exception as e:
        print(f"❌ Error verificando configuración: {str(e)}")
        return False

def show_last_update():
    """Mostrar última actualización"""
    try:
        from scheduler_railway import load_config
        config = load_config()
        last_update = config.get('last_update')
        
        if last_update:
            print(f"✅ Última actualización: {last_update}")
        else:
            print("⏳ Sin actualizaciones previas")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    print("🚀 ACTUALIZADOR MANUAL DE STOCK - Railway")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "update":
            manual_update()
        elif command == "config":
            check_config()
        elif command == "status":
            show_last_update()
        else:
            print(f"❌ Comando desconocido: {command}")
            show_help()
    else:
        show_help()

def show_help():
    """Mostrar ayuda"""
    print("""
📖 COMANDOS DISPONIBLES:

python manual_update.py update    - Forzar actualización inmediata
python manual_update.py config    - Verificar configuración SFTP  
python manual_update.py status    - Ver última actualización

🔧 VARIABLES DE ENTORNO:
ENABLE_SCHEDULER=true            - Habilitar scheduler automático
UPDATE_SCHEDULE_TIME=02:00       - Cambiar horario de actualización

📋 EJEMPLOS:
# Actualización inmediata
python manual_update.py update

# Ver configuración
python manual_update.py config

# Estado actual  
python manual_update.py status
""")

if __name__ == "__main__":
    main()