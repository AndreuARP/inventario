import streamlit as st
import pandas as pd
import os
from io import StringIO
import csv
import ftplib
import socket
from datetime import datetime
import urllib.request
import urllib.error
import paramiko
import schedule
import time
import threading
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Consulta de Stock",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
PASSWORD = "stock2025"  # Contraseña por defecto, se puede cambiar por variable de entorno
CSV_FILE_PATH = "data/productos.csv"

def check_password():
    """Función para verificar la contraseña de acceso"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        st.title("🔐 Acceso al Sistema de Stock")
        st.markdown("---")
        
        password = st.text_input(
            "Ingrese la contraseña para acceder:",
            type="password",
            placeholder="Contraseña requerida"
        )
        
        if st.button("Ingresar", type="primary"):
            if password == PASSWORD:
                st.session_state.password_correct = True
                st.success("✅ Acceso concedido. Redirigiendo...")
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta. Intente nuevamente.")
        
        st.markdown("---")
        st.info("💡 Contacte al administrador del sistema si no tiene acceso.")
        return False
    
    return True

def load_data():
    """Cargar datos desde el archivo CSV"""
    try:
        if os.path.exists(CSV_FILE_PATH):
            df = pd.read_csv(CSV_FILE_PATH)
            # Validar que tenga las columnas requeridas
            required_columns = ['Codigo', 'Descripcion', 'Familia', 'Stock']
            if all(col in df.columns for col in required_columns):
                return df
            else:
                st.error(f"❌ El archivo CSV debe contener las columnas: {', '.join(required_columns)}")
                return pd.DataFrame(columns=required_columns)
        else:
            # Crear archivo CSV vacío con estructura correcta
            os.makedirs("data", exist_ok=True)
            df = pd.DataFrame(columns=['Codigo', 'Descripcion', 'Familia', 'Stock'])
            df.to_csv(CSV_FILE_PATH, index=False)
            return df
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        return pd.DataFrame(columns=['Codigo', 'Descripcion', 'Familia', 'Stock'])

def save_data(df):
    """Guardar datos en el archivo CSV"""
    try:
        os.makedirs("data", exist_ok=True)
        df.to_csv(CSV_FILE_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"❌ Error al guardar los datos: {str(e)}")
        return False

def download_from_ftp(ftp_host, ftp_user, ftp_password, ftp_file_path, ftp_port=21, passive_mode=True, timeout=30):
    """Descargar archivo CSV desde servidor FTP"""
    ftp = None
    try:
        # Validar parámetros
        if not all([ftp_host, ftp_user, ftp_password, ftp_file_path]):
            return False, "Faltan parámetros de conexión FTP"
        
        # Conectar al servidor FTP
        ftp = ftplib.FTP()
        ftp.set_debuglevel(0)  # Desactivar debug para producción
        
        # Intentar conexión
        try:
            ftp.connect(ftp_host, ftp_port, timeout=timeout)
            # Configurar modo pasivo según parámetro
            ftp.set_pasv(passive_mode)
        except Exception as e:
            return False, f"No se pudo conectar al servidor {ftp_host}:{ftp_port} - {str(e)}"
        
        # Intentar login
        try:
            ftp.login(ftp_user, ftp_password)
        except Exception as e:
            return False, f"Error de autenticación para usuario '{ftp_user}' - {str(e)}"
        
        # Verificar que el archivo existe
        try:
            ftp.size(ftp_file_path)
        except Exception as e:
            return False, f"Archivo '{ftp_file_path}' no encontrado en el servidor - {str(e)}"
        
        # Descargar el archivo
        csv_content = []
        try:
            ftp.retrlines(f'RETR {ftp_file_path}', csv_content.append)
        except Exception as e:
            return False, f"Error al descargar el archivo '{ftp_file_path}' - {str(e)}"
        
        # Verificar que se descargó contenido
        if not csv_content:
            return False, "El archivo descargado está vacío"
        
        # Unir las líneas del archivo
        csv_string = '\n'.join(csv_content)
        
        return True, csv_string
        
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"
    finally:
        # Cerrar conexión de forma segura
        if ftp:
            try:
                ftp.quit()
            except:
                try:
                    ftp.close()
                except:
                    pass

def check_network_connectivity(host, port, timeout=5):
    """Verificar conectividad de red básica antes de FTP"""
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_ftp_connection(ftp_host, ftp_user, ftp_password, ftp_port=21, passive_mode=True, timeout=10):
    """Probar la conectividad FTP sin descargar archivos"""
    # Primero verificar conectividad básica
    if not check_network_connectivity(ftp_host, ftp_port, timeout=5):
        return False, f"No se puede alcanzar el servidor {ftp_host}:{ftp_port}. Verifique la dirección y puerto."
    
    ftp = None
    try:
        ftp = ftplib.FTP()
        ftp.set_debuglevel(0)
        
        # Probar conexión
        ftp.connect(ftp_host, ftp_port, timeout=timeout)
        # Configurar modo pasivo según parámetro
        ftp.set_pasv(passive_mode)
        
        # Probar login
        ftp.login(ftp_user, ftp_password)
        
        # Obtener directorio actual para confirmar que funciona
        current_dir = ftp.pwd()
        
        return True, f"Conexión exitosa. Directorio actual: {current_dir}"
        
    except ftplib.error_perm as e:
        if "530" in str(e):
            return False, f"Error de autenticación: Usuario '{ftp_user}' o contraseña incorrectos"
        else:
            return False, f"Error de permisos FTP: {str(e)}"
    except ftplib.error_temp as e:
        return False, f"Error temporal del servidor FTP: {str(e)}"
    except socket.timeout:
        return False, f"Timeout de conexión. El servidor {ftp_host}:{ftp_port} no responde en {timeout} segundos"
    except ConnectionRefusedError:
        return False, f"Conexión rechazada por {ftp_host}:{ftp_port}. Verifique que el servicio FTP esté ejecutándose"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"
    finally:
        if ftp:
            try:
                ftp.quit()
            except:
                try:
                    ftp.close()
                except:
                    pass

def auto_diagnose_ftp(ftp_host, ftp_user, ftp_password, ftp_port=21):
    """Diagnóstico automático probando diferentes configuraciones FTP"""
    configurations = [
        {"passive": True, "timeout": 30, "description": "Modo pasivo (recomendado)"},
        {"passive": False, "timeout": 30, "description": "Modo activo"},
        {"passive": True, "timeout": 60, "description": "Modo pasivo con timeout extendido"},
        {"passive": False, "timeout": 60, "description": "Modo activo con timeout extendido"},
    ]
    
    results = []
    for config in configurations:
        success, message = test_ftp_connection(
            ftp_host, ftp_user, ftp_password, ftp_port, 
            config["passive"], config["timeout"]
        )
        results.append({
            "config": config["description"],
            "success": success,
            "message": message
        })
        if success:
            return True, config, results
    
    return False, None, results

def download_from_url(url, timeout=30):
    """Descargar archivo CSV desde URL directa"""
    try:
        # Configurar timeout
        urllib.request.socket.setdefaulttimeout(timeout)
        
        # Descargar el archivo
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
            return True, content
            
    except urllib.error.HTTPError as e:
        return False, f"Error HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Error de URL: {str(e.reason)}"
    except socket.timeout:
        return False, f"Timeout: La descarga tardó más de {timeout} segundos"
    except Exception as e:
        return False, f"Error al descargar: {str(e)}"

def download_from_sftp(sftp_host, sftp_user, sftp_password, sftp_file_path, sftp_port=22, timeout=30):
    """Descargar archivo CSV desde servidor SFTP"""
    ssh = None
    sftp = None
    try:
        # Validar parámetros
        if not all([sftp_host, sftp_user, sftp_password, sftp_file_path]):
            return False, "Faltan parámetros de conexión SFTP"
        
        # Crear cliente SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conectar
        ssh.connect(
            hostname=sftp_host,
            port=sftp_port,
            username=sftp_user,
            password=sftp_password,
            timeout=timeout,
            look_for_keys=False,
            allow_agent=False
        )
        
        # Crear cliente SFTP
        sftp = ssh.open_sftp()
        
        # Verificar que el archivo existe
        try:
            sftp.stat(sftp_file_path)
        except FileNotFoundError:
            return False, f"Archivo '{sftp_file_path}' no encontrado en el servidor SFTP"
        
        # Descargar el archivo - probar diferentes métodos
        try:
            # Método 1: Modo texto con UTF-8
            with sftp.open(sftp_file_path, 'r', encoding='utf-8') as remote_file:
                content = remote_file.read()
        except (UnicodeDecodeError, Exception):
            try:
                # Método 2: Modo binario y decodificar UTF-8
                with sftp.open(sftp_file_path, 'rb') as remote_file:
                    content_bytes = remote_file.read()
                    content = content_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # Método 3: Probar con latin-1 
                    content = content_bytes.decode('latin-1')
                except:
                    # Método 4: Forzar UTF-8 ignorando errores
                    content = content_bytes.decode('utf-8', errors='ignore')
            
        return True, content
        
    except paramiko.AuthenticationException:
        return False, f"Error de autenticación SFTP para usuario '{sftp_user}'"
    except paramiko.SSHException as e:
        return False, f"Error SSH: {str(e)}"
    except socket.timeout:
        return False, f"Timeout de conexión SFTP ({timeout}s)"
    except Exception as e:
        return False, f"Error SFTP: {str(e)}"
    finally:
        # Cerrar conexiones
        if sftp:
            try:
                sftp.close()
            except:
                pass
        if ssh:
            try:
                ssh.close()
            except:
                pass

def test_sftp_connection(sftp_host, sftp_user, sftp_password, sftp_port=22, timeout=10):
    """Probar la conectividad SFTP"""
    ssh = None
    sftp = None
    try:
        # Crear cliente SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conectar
        ssh.connect(
            hostname=sftp_host,
            port=sftp_port,
            username=sftp_user,
            password=sftp_password,
            timeout=timeout,
            look_for_keys=False,
            allow_agent=False
        )
        
        # Crear cliente SFTP para probar
        sftp = ssh.open_sftp()
        
        # Obtener directorio actual
        current_dir = sftp.getcwd() or "/"
        
        return True, f"Conexión SFTP exitosa. Directorio actual: {current_dir}"
        
    except paramiko.AuthenticationException:
        return False, f"Error de autenticación SFTP para usuario '{sftp_user}'"
    except paramiko.SSHException as e:
        return False, f"Error SSH: {str(e)}"
    except socket.timeout:
        return False, f"Timeout de conexión SFTP ({timeout}s)"
    except Exception as e:
        return False, f"Error SFTP: {str(e)}"
    finally:
        if sftp:
            try:
                sftp.close()
            except:
                pass
        if ssh:
            try:
                ssh.close()
            except:
                pass

def auto_update_from_ftp():
    """Función para actualización automática desde FTP/SFTP"""
    # Priorizar SFTP si está configurado
    if 'sftp_config' in st.session_state and 'auto_ftp_enabled' in st.session_state:
        config = st.session_state.sftp_config
        password = st.session_state.get('sftp_password', '@Q&jb@kpcU(OhpQv95bN0%eI')
        
        if all([config['host'], config['user'], config['file_path'], password]):
            try:
                success, result = download_from_sftp(
                    config['host'], 
                    config['user'], 
                    password, 
                    config['file_path'], 
                    config['port'],
                    config.get('timeout', 30)
                )
                
                if success:
                    is_valid, csv_result = validate_csv_content(result)
                    if is_valid:
                        if save_data(csv_result):
                            st.session_state['last_auto_update'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            return True
                return False
            except:
                return False
    
    # Fallback a FTP si SFTP no está configurado
    if 'ftp_config' in st.session_state and 'auto_ftp_enabled' in st.session_state:
        config = st.session_state.ftp_config
        password = st.session_state.get('ftp_password', '')
        
        if all([config['host'], config['user'], config['file_path'], password]):
            try:
                success, result = download_from_ftp(
                    config['host'], 
                    config['user'], 
                    password, 
                    config['file_path'], 
                    config['port']
                )
                
                if success:
                    is_valid, csv_result = validate_csv_content(result)
                    if is_valid:
                        if save_data(csv_result):
                            st.session_state['last_auto_update'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            return True
                return False
            except:
                return False
    return False

def schedule_worker():
    """Worker que ejecuta las tareas programadas"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisa cada minuto

