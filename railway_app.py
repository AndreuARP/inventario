#!/usr/bin/env python3
"""
Archivo principal adaptado para Railway
Este archivo configura automáticamente el puerto desde las variables de entorno de Railway
"""

import os
import sys

# Configurar el puerto de Railway
port = int(os.environ.get("PORT", 8501))

# Configurar Streamlit para Railway
os.environ["STREAMLIT_SERVER_PORT"] = str(port)
os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# Ejecutar la aplicación principal
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    # Configurar argumentos para Streamlit
    sys.argv = [
        "streamlit",
        "run",
        "app_railway.py",
        f"--server.port={port}",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    
    sys.exit(stcli.main())