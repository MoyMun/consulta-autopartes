import streamlit as st
import pandas as pd

# Configuración de la página
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

# Cargar datos
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

# Pestañas de navegación
tab1, tab2, tab3 = st.tabs(["📦 Inventario disponible", "🧾 Historial de vendidos", "🛠️ Marcar como vendido"])

with tab1:
    if "reset" not in st.session_state:
        st.session_state.reset = False

    if st.button("🔄 Limpiar filtros"):
        st.session_state.reset = True

    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    with col1:
        search_term = st.text_input("Buscar (Código o Descripción)", value="")
    with col2:
        categorias = ["Selecciona una categoría"] + sorted(df_disponible['Categoria'].unique())
        selected_category = st.selectbox("Categoría", categorias, index=0)
    with col3:
        if selected_category != "Selecciona una categoría":
            marcas_filtradas = sorted(df_disponible[df_disponible['Categoria'] == selected_category]['Marca'].unique())
            selected_brand = st.selectbox("Marca", ["Todas"] + marcas_filtradas)
        else:
            selected_brand = None
    with col4:
        min_price = float(df_disponible['Precio Outlet'].min())
        max_price = float(df_disponible['Precio Outlet'].max())
        price_min, price_max = st.slider("Precio (rango)", int(min_price), int(max_price), (int(min_price), int(max_price)), step=1)

    filtered_df = df_disponible.copy()
    if search_term:
        mask = filtered_df['Código'].astype(str).str.contains(search_term, case=False, na=False) | \
               filtered_df['Descripción'].astype(str).str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[mask]
    if selected_category != "Selecciona una categoría":
        filtered_df = filtered_df[filtered_df['Categoria'] == selected_category]
        if selected_brand and selected_brand != "Todas":
            filtered_df = filtered_df[filtered_df['Marca'] == selected_brand]
    filtered_df = filtered_df[(filtered_df['Precio Outlet'] >= price_min) & (filtered_df['Precio Outlet'] <= price_max)]

    st.markdown(f"**Resultados filtrados: {len(filtered_df)}**")
    if filtered_df.empty:
        st.warning("No se encontraron resultados.")
    else:
        st.dataframe(filtered_df)
        st.download_button("💾 Exportar resultados filtrados", data=filtered_df.to_csv(index=False), file_name="resultados.csv", mime="text/csv")

with tab2:
    st.markdown("### 🧾 Historial de productos vendidos")
    if df_vendido.empty:
        st.info("Aún no hay productos marcados como vendidos.")
    else:
        st.dataframe(df_vendido)

with tab3:
    st.markdown("### 🛠️ Marcar producto como vendido")
    codigo_a_vender = st.text_input("Código del producto")
    password_input = st.text_input("Contraseña", type="password")
    if st.button("✅ Marcar como VENDIDO"):
        if password_input == CONTRASEÑA:
            if codigo_a_vender in df_todo['Código'].astype(str).values:
                df_todo.loc[df_todo['Código'].astype(str) == codigo_a_vender, 'Estado'] = 'VENDIDO'
                df_todo.to_excel(ARCHIVO_EXCEL, index=False)
                st.success(f"✅ Producto {codigo_a_vender} marcado como VENDIDO.")
                st.info("🔁 Vuelve a cargar la app para ver los cambios.")
            else:
                st.error("❌ El código no existe.")
        else:
            st.error("❌ Contraseña incorrecta.")
