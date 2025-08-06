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

# Configuración optimizada para Railway
st.set_page_config(
    page_title="Distribuciones Lucero - Sistema de Stock",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar si estamos en Railway
IS_RAILWAY = os.environ.get("RAILWAY_ENVIRONMENT") is not None
PORT = int(os.environ.get("PORT", 8501))

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
    
    /* Métricas */
    .metric-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--lucero-blue);
    }
</style>
""", unsafe_allow_html=True)

# Constantes adaptadas para Railway
PASSWORD = os.environ.get("ADMIN_PASSWORD", "stock2025")
VIEWER_PASSWORD = os.environ.get("VIEWER_PASSWORD", "lucero")
CSV_FILE_PATH = "data/productos.csv"
CONFIG_FILE_PATH = "data/config.json"

def check_password():
    """Función para verificar la contraseña de acceso"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        st.title("🔐 Acceso al Sistema de Stock")
        
        # Mostrar información sobre Railway si aplicable
        if IS_RAILWAY:
            st.info("🚀 Aplicación ejecutándose en Railway")
        
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
            elif password == VIEWER_PASSWORD:
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
    """Determinar el color del indicador de stock"""
    try:
        stock_val = pd.to_numeric(stock, errors='coerce')
        if pd.isna(stock_val):
            return "⚪"
        
        low_threshold = st.session_state.get('stock_low_threshold', 5)
        high_threshold = st.session_state.get('stock_high_threshold', 20)
        
        if stock_val <= low_threshold:
            return "🔴"
        elif stock_val <= high_threshold:
            return "🟡"
        else:
            return "🟢"
    except:
        return "⚪"

def filter_dataframe(df, search_term):
    """Filtrar DataFrame basado en el término de búsqueda"""
    if not search_term:
        return df
    
    search_term = search_term.lower()
    mask = (
        df['Codigo'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Descripcion'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Familia'].astype(str).str.lower().str.contains(search_term, na=False) |
        df['Stock'].astype(str).str.lower().str.contains(search_term, na=False)
    )
    return df[mask]

def main():
    """Función principal de la aplicación"""
    if not check_password():
        return
    
    # Header corporativo
    st.markdown("""
    <div class="main-header">
        <h1>📦 Distribuciones Lucero</h1>
        <div class="subtitle">Sistema de Gestión de Stock</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar información de Railway en el sidebar
    with st.sidebar:
        st.markdown("### 🏢 Sistema de Stock")
        user_type = st.session_state.get('user_type', 'viewer')
        st.success(f"👤 Usuario: **{user_type.title()}**")
        
        if IS_RAILWAY:
            st.info(f"🚀 Railway - Puerto {PORT}")
        
        if st.button("🚪 Cerrar Sesión", key="logout"):
            st.session_state.password_correct = False
            st.session_state.user_type = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Resumen de Inventario")
        df = load_data()
        
        if not df.empty:
            low_threshold = st.session_state.get('stock_low_threshold', 5)
            high_threshold = st.session_state.get('stock_high_threshold', 20)
            
            # Calcular stocks por categorías de forma segura
            try:
                stock_numbers = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
                stock_bajo = len(df[stock_numbers <= low_threshold])
                stock_medio = len(df[(stock_numbers > low_threshold) & (stock_numbers <= high_threshold)])
                stock_alto = len(df[stock_numbers > high_threshold])
                
                st.metric("📦 Total", len(df))
                st.metric("🔴 Stock Bajo", stock_bajo)
                st.metric("🟡 Stock Medio", stock_medio) 
                st.metric("🟢 Stock Alto", stock_alto)
            except Exception as e:
                st.error(f"Error calculando métricas: {str(e)}")
    
    # Contenido principal
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ No hay datos disponibles. Cargue un archivo CSV para comenzar.")
        
        # Mostrar datos de ejemplo para Railway
        if IS_RAILWAY:
            st.info("🚀 Para Railway: Puede crear datos de prueba usando la función de administrador")
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
        
        # Preparar datos para mostrar de forma segura
        try:
            display_df = filtered_df.copy()
            display_df['Indicador'] = filtered_df['Stock'].apply(get_stock_color)
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
        except Exception as e:
            st.error(f"Error mostrando datos: {str(e)}")
            st.dataframe(filtered_df, use_container_width=True)
        
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