# Inicializar el hilo de programación si no existe
if 'scheduler_started' not in st.session_state:
    st.session_state.scheduler_started = True
    # Programar actualización diaria a las 6:00 AM
    schedule.every().day.at("06:00").do(auto_update_from_ftp)
    # Iniciar el worker en un hilo separado
    scheduler_thread = threading.Thread(target=schedule_worker, daemon=True)
    scheduler_thread.start()

def validate_csv_content(content):
    """Validar el contenido del archivo CSV"""
    try:
        # Leer el contenido como DataFrame
        df = pd.read_csv(StringIO(content))
        
        # Verificar columnas requeridas
        required_columns = ['Codigo', 'Descripcion', 'Familia', 'Stock']
        if not all(col in df.columns for col in required_columns):
            return False, f"El archivo debe contener las columnas: {', '.join(required_columns)}"
        
        # Verificar que Stock sea numérico
        try:
            df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce')
            if df['Stock'].isna().any():
                return False, "La columna 'Stock' debe contener solo valores numéricos"
        except:
            return False, "Error al procesar la columna 'Stock'"
        
        # Verificar que no haya códigos duplicados
        if df['Codigo'].duplicated().any():
            return False, "Se encontraron códigos de producto duplicados"
        
        return True, df
    
    except Exception as e:
        return False, f"Error al procesar el archivo: {str(e)}"

