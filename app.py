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

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Consulta de Stock",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
PASSWORD = "stock2025"
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

def main():
    """Función principal de la aplicación"""
    if not check_password():
        return
    
    # Título principal
    st.title("📦 Sistema de Consulta de Stock")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        user_type = st.session_state.get("user_type", "admin")
        if user_type == "admin":
            st.header("🔧 Administración")
        else:
            st.header("👁️ Consulta")
        
        if st.button("🚪 Cerrar Sesión", type="secondary"):
            st.session_state.password_correct = False
            st.rerun()
        
        st.markdown("---")
        
        # Configuración de rangos de stock para administradores
        if user_type == "admin":
            st.subheader("⚙️ Configuración de Stock")
            
            if 'stock_high_threshold' not in st.session_state:
                st.session_state.stock_high_threshold = 20
            if 'stock_low_threshold' not in st.session_state:
                st.session_state.stock_low_threshold = 5
            
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
                    st.success(f"✅ Configuración guardada")
                    st.rerun()
                
                st.info(f"📊 Actual: 🔴≤{st.session_state.stock_low_threshold} | 🟡{st.session_state.stock_low_threshold+1}-{st.session_state.stock_high_threshold} | 🟢>{st.session_state.stock_high_threshold}")
            
            st.markdown("---")
            st.subheader("📂 Actualizar Datos")
            
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
        st.subheader("ℹ️ Información")
        df = load_data()
        st.metric("Total de Productos", len(df))
        
        if not df.empty:
            low_threshold = st.session_state.get('stock_low_threshold', 5)
            stock_bajo = len(df[pd.to_numeric(df['Stock'], errors='coerce') <= low_threshold])
            st.metric(f"🔴 Stock Bajo (≤{low_threshold})", stock_bajo)
    
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
    main()