import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Inventario de Autopartes", page_icon="📦", layout="wide")
st.markdown("### 📦 Inventario de Autopartes")

# Mostrar logo y WhatsApp
col_logo, col_info = st.columns([1, 4])
with col_logo:
    st.image("logo.png", width=120)
with col_info:
    st.markdown("""
        ### Autopartes Villa Insurgentes  
        📍 León, Guanajuato  
        📞 WhatsApp: [477 247 9133](https://wa.me/524772479133)
    """)

# Ruta del archivo
ARCHIVO_EXCEL = "INVENTARIO FINAL AUTOPARTES Phyton.xlsx"
CONTRASEÑA = "moy<<250403"

@st.cache_data
def load_data():
    df = pd.read_excel(ARCHIVO_EXCEL)
    df['Marca'] = df['Marca'].astype(str).str.strip().str.upper()
    df['Categoria'] = df['Categoria'].astype(str).str.strip().str.title()
    df['Descripción'] = df['Descripción'].astype(str).str.strip()

    if 'Precio Original' in df.columns:
        df.drop(columns=['Precio Original'], inplace=True)
    if 'Estado' in df.columns:
        df = df[df['Estado'].str.upper() != 'VENDIDO']
    return df

df = load_data()

if "reset" not in st.session_state:
    st.session_state.reset = False

if st.button("🔄 Limpiar filtros"):
    st.session_state.reset = True

col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

with col1:
    search_term = st.text_input("Buscar (Código o Descripción)", value="" if st.session_state.reset else "")

with col2:
    categorias = ["Selecciona una categoría"] + sorted(df['Categoria'].unique())
    selected_category = st.selectbox("Categoría", categorias, index=0 if st.session_state.reset else 0)

with col3:
    if selected_category != "Selecciona una categoría":
        marcas_filtradas = sorted(df[df['Categoria'] == selected_category]['Marca'].unique())
        selected_brand = st.selectbox("Marca", ["Todas"] + marcas_filtradas, index=0 if st.session_state.reset else 0)
    else:
        selected_brand = None

with col4:
    min_price = float(df['Precio Outlet'].min())
    max_price = float(df['Precio Outlet'].max())
    price_min, price_max = st.slider(
        "Precio (rango)",
        min_value=int(min_price),
        max_value=int(max_price),
        value=(int(min_price), int(max_price)) if st.session_state.reset else (int(min_price), int(max_price)),
        step=1
    )

if st.session_state.reset:
    st.session_state.reset = False

filtered_df = df.copy()
if search_term:
    mask = filtered_df['Código'].astype(str).str.contains(search_term, case=False, na=False) | \
           filtered_df['Descripción'].astype(str).str.contains(search_term, case=False, na=False)
    filtered_df = filtered_df[mask]

if selected_category != "Selecciona una categoría":
    filtered_df = filtered_df[filtered_df['Categoria'] == selected_category]
    if selected_brand and selected_brand != "Todas":
        filtered_df = filtered_df[filtered_df['Marca'] == selected_brand]

filtered_df = filtered_df[
    (filtered_df['Precio Outlet'] >= price_min) & 
    (filtered_df['Precio Outlet'] <= price_max)
]

st.markdown(f"**Resultados filtrados: {len(filtered_df)}**")
if filtered_df.empty:
    st.warning("No se encontraron resultados para los filtros seleccionados.")
else:
    st.dataframe(filtered_df)
    csv_data = filtered_df.to_csv(index=False)
    st.download_button("💾 Exportar resultados filtrados", data=csv_data, file_name="resultados_filtrados.csv", mime="text/csv")

# --- NUEVO: Marcar producto como vendido ---
st.markdown("---")
st.markdown("## 🛠️ Marcar producto como vendido")

codigo_a_vender = st.text_input("Código del producto")
password_input = st.text_input("Contraseña", type="password")

if st.button("✅ Marcar como VENDIDO"):
    if password_input == CONTRASEÑA:
        df_full = pd.read_excel(ARCHIVO_EXCEL)

        if codigo_a_vender in df_full['Código'].astype(str).values:
            df_full.loc[df_full['Código'].astype(str) == codigo_a_vender, 'Estado'] = 'VENDIDO'
            df_full.to_excel(ARCHIVO_EXCEL, index=False)
            st.success(f"✅ El producto con código {codigo_a_vender} fue marcado como VENDIDO.")
            st.info("🔁 Vuelve a cargar la app para ver los cambios reflejados.")
        else:
            st.error("❌ El código ingresado no existe en el archivo.")
    else:
        st.error("❌ Contraseña incorrecta.")
