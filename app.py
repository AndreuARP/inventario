import streamlit as st
import pandas as pd
import os
from io import StringIO
import csv
import ftplib
from datetime import datetime
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

def download_from_ftp(ftp_host, ftp_user, ftp_password, ftp_file_path, ftp_port=21):
    """Descargar archivo CSV desde servidor FTP"""
    try:
        # Conectar al servidor FTP
        ftp = ftplib.FTP()
        ftp.connect(ftp_host, ftp_port)
        ftp.login(ftp_user, ftp_password)
        
        # Descargar el archivo
        csv_content = []
        ftp.retrlines(f'RETR {ftp_file_path}', csv_content.append)
        
        # Cerrar conexión
        ftp.quit()
        
        # Unir las líneas del archivo
        csv_string = '\n'.join(csv_content)
        
        return True, csv_string
        
    except ftplib.all_errors as e:
        return False, f"Error de FTP: {str(e)}"
    except Exception as e:
        return False, f"Error general: {str(e)}"

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
        tab1, tab2 = st.tabs(["📁 Archivo Local", "🌐 Servidor FTP"])
        
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
            
            # Inicializar configuración FTP en session state
            if 'ftp_config' not in st.session_state:
                st.session_state.ftp_config = {
                    'host': '',
                    'port': 21,
                    'user': '',
                    'file_path': ''
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
                ftp_password = st.text_input("Contraseña:", type="password")
                ftp_file_path = st.text_input(
                    "Ruta del archivo:", 
                    value=st.session_state.ftp_config['file_path'],
                    placeholder="/data/productos.csv"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    save_config = st.form_submit_button("💾 Guardar Configuración")
                with col2:
                    download_ftp = st.form_submit_button("🔄 Descargar desde FTP", type="primary")
                
                if save_config:
                    st.session_state.ftp_config = {
                        'host': ftp_host,
                        'port': ftp_port,
                        'user': ftp_user,
                        'file_path': ftp_file_path
                    }
                    st.success("✅ Configuración FTP guardada")
                    st.rerun()
                
                if download_ftp:
                    if all([ftp_host, ftp_user, ftp_password, ftp_file_path]):
                        # Guardar configuración automáticamente al descargar
                        st.session_state.ftp_config = {
                            'host': ftp_host,
                            'port': ftp_port,
                            'user': ftp_user,
                            'file_path': ftp_file_path
                        }
                        
                        with st.spinner("Conectando al servidor FTP..."):
                            success, result = download_from_ftp(ftp_host, ftp_user, ftp_password, ftp_file_path, ftp_port)
                            
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
            
            # Mostrar información de última actualización
            if os.path.exists(CSV_FILE_PATH):
                mod_time = os.path.getmtime(CSV_FILE_PATH)
                last_update = datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M:%S")
                st.info(f"📅 Última actualización: {last_update}")
        
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

if __name__ == "__main__":
    main()