def get_stock_color(stock):
    """Obtener color para el indicador de stock"""
    try:
        stock_num = float(stock)
        if stock_num <= 5:
            return "🔴"  # Stock bajo
        elif stock_num <= 20:
            return "🟡"  # Stock medio
        else:
            return "🟢"  # Stock alto
    except:
        return "⚪"  # Sin datos

def filter_dataframe(df, search_term):
    """Filtrar DataFrame por término de búsqueda"""
    if not search_term:
        return df
    
    # Convertir todo a string para búsqueda
    search_term = str(search_term).lower()
    
    # Buscar en todas las columnas
    mask = (
        df['Codigo'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Descripcion'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Familia'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Stock'].astype(str).str.lower().str.contains(search_term, na=False)
    )
    
    return df[mask]

def main():
    """Función principal de la aplicación"""
    # Verificar contraseña
    if not check_password():
        return
    
    # Título principal
    st.title("📦 Sistema de Consulta de Stock")
    st.markdown("---")
    
    # Sidebar para carga de archivos
    with st.sidebar:
        st.header("🔧 Administración")
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", type="secondary"):
            st.session_state.password_correct = False
            st.rerun()
        
        st.markdown("---")
        
        # Sección de carga de archivos
        st.subheader("📂 Actualizar Datos")
        
        # Tabs para diferentes métodos de carga
        tab1, tab2, tab3, tab4 = st.tabs(["📁 Archivo Local", "🌐 Servidor FTP", "🔐 Servidor SFTP", "🔗 URL Directa"])
        
        with tab1:
            uploaded_file = st.file_uploader(
                "Cargar archivo CSV:",
                type=['csv'],
                help="El archivo debe contener las columnas: Codigo, Descripcion, Familia, Stock"
            )
            
            if uploaded_file is not None:
                # Leer contenido del archivo
                content = uploaded_file.read().decode('utf-8')
                
                # Validar contenido
                is_valid, result = validate_csv_content(content)
                
                if is_valid:
                    st.success("✅ Archivo válido")
                    
                    if st.button("💾 Actualizar Base de Datos", type="primary", key="local_update"):
                        if save_data(result):
                            st.success("🎉 ¡Datos actualizados exitosamente!")
                            st.rerun()
                else:
                    st.error(f"❌ {result}")
        
        with tab2:
            st.markdown("**Configuración del Servidor FTP:**")
            
            # Información de ayuda
            with st.expander("💡 Ayuda con Configuración FTP"):
                st.markdown("""
                **Ejemplos de configuración común:**
                
                - **Servidor FTP estándar:**
                  - Puerto: 21 (por defecto)
                  - Ruta archivo: `/ruta/completa/productos.csv`
                
                - **Servidor SFTP:**
                  - Puerto: 22 (usar puerto SFTP si aplica)
                  
                - **Servidores de hosting:**
                  - Host: `ftp.tudominio.com` o IP del servidor
                  - Usuario: tu usuario FTP
                  - Ruta: `/public_html/data/productos.csv`
                
                **Problemas comunes y soluciones:**
                - ❌ "Connection refused": Revisar host y puerto
                - ❌ "Authentication failed": Verificar usuario/contraseña
                - ❌ "File not found": Confirmar ruta completa del archivo
                - ❌ "Timeout": Probar modo activo/pasivo o usar URL directa
                - ❌ "No se puede alcanzar": Firewall o red bloqueando conexión
                
                **💡 Alternativa recomendada:**
                Si FTP sigue fallando, use la pestaña "URL Directa" que es más compatible con firewalls y redes empresariales.
                """)
            
            # Inicializar configuración FTP en session state
            if 'ftp_config' not in st.session_state:
                st.session_state.ftp_config = {
                    'host': '',
                    'port': 21,
                    'user': '',
                    'file_path': ''
                }
            
            # Inicializar configuración SFTP en session state  
            if 'sftp_config' not in st.session_state:
                st.session_state.sftp_config = {
                    'host': 'home567855122.1and1-data.host',
                    'port': 22,
                    'user': 'acc1195143440',
                    'file_path': '/stock/stock.csv',
                    'timeout': 30
                }
            
            with st.form("ftp_form"):
                ftp_host = st.text_input(
                    "Servidor FTP:", 
                    value=st.session_state.ftp_config['host'],
                    placeholder="ftp.ejemplo.com"
                )
                ftp_port = st.number_input(
                    "Puerto:", 
                    value=st.session_state.ftp_config['port'], 
                    min_value=1, 
                    max_value=65535
                )
                ftp_user = st.text_input(
                    "Usuario:", 
                    value=st.session_state.ftp_config['user'],
                    placeholder="usuario"
                )
                ftp_password = st.text_input(
                    "Contraseña:", 
                    type="password",
                    help="La contraseña se guardará de forma segura para actualizaciones automáticas"
                )
                ftp_file_path = st.text_input(
                    "Ruta del archivo:", 
                    value=st.session_state.ftp_config['file_path'],
                    placeholder="/data/productos.csv"
                )
                
                # Opciones avanzadas
                with st.expander("⚙️ Configuración Avanzada"):
                    passive_mode = st.checkbox(
                        "Modo Pasivo (recomendado para firewalls)", 
                        value=True,
                        help="El modo pasivo resuelve problemas de conexión en la mayoría de casos"
                    )
                    connection_timeout = st.slider(
                        "Timeout de conexión (segundos):", 
                        min_value=5, 
                        max_value=60, 
                        value=30
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    save_config = st.form_submit_button("💾 Guardar Configuración")
                    test_connection = st.form_submit_button("🔧 Probar Conexión")
                with col2:
                    auto_diagnose = st.form_submit_button("🩺 Diagnóstico Automático")
                    download_ftp = st.form_submit_button("🔄 Descargar desde FTP", type="primary")
                
                if save_config:
                    st.session_state.ftp_config = {
                        'host': ftp_host,
                        'port': ftp_port,
                        'user': ftp_user,
                        'file_path': ftp_file_path
                    }
                    if ftp_password:
                        st.session_state.ftp_password = ftp_password
                    st.success("✅ Configuración FTP guardada")
                    st.rerun()
                
                if test_connection:
                    if all([ftp_host, ftp_user, ftp_password]):
                        with st.spinner("Probando conexión FTP..."):
                            success, message = test_ftp_connection(
                                ftp_host, ftp_user, ftp_password, ftp_port, 
                                passive_mode, connection_timeout
                            )
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
                                # Sugerencia para probar modo alternativo
                                if "timed out" in message.lower():
                                    st.info("💡 Intenta desactivar el 'Modo Pasivo' en configuración avanzada")
                    else:
                        st.error("❌ Complete todos los campos para probar la conexión")
                
                if auto_diagnose:
                    if all([ftp_host, ftp_user, ftp_password]):
                        with st.spinner("Ejecutando diagnóstico automático..."):
                            success, best_config, all_results = auto_diagnose_ftp(ftp_host, ftp_user, ftp_password, ftp_port)
                            
                            if success:
                                st.success(f"✅ Conexión exitosa con: {best_config['description']}")
                                st.info(f"💡 Configuración recomendada: Modo Pasivo = {best_config['passive']}, Timeout = {best_config['timeout']}s")
                            else:
                                st.error("❌ No se pudo establecer conexión con ninguna configuración")
                            
                            # Mostrar resultados detallados
                            with st.expander("Ver resultados detallados del diagnóstico"):
                                for result in all_results:
                                    if result['success']:
                                        st.success(f"✅ {result['config']}: {result['message']}")
                                    else:
                                        st.error(f"❌ {result['config']}: {result['message']}")
                    else:
                        st.error("❌ Complete todos los campos para ejecutar el diagnóstico")
                
                if download_ftp:
                    if all([ftp_host, ftp_user, ftp_password, ftp_file_path]):
                        # Guardar configuración automáticamente al descargar
                        st.session_state.ftp_config = {
                            'host': ftp_host,
                            'port': ftp_port,
                            'user': ftp_user,
                            'file_path': ftp_file_path
                        }
                        if ftp_password:
                            st.session_state.ftp_password = ftp_password
                        
                        with st.spinner("Conectando al servidor FTP..."):
                            success, result = download_from_ftp(
                                ftp_host, ftp_user, ftp_password, ftp_file_path, ftp_port,
                                passive_mode, connection_timeout
                            )
                            
                            if success:
                                # Validar contenido descargado
                                is_valid, csv_result = validate_csv_content(result)
                                
                                if is_valid:
                                    st.success("✅ Archivo descargado y validado correctamente")
                                    st.info(f"📊 Se encontraron {len(csv_result)} productos")
                                    
                                    if st.button("💾 Actualizar Base de Datos", type="primary", key="ftp_update"):
                                        if save_data(csv_result):
                                            st.success("🎉 ¡Datos actualizados desde FTP exitosamente!")
                                            st.rerun()
                                else:
                                    st.error(f"❌ Error en el archivo descargado: {csv_result}")
                            else:
                                st.error(f"❌ {result}")
                    else:
                        st.error("❌ Por favor complete todos los campos")
            
            # Configuración de actualización automática
            st.markdown("---")
            st.markdown("**Actualización Automática:**")
            
            # Inicializar configuración automática (activada por defecto para SFTP)
            if 'auto_ftp_enabled' not in st.session_state:
                # Activar automáticamente si tenemos configuración SFTP
                has_sftp_config = (
                    'sftp_config' in st.session_state and 
                    st.session_state.sftp_config.get('host') == 'home567855122.1and1-data.host'
                )
                st.session_state.auto_ftp_enabled = has_sftp_config
            
            # Mostrar mensaje si está habilitado por defecto
            if st.session_state.auto_ftp_enabled and 'sftp_config' in st.session_state:
                st.success("🌙 Actualización nocturna automática activada con tu configuración SFTP")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                auto_enabled = st.checkbox(
                    "Activar actualización automática diaria (2:00 AM)",
                    value=st.session_state.auto_ftp_enabled,
                    help="Descarga automáticamente el archivo desde SFTP todas las noches"
                )
            
            with col2:
                if st.button("🔄 Actualizar Ahora", help="Ejecutar actualización inmediata"):
                    # Priorizar SFTP si está configurado
                    if 'sftp_config' in st.session_state and st.session_state.get('sftp_password'):
                        with st.spinner("Actualizando desde SFTP..."):
                            if auto_update_from_ftp():
                                st.success("✅ Actualización automática desde SFTP completada")
                                st.rerun()
                            else:
                                st.error("❌ Error en la actualización automática desde SFTP")
                    elif 'ftp_config' in st.session_state and st.session_state.get('ftp_password'):
                        with st.spinner("Actualizando desde FTP..."):
                            if auto_update_from_ftp():
                                st.success("✅ Actualización automática desde FTP completada")
                                st.rerun()
                            else:
                                st.error("❌ Error en la actualización automática desde FTP")
                    else:
                        st.error("❌ Configure primero los datos de FTP o SFTP")
            
            # Guardar estado de configuración automática
            if auto_enabled != st.session_state.auto_ftp_enabled:
                st.session_state.auto_ftp_enabled = auto_enabled
                if auto_enabled:
                    # Verificar si tenemos configuración SFTP
                    if 'sftp_config' in st.session_state and st.session_state.sftp_config.get('host'):
                        # Configurar actualización automática para las 2:00 AM
                        schedule.clear()
                        schedule.every().day.at("02:00").do(auto_update_from_ftp)
                        st.success("✅ Actualización automática activada para las 2:00 AM (SFTP)")
                        st.session_state.sftp_password = "@Q&jb@kpcU(OhpQv95bN0%eI"  # Establecer contraseña
                    elif 'ftp_config' in st.session_state:
                        # Verificar que tengamos la contraseña guardada para FTP
                        if not st.session_state.get('ftp_password'):
                            st.warning("⚠️ Para la actualización automática, ingrese la contraseña FTP arriba")
                        else:
                            schedule.clear()
                            schedule.every().day.at("02:00").do(auto_update_from_ftp)
                            st.success("✅ Actualización automática activada para las 2:00 AM (FTP)")
                    else:
                        st.warning("⚠️ Configure primero los datos de conexión")
                elif not auto_enabled:
                    schedule.clear()
                    st.info("ℹ️ Actualización automática desactivada")
            
            # Configurar tiempo personalizado
            if auto_enabled:
                st.markdown("**Horario Personalizado:**")
                col1, col2 = st.columns(2)
                with col1:
                    update_hour = st.selectbox("Hora:", list(range(24)), index=2, help="Hora nocturna recomendada: 1-4 AM")
                with col2:
                    update_minute = st.selectbox("Minuto:", [0, 15, 30, 45], index=0)
                
                if st.button("⏰ Cambiar Horario"):
                    # Limpiar trabajos anteriores
                    schedule.clear()
                    # Programar nuevo horario
                    time_str = f"{update_hour:02d}:{update_minute:02d}"
                    schedule.every().day.at(time_str).do(auto_update_from_ftp)
                    st.success(f"✅ Actualización programada para las {time_str} (horario nocturno)")
                    
                # Mostrar horario actual configurado
                next_run = schedule.next_run()
                if next_run:
                    st.info(f"🌙 Próxima actualización nocturna: {next_run.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Mostrar información de última actualización
            st.markdown("---")
            if os.path.exists(CSV_FILE_PATH):
                mod_time = os.path.getmtime(CSV_FILE_PATH)
                last_update = datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M:%S")
                st.info(f"📅 Última actualización: {last_update}")
            
            # Mostrar última actualización automática
            if 'last_auto_update' in st.session_state:
                st.info(f"🤖 Última actualización automática: {st.session_state.last_auto_update}")
            
            # Estado del programador
            if auto_enabled:
                next_run = schedule.next_run()
                if next_run:
                    st.info(f"⏳ Próxima actualización: {next_run.strftime('%d/%m/%Y %H:%M:%S')}")
        
        with tab3:
            st.markdown("**Configuración del Servidor SFTP (SSH):**")
            st.success("✅ SFTP detectado - Esta es la configuración correcta para tu servidor")
            st.info("🔧 Configuración preestablecida - Los datos ya están configurados para tu servidor")
            
            with st.form("sftp_form"):
                sftp_host = st.text_input(
                    "Servidor SFTP:", 
                    value=st.session_state.sftp_config['host'],
                    placeholder="sftp.ejemplo.com"
                )
                sftp_port = st.number_input(
                    "Puerto SSH:", 
                    value=st.session_state.sftp_config['port'], 
                    min_value=1, 
                    max_value=65535
                )
                sftp_user = st.text_input(
                    "Usuario SSH:", 
                    value=st.session_state.sftp_config['user'],
                    placeholder="usuario"
                )
                sftp_password = st.text_input(
                    "Contraseña SSH:", 
                    type="password",
                    value="@Q&jb@kpcU(OhpQv95bN0%eI",
                    help="Contraseña preconfigurada para el servidor"
                )
                sftp_file_path = st.text_input(
                    "Ruta del archivo:", 
                    value=st.session_state.sftp_config['file_path'],
                    placeholder="/home/usuario/datos/productos.csv"
                )
                
                sftp_timeout = st.slider("Timeout (segundos):", min_value=5, max_value=60, value=30)
                
                col1, col2 = st.columns(2)
                with col1:
                    test_sftp = st.form_submit_button("🔧 Probar Conexión SFTP")
                    save_sftp_config = st.form_submit_button("💾 Guardar Configuración")
                with col2:
                    download_sftp = st.form_submit_button("🔄 Descargar desde SFTP", type="primary")
                
                if test_sftp:
                    if all([sftp_host, sftp_user, sftp_password]):
                        with st.spinner("Probando conexión SFTP..."):
                            success, message = test_sftp_connection(sftp_host, sftp_user, sftp_password, sftp_port, sftp_timeout)
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
                    else:
                        st.error("❌ Complete todos los campos para probar la conexión SFTP")
                
                if save_sftp_config:
                    st.session_state.sftp_config = {
                        'host': sftp_host,
                        'port': sftp_port,
                        'user': sftp_user,
                        'file_path': sftp_file_path,
                        'timeout': sftp_timeout
                    }
                    if sftp_password:
                        st.session_state.sftp_password = sftp_password
                    st.success("✅ Configuración SFTP guardada")
                    st.rerun()
                
                if download_sftp:
                    if all([sftp_host, sftp_user, sftp_password, sftp_file_path]):
                        with st.spinner("Descargando desde SFTP..."):
                            success, result = download_from_sftp(sftp_host, sftp_user, sftp_password, sftp_file_path, sftp_port, sftp_timeout)
                            
                            if success:
                                # Mostrar información de depuración
                                st.info(f"📄 Archivo descargado ({len(result)} caracteres)")
                                
                                # Mostrar una muestra del contenido
                                with st.expander("🔍 Vista previa del archivo descargado"):
                                    preview = result[:500] + "..." if len(result) > 500 else result
                                    st.text(preview)
                                
                                is_valid, csv_result = validate_csv_content(result)
                                if is_valid:
                                    st.success("✅ Archivo descargado desde SFTP correctamente")
                                    st.info(f"📊 Se encontraron {len(csv_result)} productos")
                                    
                                    # Guardar el resultado temporalmente para uso fuera del formulario
                                    st.session_state['sftp_download_result'] = csv_result
                                    st.session_state['sftp_download_ready'] = True
                                else:
                                    st.error(f"❌ Error en el archivo descargado: {csv_result}")
                                    # Mostrar información adicional para debug
                                    st.info("💡 Verifique que el archivo tenga las columnas: Codigo, Descripcion, Familia, Stock")
                            else:
                                st.error(f"❌ {result}")
                    else:
                        st.error("❌ Complete todos los campos para descargar desde SFTP")
            
            # Botón para actualizar base de datos fuera del formulario
            if st.session_state.get('sftp_download_ready', False):
                if st.button("💾 Actualizar Base de Datos", type="primary", key="sftp_update_outside"):
                    csv_result = st.session_state.get('sftp_download_result')
                    if csv_result is not None:
                        if save_data(csv_result):
                            st.success("🎉 ¡Datos actualizados desde SFTP exitosamente!")
                            # Limpiar el estado temporal
                            st.session_state['sftp_download_ready'] = False
                            st.session_state.pop('sftp_download_result', None)
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar los datos")
            
            with st.expander("💡 Información sobre SFTP"):
                st.markdown("""
                **SFTP vs FTP:**
                - **SFTP**: Protocolo seguro que usa SSH (puerto 22)
                - **FTP**: Protocolo tradicional no seguro (puerto 21)
                
                **Configuración típica SFTP:**
                - Puerto: 22 (estándar SSH)
                - Ruta: `/home/usuario/archivo.csv` o `/var/www/data/productos.csv`
                - Autenticación: Usuario y contraseña SSH
                
                **Ventajas de SFTP:**
                - ✅ Conexión encriptada y segura
                - ✅ Compatible con servidores Linux/Unix
                - ✅ Mismo puerto que SSH (22)
                """)
        
        with tab4:
            st.markdown("**Descarga desde URL directa:**")
            st.info("💡 Alternativa más simple al FTP. Use una URL directa al archivo CSV (HTTP/HTTPS)")
            
            with st.form("url_form"):
                csv_url = st.text_input(
                    "URL del archivo CSV:",
                    placeholder="https://ejemplo.com/datos/productos.csv",
                    help="URL directa que apunte al archivo CSV"
                )
                
                url_timeout = st.slider(
                    "Timeout de descarga (segundos):",
                    min_value=5,
                    max_value=120,
                    value=30
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    test_url = st.form_submit_button("🔗 Probar URL")
                with col2:
                    download_url = st.form_submit_button("📥 Descargar desde URL", type="primary")
                
                if test_url:
                    if csv_url:
                        with st.spinner("Probando URL..."):
                            success, result = download_from_url(csv_url, timeout=10)
                            if success:
                                # Verificar que sea CSV válido
                                is_valid, csv_result = validate_csv_content(result)
                                if is_valid:
                                    st.success(f"✅ URL válida. Se encontraron {len(csv_result)} productos")
                                else:
                                    st.error(f"❌ El archivo no es un CSV válido: {csv_result}")
                            else:
                                st.error(f"❌ {result}")
                    else:
                        st.error("❌ Ingrese una URL válida")
                
                if download_url:
                    if csv_url:
                        with st.spinner("Descargando desde URL..."):
                            success, result = download_from_url(csv_url, url_timeout)
                            if success:
                                is_valid, csv_result = validate_csv_content(result)
                                if is_valid:
                                    st.success("✅ Archivo descargado y validado correctamente")
                                    st.info(f"📊 Se encontraron {len(csv_result)} productos")
                                    
                                    if st.button("💾 Actualizar Base de Datos", type="primary", key="url_update"):
                                        if save_data(csv_result):
                                            st.success("🎉 ¡Datos actualizados desde URL exitosamente!")
                                            st.rerun()
                                else:
                                    st.error(f"❌ Error en el archivo descargado: {csv_result}")
                            else:
                                st.error(f"❌ {result}")
                    else:
                        st.error("❌ Ingrese una URL válida")
            
            # Ejemplos de URLs
            with st.expander("💡 Ejemplos de URLs válidas"):
                st.markdown("""
                **Tipos de URLs compatibles:**
                - `https://ejemplo.com/datos/productos.csv`
                - `http://ftp.ejemplo.com/public/stock.csv`
                - `https://drive.google.com/uc?export=download&id=FILE_ID` (Google Drive)
                - `https://github.com/usuario/repo/raw/main/data.csv` (GitHub)
                
                **Ventajas de usar URL directa:**
                - ✅ Más simple que configurar FTP
                - ✅ Funciona con servidores web estándar
                - ✅ Compatible con servicios en la nube
                - ✅ No requiere credenciales especiales
                """)
        
        st.markdown("---")
        
        # Información del sistema
        st.subheader("ℹ️ Información")
        df = load_data()
        st.metric("Total de Productos", len(df))
        
        if not df.empty:
            stock_bajo = len(df[pd.to_numeric(df['Stock'], errors='coerce') <= 5])
            st.metric("🔴 Stock Bajo (≤5)", stock_bajo)
    
    # Cargar datos
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ No hay datos disponibles. Cargue un archivo CSV para comenzar.")
        return
    
    # Barra de búsqueda
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Buscar productos:",
            placeholder="Buscar por código, descripción, familia o stock...",
            help="La búsqueda es en tiempo real y busca en todos los campos"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Espaciado
        clear_search = st.button("🗑️ Limpiar", help="Limpiar búsqueda")
        if clear_search:
            st.rerun()
    
    # Filtrar datos
    filtered_df = filter_dataframe(df, search_term)
    
    # Mostrar resultados
    if filtered_df.empty:
        st.warning("🔍 No se encontraron productos que coincidan con la búsqueda.")
    else:
        # Información de resultados
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Productos Encontrados", len(filtered_df))
        with col2:
            if search_term:
                st.metric("📋 Total en Base", len(df))
        with col3:
            # Botón de exportar
            csv_export = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Exportar Resultados",
                data=csv_export,
                file_name=f"stock_productos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Descargar resultados en formato CSV"
            )
        
        st.markdown("---")
        
        # Preparar datos para mostrar con indicadores de stock
        display_df = filtered_df.copy()
        display_df['Indicador'] = display_df['Stock'].apply(get_stock_color)
        
        # Reordenar columnas
        display_df = display_df[['Indicador', 'Codigo', 'Descripcion', 'Familia', 'Stock']]
        
        # Configurar la tabla
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Indicador": st.column_config.TextColumn(
                    "Estado",
                    help="🟢 Stock Alto | 🟡 Stock Medio | 🔴 Stock Bajo",
                    width="small"
                ),
                "Codigo": st.column_config.TextColumn(
                    "Código",
                    width="medium"
                ),
                "Descripcion": st.column_config.TextColumn(
                    "Descripción",
                    width="large"
                ),
                "Familia": st.column_config.TextColumn(
                    "Familia",
                    width="medium"
                ),
                "Stock": st.column_config.NumberColumn(
                    "Stock",
                    width="small",
                    format="%d"
                )
            }
        )
        
        # Leyenda de colores
        st.markdown("---")
        st.markdown("""
        **Leyenda de Stock:**
        - 🟢 **Stock Alto:** Más de 20 unidades
        - 🟡 **Stock Medio:** Entre 6 y 20 unidades  
        - 🔴 **Stock Bajo:** 5 unidades o menos
        """)

def initialize_auto_scheduler():
    """Inicializar el programador automático al cargar la aplicación"""
    # Solo si tenemos configuración SFTP válida y está habilitado
    if (st.session_state.get('auto_ftp_enabled', False) and 
        'sftp_config' in st.session_state and
        st.session_state.sftp_config.get('host') == 'home567855122.1and1-data.host'):
        
        # Limpiar programaciones anteriores
        schedule.clear()
        # Programar para las 2:00 AM
        schedule.every().day.at("02:00").do(auto_update_from_ftp)
        # Establecer contraseña para SFTP
        st.session_state.sftp_password = "@Q&jb@kpcU(OhpQv95bN0%eI"

if __name__ == "__main__":
    # Inicializar el programador automático
    initialize_auto_scheduler()
    main()
