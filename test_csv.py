#!/usr/bin/env python3
"""
Script simple para crear un archivo CSV de prueba en un servidor web local
Esto permite probar la funcionalidad de URL directa sin necesidad de FTP
"""

import http.server
import socketserver
import threading
import time

def create_test_csv():
    """Crear archivo CSV de prueba"""
    csv_content = """Codigo,Descripcion,Familia,Stock
T001,Tornillo Acero 4x30mm,Ferreteria,125
T002,Tuerca Hexagonal M8,Ferreteria,68
T003,Arandela Zinc 8mm,Ferreteria,245
E001,Cable Cobre 4mm,Electricidad,52
E002,Interruptor Doble,Electricidad,18
E003,Enchufe Triple,Electricidad,9
P001,Pintura Azul 1L,Pintura,6
P002,Rodillo Pro 25cm,Pintura,12
P003,Brocha 3 pulgadas,Pintura,28
H001,Martillo 500g,Herramientas,15
"""
    
    with open('productos_test.csv', 'w') as f:
        f.write(csv_content)
    print("✅ Archivo productos_test.csv creado")

def start_test_server():
    """Iniciar servidor web simple para servir el CSV"""
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Servidor iniciado en http://localhost:{PORT}")
        print(f"📁 URL del archivo: http://localhost:{PORT}/productos_test.csv")
        print("⏹️  Presione Ctrl+C para detener el servidor")
        httpd.serve_forever()

if __name__ == "__main__":
    create_test_csv()
    start_test_server()