import streamlit as st
import pandas as pd
import os
import ftplib
import paramiko
import socket
import threading
import time
import schedule
from io import StringIO
import requests
from datetime import datetime
import json

# Configuración de la página
st.set_page_config(
    page_title="Distribuciones Lucero - Sistema de Stock",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con colores corporativos de Distribuciones Lucero
st.markdown("""
<style>
    /* Colores corporativos Distribuciones Lucero */
    :root {
        --lucero-blue: #1f4e79;
        --lucero-green: #7cb518;
        --lucero-red: #e31e24;
        --lucero-light-blue: #4a90b8;
    }
    
    /* Header personalizado */
    .main-header {
        background: linear-gradient(90deg, var(--lucero-blue) 0%, var(--lucero-light-blue) 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header .subtitle {
        color: #f0f0f0;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Botones principales */
    .stButton > button[kind="primary"] {
        background-color: var(--lucero-green);
        border-color: var(--lucero-green);
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #6a9c15;
        border-color: #6a9c15;
    }
    
    /* Botones secundarios */
    .stButton > button[kind="secondary"] {
        background-color: var(--lucero-red);
        border-color: var(--lucero-red);
        color: white;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #c21a1f;
        border-color: #c21a1f;
    }
    
    /* Métricas */
    .metric-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--lucero-blue);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Expandibles */
    .streamlit-expanderHeader {
        background-color: var(--lucero-blue);
        color: white;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: rgba(124, 181, 24, 0.1);
        border-color: var(--lucero-green);
    }
    
    /* Error messages */
    .stError {
        background-color: rgba(227, 30, 36, 0.1);
        border-color: var(--lucero-red);
    }
    
    /* Indicadores de stock */
    .stock-indicator {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .logo-container img {
        max-height: 80px;
        margin-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Constantes
PASSWORD = "stock2025"
CSV_FILE_PATH = "data/productos.csv"
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(CSV_FILE_PATH):
    st.info("Descargando archivo de stock desde SFTP...")

    # Sustituye esto con tus valores reales
    SFTP_HOST = "home567855122.1and1-data.host"
    SFTP_USER = "acc1195143440"
    SFTP_PASS = "@Q&jb@kpcU(OhpQv95bN0%eI"
    SFTP_PATH = "/stock/stock.csv"

    success, content, msg = download_from_sftp(
        sftp_host=SFTP_HOST,
        sftp_user=SFTP_USER,
        sftp_password=SFTP_PASS,
        sftp_file_path=SFTP_PATH
    )

    if success:
        with open(CSV_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        st.success("Archivo descargado correctamente.")
    else:
        st.error(f"No se pudo descargar el archivo: {msg}")
CONFIG_FILE_PATH = "data/config.json"


def check_password():
    """Función para verificar la contraseña de acceso"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        # Logo y título de acceso
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if os.path.exists("assets/logo.gif"):
                st.image("assets/logo.gif", width=300)
            st.markdown('<div class="main-header"><h1>🔐 Acceso al Sistema</h1><div class="subtitle">Sistema de Consulta de Stock</div></div>', unsafe_allow_html=True)
        
        password = st.text_input(
            "Ingrese la contraseña para acceder:",
            type="password",
            placeholder="Contraseña requerida"
        )
        
        if st.button("Ingresar", type="primary"):
            if password == PASSWORD:
                st.session_state.password_correct = True
                st.session_state.user_type = "admin"
                st.success("✅ Acceso concedido como administrador. Redirigiendo...")
                st.rerun()
            elif password == "lucero":
                st.session_state.password_correct = True
                st.session_state.user_type = "viewer"
                st.success("✅ Acceso concedido como consulta. Redirigiendo...")
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
            required_columns = ['Codigo', 'Descripcion', 'Familia', 'Stock']
            if all(col in df.columns for col in required_columns):
                return df
            else:
                st.error(f"❌ El archivo CSV debe contener las columnas: {', '.join(required_columns)}")
                return pd.DataFrame(columns=required_columns)
        else:
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

def load_config():
    """Cargar configuración desde archivo JSON"""
    default_config = {
        'stock_high_threshold': 20,
        'stock_low_threshold': 5,
        'sftp_config': {
            'enabled': False,
            'host': 'home567855122.1and1-data.host',
            'port': 22,
            'user': 'acc1195143440',
            'password': '@Q&jb@kpcU(OhpQv95bN0%eI',
            'file_path': '/stock/stock.csv'
        },
        'last_update': None
    }
    
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_config.items():
                    if key not in saved_config:
                        saved_config[key] = value
                    elif key == 'sftp_config' and isinstance(value, dict):
                        for sftp_key, sftp_value in value.items():
                            if sftp_key not in saved_config[key]:
                                saved_config[key][sftp_key] = sftp_value
                return saved_config
        else:
            return default_config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return default_config

def save_config(config):
    """Guardar configuración en archivo JSON"""
    try:
        os.makedirs("data", exist_ok=True)
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        return False

def initialize_session_config():
    """Inicializar configuración en session state desde archivo"""
    if 'config_initialized' not in st.session_state:
        st.session_state.config_initialized = True
        config = load_config()
        
        # Cargar configuraciones en session state
        st.session_state.stock_high_threshold = config['stock_high_threshold']
        st.session_state.stock_low_threshold = config['stock_low_threshold']
        st.session_state.sftp_config = config['sftp_config']
        if config['last_update']:
            st.session_state.last_update = config['last_update']

def get_stock_color(stock):
    """Obtener color para el indicador de stock"""
    try:
        stock_num = float(stock)
        high_threshold = st.session_state.get('stock_high_threshold', 20)
        low_threshold = st.session_state.get('stock_low_threshold', 5)
        
        if stock_num <= low_threshold:
            return "🔴"
        elif stock_num <= high_threshold:
            return "🟡"
        else:
            return "🟢"
    except:
        return "⚪"

def filter_dataframe(df, search_term):
    """Filtrar DataFrame por término de búsqueda"""
    if not search_term:
        return df
    
    search_term = search_term.lower()
    mask = (
        df['Codigo'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Descripcion'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Familia'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Stock'].astype(str).str.contains(search_term, na=False)
    )
    return df[mask]

def validate_csv_content(content):
    """Validar el contenido del archivo CSV"""
    try:
        df = pd.read_csv(StringIO(content))
        required_columns = ['Codigo', 'Descripcion', 'Familia', 'Stock']
        if not all(col in df.columns for col in required_columns):
            return False, f"El archivo debe contener las columnas: {', '.join(required_columns)}"
        
        if len(df) == 0:
            return False, "El archivo está vacío"
        
        return True, df
        
    except Exception as e:
        return False, f"Error al procesar el archivo: {str(e)}"

def download_from_sftp(sftp_host, sftp_user, sftp_password, sftp_file_path, sftp_port=22, timeout=30):
    """Descargar archivo CSV desde servidor SFTP"""
    try:
        # Configurar el cliente SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conectar al servidor SFTP
        ssh.connect(
            hostname=sftp_host,
            port=sftp_port,
            username=sftp_user,
            password=sftp_password,
            timeout=timeout
        )
        
        # Abrir SFTP
        sftp = ssh.open_sftp()
        
        # Leer el archivo remoto
        with sftp.open(sftp_file_path, 'r') as remote_file:
            content = remote_file.read().decode('utf-8')
        
        # Cerrar conexiones
        sftp.close()
        ssh.close()
        
        return True, content, "Archivo descargado exitosamente via SFTP"
        
    except paramiko.AuthenticationException:
        return False, None, "Error de autenticación SFTP - Verifique usuario y contraseña"
    except paramiko.SSHException as e:
        return False, None, f"Error de conexión SSH: {str(e)}"
    except FileNotFoundError:
        return False, None, f"Archivo no encontrado en el servidor: {sftp_file_path}"
    except socket.timeout:
        return False, None, f"Timeout de conexión ({timeout}s) - Servidor no responde"
    except Exception as e:
        return False, None, f"Error SFTP: {str(e)}"

def test_sftp_connection(sftp_host, sftp_user, sftp_password, sftp_port=22, timeout=10):
    """Probar la conectividad SFTP"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=sftp_host,
            port=sftp_port,
            username=sftp_user,
            password=sftp_password,
            timeout=timeout
        )
        
        sftp = ssh.open_sftp()
        sftp.close()
        ssh.close()
        
        return True, "Conexión SFTP exitosa"
        
    except Exception as e:
        return False, f"Error en conexión SFTP: {str(e)}"

def log_message(message):
    """Escribir mensaje de log con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/scheduler.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(log_entry.strip())
    except Exception as e:
        print(f"Error writing log: {e}")

def auto_update_from_sftp():
    """Función para actualización automática desde SFTP"""
    try:
        log_message("🔄 Iniciando actualización automática SFTP...")
        
        config = load_config()
        if not config['sftp_config'].get('enabled', False):
            log_message("⚠️ Actualizaciones automáticas deshabilitadas")
            return
        
        sftp_config = config['sftp_config']
        log_message(f"📡 Conectando a {sftp_config['host']}...")
        
        success, content, message = download_from_sftp(
            sftp_config['host'],
            sftp_config['user'],
            sftp_config['password'],
            sftp_config['file_path'],
            sftp_config.get('port', 22)
        )
        
        if success:
            log_message("✅ Archivo descargado exitosamente")
            is_valid, result = validate_csv_content(content)
            if is_valid:
                save_data(result)
                # Actualizar y guardar la fecha de última actualización
                config['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_config(config)
                log_message(f"🎉 Actualización automática exitosa: {config['last_update']}")
                log_message(f"📊 Productos actualizados: {len(result)}")
            else:
                log_message(f"❌ Error en validación CSV: {result}")
        else:
            log_message(f"❌ Error en descarga SFTP: {message}")
            
    except Exception as e:
        log_message(f"💥 Error crítico en actualización automática: {str(e)}")

def schedule_worker():
    """Worker que ejecuta las tareas programadas"""
    log_message("🚀 Scheduler worker iniciado - próxima ejecución: 02:00 AM")
    
    # Crear archivo de estado para tracking
    status_file = "data/scheduler_status.json"
    
    while True:
        try:
            current_time = datetime.now()
            
            # Actualizar archivo de estado cada minuto
            status_data = {
                "last_check": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "worker_active": True,
                "next_run": schedule.next_run().strftime("%Y-%m-%d %H:%M:%S") if schedule.next_run() else None
            }
            
            try:
                with open(status_file, "w", encoding="utf-8") as f:
                    json.dump(status_data, f, indent=2)
            except:
                pass  # No fallar si no se puede escribir el estado
            
            # Ejecutar tareas pendientes
            schedule.run_pending()
            
            # Log del estado cada 6 horas para verificar que está funcionando
            if current_time.hour in [0, 6, 12, 18] and current_time.minute == 0:
                log_message(f"⏰ Scheduler activo a las {current_time.strftime('%H:%M')} - próxima ejecución: {schedule.next_run()}")
            
            # Si estamos cerca de las 2:00 AM, hacer log más frecuente
            if current_time.hour == 1 and current_time.minute >= 55:
                log_message(f"🕐 Preparándose para actualización automática en {60 - current_time.minute} minutos")
            
            time.sleep(60)  # Revisar cada minuto
            
        except Exception as e:
            log_message(f"💥 Error en scheduler worker: {str(e)}")
            time.sleep(300)  # Esperar 5 minutos antes de reintentar

def check_missed_updates():
    """Verificar si se perdieron actualizaciones y ejecutarlas si es necesario"""
    try:
        config = load_config()
        last_update_str = config.get('last_update', '')
        now = datetime.now()
        
        if last_update_str:
            last_update = datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S")
            
            # Si la última actualización fue hace más de 20 horas, probablemente se perdió una
            hours_since_last = (now - last_update).total_seconds() / 3600
            
            if hours_since_last > 20:  # Más de 20 horas
                log_message(f"🔍 Última actualización hace {hours_since_last:.1f} horas. Ejecutando actualización de recuperación...")
                auto_update_from_sftp()
                return True
        else:
            # Si no hay registro de última actualización, ejecutar una
            log_message("🔍 No hay registro de actualizaciones previas. Ejecutando primera actualización...")
            auto_update_from_sftp()
            return True
                        
        return False
    except Exception as e:
        log_message(f"💥 Error verificando actualizaciones perdidas: {str(e)}")
        return False

def initialize_auto_scheduler():
    """Inicializar el programador automático al cargar la aplicación"""
    # Usar un enfoque más robusto sin depender de session_state
    try:
        # Primero verificar si hay actualizaciones perdidas
        check_missed_updates()
        
        # Limpiar trabajos anteriores
        schedule.clear()
        
        # Configurar actualización a las 2:00 AM
        schedule.every().day.at("02:00").do(auto_update_from_sftp)
        
        # Log para confirmar configuración
        log_message("⚙️ Scheduler configurado para actualizaciones a las 02:00 AM")
        
        # Verificar si ya hay un worker ejecutándose
        active_threads = [t for t in threading.enumerate() if t.name.startswith('scheduler_worker')]
        
        if not active_threads:
            # Iniciar worker en hilo separado con nombre específico
            worker_thread = threading.Thread(
                target=schedule_worker, 
                daemon=True,
                name='scheduler_worker_main'
            )
            worker_thread.start()
            log_message("✅ Worker de scheduler iniciado correctamente")
        else:
            log_message("ℹ️ Worker de scheduler ya está ejecutándose")
            
    except Exception as e:
        log_message(f"💥 Error inicializando scheduler: {str(e)}")

def get_scheduler_status():
    """Obtener estado del scheduler y próxima ejecución"""
    try:
        status_info = []
        
        # Información básica del scheduler
        next_run = schedule.next_run()
        if next_run:
            status_info.append(f"Próxima ejecución: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            status_info.append("Sin tareas programadas")
        
        # Verificar archivo de estado del worker
        status_file = "data/scheduler_status.json"
        if os.path.exists(status_file):
            try:
                with open(status_file, "r", encoding="utf-8") as f:
                    worker_status = json.load(f)
                
                last_check = datetime.strptime(worker_status["last_check"], "%Y-%m-%d %H:%M:%S")
                minutes_ago = (datetime.now() - last_check).total_seconds() / 60
                
                if minutes_ago < 5:
                    status_info.append(f"Worker activo (último check hace {int(minutes_ago)} min)")
                else:
                    status_info.append(f"⚠️ Worker inactivo (último check hace {int(minutes_ago)} min)")
                    
            except:
                status_info.append("Estado del worker desconocido")
        else:
            status_info.append("Archivo de estado no encontrado")
        
        # Verificar threads activos
        active_threads = [t for t in threading.enumerate() if 'scheduler_worker' in t.name]
        status_info.append(f"Threads del scheduler: {len(active_threads)}")
        
        return " | ".join(status_info)
        
    except Exception as e:
        return f"Error obteniendo estado: {str(e)}"

def get_recent_logs():
    """Obtener los últimos logs del scheduler"""
    try:
        if os.path.exists("data/scheduler.log"):
            with open("data/scheduler.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Retornar las últimas 10 líneas
                return "".join(lines[-10:]) if lines else "Sin logs disponibles"
        return "Archivo de log no encontrado"
    except Exception as e:
        return f"Error leyendo logs: {str(e)}"

def main():
    """Función principal de la aplicación"""
    if not check_password():
        return
    
    # Inicializar configuración persistente
    initialize_session_config()
    
    # Header principal con logo corporativo
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("assets/logo.gif"):
            st.image("assets/logo.gif", width=180)
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1>📦 Sistema de Consulta de Stock</h1>
            <div class="subtitle">Distribuciones Lucero - Gestión de Inventario</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Logo en sidebar
        if os.path.exists("assets/logo.gif"):
            st.image("assets/logo.gif", width=200)
        
        user_type = st.session_state.get("user_type", "admin")
        if user_type == "admin":
            st.markdown("### 🔧 Panel de Administración")
            st.markdown("**Distribuciones Lucero**")
        else:
            st.markdown("### 👁️ Panel de Consulta")
            st.markdown("**Distribuciones Lucero**")
        
        if st.button("🚪 Cerrar Sesión", type="secondary"):
            st.session_state.password_correct = False
            st.rerun()
        
        st.markdown("---")
        
        # Configuración para administradores
        if user_type == "admin":
            
            with st.expander("🎯 Configurar Rangos de Stock"):
                col1, col2 = st.columns(2)
                
                with col1:
                    low_threshold = st.number_input(
                        "Stock Bajo (≤):",
                        min_value=0,
                        max_value=100,
                        value=st.session_state.stock_low_threshold,
                        help="Stock igual o menor se marca en rojo"
                    )
                
                with col2:
                    high_threshold = st.number_input(
                        "Stock Alto (>):",
                        min_value=low_threshold + 1,
                        max_value=200,
                        value=st.session_state.stock_high_threshold,
                        help="Stock mayor se marca en verde"
                    )
                
                if st.button("💾 Guardar Configuración", key="save_stock_config"):
                    st.session_state.stock_low_threshold = low_threshold
                    st.session_state.stock_high_threshold = high_threshold
                    
                    # Guardar en archivo persistente
                    config = load_config()
                    config['stock_low_threshold'] = low_threshold
                    config['stock_high_threshold'] = high_threshold
                    save_config(config)
                    
                    st.success(f"✅ Configuración guardada permanentemente")
                    st.rerun()
                
                st.info(f"📊 Actual: 🔴≤{st.session_state.stock_low_threshold} | 🟡{st.session_state.stock_low_threshold+1}-{st.session_state.stock_high_threshold} | 🟢>{st.session_state.stock_high_threshold}")
            
            with st.expander("🌐 Configuración SFTP"):
                st.markdown("**Configurar servidor SFTP para actualizaciones automáticas**")
                
                col1, col2 = st.columns(2)
                with col1:
                    sftp_host = st.text_input("🖥️ Servidor SFTP:", value=st.session_state.sftp_config['host'])
                    sftp_user = st.text_input("👤 Usuario:", value=st.session_state.sftp_config['user'])
                    sftp_port = st.number_input("🔌 Puerto:", min_value=1, max_value=65535, value=st.session_state.sftp_config['port'])
                
                with col2:
                    sftp_password = st.text_input("🔑 Contraseña:", value=st.session_state.sftp_config['password'], type="password")
                    sftp_file_path = st.text_input("📁 Ruta del archivo:", value=st.session_state.sftp_config['file_path'])
                    sftp_enabled = st.checkbox("✅ Habilitar actualizaciones automáticas", value=st.session_state.sftp_config['enabled'])
                
                col_test, col_save = st.columns(2)
                
                with col_test:
                    if st.button("🔍 Probar Conexión", key="test_sftp"):
                        with st.spinner("Probando conexión SFTP..."):
                            success, message = test_sftp_connection(sftp_host, sftp_user, sftp_password, sftp_port)
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
                
                with col_save:
                    if st.button("💾 Guardar Config. SFTP", key="save_sftp_config"):
                        new_sftp_config = {
                            'enabled': sftp_enabled,
                            'host': sftp_host,
                            'port': sftp_port,
                            'user': sftp_user,
                            'password': sftp_password,
                            'file_path': sftp_file_path
                        }
                        st.session_state.sftp_config = new_sftp_config
                        
                        # Guardar en archivo persistente
                        config = load_config()
                        config['sftp_config'] = new_sftp_config
                        save_config(config)
                        
                        st.success("✅ Configuración SFTP guardada permanentemente")
                        st.rerun()
                
                if st.button("🔄 Actualizar Ahora desde SFTP", key="manual_sftp_update"):
                    with st.spinner("Descargando archivo desde SFTP..."):
                        success, content, message = download_from_sftp(sftp_host, sftp_user, sftp_password, sftp_file_path, sftp_port)
                        
                        if success:
                            is_valid, result = validate_csv_content(content)
                            if is_valid:
                                if save_data(result):
                                    # Guardar fecha de actualización persistente
                                    config = load_config()
                                    config['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    save_config(config)
                                    st.session_state.last_update = config['last_update']
                                    
                                    st.success(f"🎉 ¡Datos actualizados desde SFTP exitosamente!")
                                    st.rerun()
                                else:
                                    st.error("❌ Error al guardar los datos")
                            else:
                                st.error(f"❌ Archivo CSV inválido: {result}")
                        else:
                            st.error(f"❌ {message}")
                
                # Estado de las actualizaciones automáticas
                if st.session_state.sftp_config['enabled']:
                    st.success("🤖 Actualizaciones automáticas: HABILITADAS (2:00 AM diario)")
                    if 'last_update' in st.session_state:
                        st.info(f"📅 Última actualización: {st.session_state.last_update}")
                    
                    # Información del scheduler
                    scheduler_status = get_scheduler_status()
                    st.info(f"⏰ {scheduler_status}")
                    
                    # Botones de control
                    col_logs, col_test, col_restart = st.columns(3)
                    
                    with col_logs:
                        if st.button("📋 Ver Logs", key="view_logs"):
                            with st.expander("📝 Logs Recientes del Sistema", expanded=True):
                                logs = get_recent_logs()
                                st.text_area("Logs:", value=logs, height=200, disabled=True)
                    
                    with col_test:
                        if st.button("🧪 Probar Ahora", key="test_auto_update"):
                            with st.spinner("Ejecutando prueba..."):
                                auto_update_from_sftp()
                                st.success("Prueba completada")
                                st.rerun()
                    
                    with col_restart:
                        if st.button("🔄 Reiniciar Scheduler", key="restart_scheduler"):
                            with st.spinner("Reiniciando scheduler..."):
                                initialize_auto_scheduler()
                                st.success("Scheduler reiniciado")
                                st.rerun()
                    
                    # Advertencia si el worker parece inactivo
                    if "Worker inactivo" in scheduler_status:
                        st.warning("⚠️ El scheduler parece estar inactivo. Considera reiniciarlo.")
                else:
                    st.warning("⚠️ Actualizaciones automáticas: DESHABILITADAS")
            
            with st.expander("📂 Actualizar Datos Manualmente"):
                uploaded_file = st.file_uploader(
                    "Cargar archivo CSV:",
                    type=['csv'],
                    help="El archivo debe contener las columnas: Codigo, Descripcion, Familia, Stock"
                )
                
                if uploaded_file is not None:
                    content = uploaded_file.read().decode('utf-8')
                    is_valid, result = validate_csv_content(content)
                    
                    if is_valid:
                        st.success("✅ Archivo válido")
                        if st.button("💾 Actualizar Base de Datos", type="primary"):
                            if save_data(result):
                                st.success("🎉 ¡Datos actualizados exitosamente!")
                                st.rerun()
                    else:
                        st.error(f"❌ {result}")
        
        else:
            # Para usuarios viewer
            st.subheader("ℹ️ Información")
            st.info("👁️ Acceso de solo consulta")
            st.markdown("Puede buscar y visualizar productos, pero no puede modificar datos o configuraciones.")
            
            low_val = st.session_state.get('stock_low_threshold', 5)
            high_val = st.session_state.get('stock_high_threshold', 20)
            st.markdown("**Leyenda de Stock:**")
            st.markdown(f"🔴 Stock Bajo: ≤{low_val} unidades")
            st.markdown(f"🟡 Stock Medio: {low_val+1}-{high_val} unidades")
            st.markdown(f"🟢 Stock Alto: >{high_val} unidades")
        
        st.markdown("---")
        st.markdown("### 📊 Resumen de Inventario")
        df = load_data()
        
        # Métricas con estilo corporativo
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="color: var(--lucero-blue); margin: 0;">📦 Total de Productos</h4>
            <h2 style="color: var(--lucero-blue); margin: 0.5rem 0;">{len(df)}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if not df.empty:
            low_threshold = st.session_state.get('stock_low_threshold', 5)
            high_threshold = st.session_state.get('stock_high_threshold', 20)
            
            # Calcular stocks por categorías
            stock_numbers = pd.to_numeric(df['Stock'], errors='coerce')
            stock_bajo = len(df[stock_numbers <= low_threshold])
            stock_medio = len(df[(stock_numbers > low_threshold) & (stock_numbers <= high_threshold)])
            stock_alto = len(df[stock_numbers > high_threshold])
            
            st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div style="background-color: rgba(227, 30, 36, 0.1); padding: 0.8rem; border-radius: 5px; border-left: 4px solid var(--lucero-red); margin-bottom: 0.5rem;">
                    <strong style="color: var(--lucero-red);">🔴 Stock Bajo (≤{low_threshold}): {stock_bajo}</strong>
                </div>
                <div style="background-color: rgba(255, 193, 7, 0.1); padding: 0.8rem; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 0.5rem;">
                    <strong style="color: #d39e00;">🟡 Stock Medio ({low_threshold+1}-{high_threshold}): {stock_medio}</strong>
                </div>
                <div style="background-color: rgba(124, 181, 24, 0.1); padding: 0.8rem; border-radius: 5px; border-left: 4px solid var(--lucero-green);">
                    <strong style="color: var(--lucero-green);">🟢 Stock Alto (>{high_threshold}): {stock_alto}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Contenido principal
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
        st.markdown("<br>", unsafe_allow_html=True)
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
            csv_export = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Exportar Resultados",
                data=csv_export,
                file_name=f"stock_productos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Descargar resultados en formato CSV"
            )
        
        st.markdown("---")
        
        # Preparar datos para mostrar
        display_df = filtered_df.copy()
        display_df['Indicador'] = display_df['Stock'].apply(get_stock_color)
        display_df = display_df[['Indicador', 'Codigo', 'Descripcion', 'Familia', 'Stock']]
        
        # Mostrar tabla
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
                "Codigo": st.column_config.TextColumn("Código", width="medium"),
                "Descripcion": st.column_config.TextColumn("Descripción", width="large"),
                "Familia": st.column_config.TextColumn("Familia", width="medium"),
                "Stock": st.column_config.NumberColumn("Stock", width="small", format="%d")
            }
        )
        
        # Leyenda de colores
        st.markdown("---")
        low_val = st.session_state.get('stock_low_threshold', 5)
        high_val = st.session_state.get('stock_high_threshold', 20)
        st.markdown(f"""
        **Leyenda de Stock:**
        - 🟢 **Stock Alto:** Más de {high_val} unidades
        - 🟡 **Stock Medio:** Entre {low_val + 1} y {high_val} unidades  
        - 🔴 **Stock Bajo:** {low_val} unidades o menos
        """)

if __name__ == "__main__":
    # Inicializar el scheduler automático
    initialize_auto_scheduler()
    main()