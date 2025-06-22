import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inventario de Autopartes", page_icon="📦", layout="wide")
st.markdown("### 📦 Inventario de Autopartes")

# Logo y contacto
col_logo, col_info = st.columns([1, 4])
with col_logo:
    st.image("logo.png", width=120)
with col_info:
    st.markdown("""
        ### Autopartes Villa Insurgentes  
        📍 León, Guanajuato  
        📞 WhatsApp: [477 247 9133](https://wa.me/524772479133)
    """)

ARCHIVO_EXCEL = "INVENTARIO FINAL AUTOPARTES Phyton.xlsx"
CONTRASEÑA = "moy<<250403"

def cargar_datos_completos():
    df = pd.read_excel(ARCHIVO_EXCEL)
    df['Marca'] = df['Marca'].astype(str).str.strip().str.upper()
    df['Categoria'] = df['Categoria'].astype(str).str.strip().str.title()
    df['Descripción'] = df['Descripción'].astype(str).str.strip()
    if 'Precio Original' in df.columns:
        df.drop(columns=['Precio Original'], inplace=True)
    return df

df_todo = cargar_datos_completos()
df_disponible = df_todo[df_todo['Estado'].str.upper() != 'VENDIDO']
df_vendido = df_todo[df_todo['Estado'].str.upper() == 'VENDIDO']

# Indicadores rápidos
st.markdown("### 📊 Resumen:")
col1, col2, col3 = st.columns(3)
col1.metric("Total productos", len(df_todo))
col2.metric("Disponibles", len(df_disponible))
col3.metric("Vendidos", len(df_vendido))

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📦 Inventario disponible", "🧾 Historial de vendidos", "🛠️ Marcar como vendido"])

with tab1:
