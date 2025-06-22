import streamlit as st
import pandas as pd
from datetime import datetime

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
    return df

df_todo = cargar_datos_completos()
df_disponible = df_todo[df_todo['Estado'].str.upper() != 'VENDIDO']
df_vendido = df_todo[df_todo['Estado'].str.upper() == 'VENDIDO']

st.markdown("### 📊 Resumen:")
col1, col2, col3 = st.columns(3)
col1.metric("Total productos", len(df_todo))
col2.metric("Disponibles", len(df_disponible))
col3.metric("Vendidos", len(df_vendido))

tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Inventario disponible",
    "🧾 Historial de vendidos",
    "🛠️ Marcar como vendido",
    "➕ Agregar nuevo producto"
])

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

    codigo_a_vender = st.text_input("Código del producto", key="vender_codigo")
    nuevo_precio = st.number_input("Precio final de venta (Outlet)", min_value=0.0, step=10.0, key="vender_precio")
    ubicaciones = sorted(df_todo['Ubicación'].dropna().unique())
    ubicacion_seleccionada = st.selectbox("Ubicación de venta", ubicaciones, key="vender_ubicacion")
    password_input = st.text_input("Contraseña", type="password", key="vender_password")

    if st.button("✅ Confirmar venta"):
        if password_input == CONTRASEÑA:
            if codigo_a_vender in df_todo['Código'].astype(str).values:
                idx = df_todo[df_todo['Código'].astype(str) == codigo_a_vender].index[0]
                df_todo.at[idx, 'Estado'] = 'VENDIDO'
                df_todo.at[idx, 'Precio Outlet'] = nuevo_precio
                df_todo.at[idx, 'Ubicación'] = ubicacion_seleccionada
                df_todo.at[idx, 'Fecha Venta'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_todo.to_excel(ARCHIVO_EXCEL, index=False)
                st.success(f"✅ Producto {codigo_a_vender} marcado como VENDIDO.")
                st.info("🔁 Recarga la app para ver los cambios.")
            else:
                st.error("❌ El código no existe.")
        else:
            st.error("❌ Contraseña incorrecta.")

with tab4:
    st.markdown("### ➕ Agregar nuevo producto al inventario")

    col1, col2 = st.columns(2)
    with col1:
        nuevo_codigo = st.text_input("Código del producto", key="agregar_codigo")
        ubicaciones_existentes = sorted(df_todo['Ubicación'].dropna().unique())
        nueva_ubicacion = st.selectbox("Ubicación", ubicaciones_existentes + ["Otra..."], key="agregar_ubicacion_opcion")
        if nueva_ubicacion == "Otra...":
            nueva_ubicacion = st.text_input("Especifica nueva ubicación", key="agregar_ubicacion")
        nueva_descripcion = st.text_input("Descripción", key="agregar_descripcion")
        nuevo_precio_original = st.number_input("Precio Original", min_value=0.0, step=10.0, key="agregar_precio_original")
        nuevo_precio_comercial = st.number_input("Precio Comercial", min_value=0.0, step=10.0, key="agregar_precio_comercial")
    with col2:
        nuevo_precio_outlet = st.number_input("Precio Outlet", min_value=0.0, step=10.0, key="agregar_precio_outlet")
        nueva_marca = st.text_input("Marca", key="agregar_marca")
        nuevo_modelo = st.text_input("Modelo", key="agregar_modelo")
        categorias_existentes = sorted(df_todo['Categoria'].dropna().unique())
        nueva_categoria = st.selectbox("Categoría", categorias_existentes + ["Otra..."], key="agregar_categoria_opcion")
        if nueva_categoria == "Otra...":
            nueva_categoria = st.text_input("Especifica nueva categoría", key="agregar_categoria")
        nuevo_estado = st.selectbox("Estado", ["DISPONIBLE", "VENDIDO"], key="agregar_estado")

    password_nuevo = st.text_input("Contraseña para guardar", type="password", key="agregar_password")

    if st.button("📦 Guardar nuevo producto"):
        if password_nuevo == CONTRASEÑA:
            nuevo_producto = {
                "Código": nuevo_codigo,
                "Ubicación": nueva_ubicacion,
                "Descripción": nueva_descripcion,
                "Precio Original": nuevo_precio_original,
                "Precio Comercial": nuevo_precio_comercial,
                "Precio Outlet": nuevo_precio_outlet,
                "Marca": nueva_marca,
                "Modelo": nuevo_modelo,
                "Categoria": nueva_categoria,
                "Estado": nuevo_estado
            }
            df_todo = pd.concat([df_todo, pd.DataFrame([nuevo_producto])], ignore_index=True)
            df_todo.to_excel(ARCHIVO_EXCEL, index=False)
            st.success("✅ Producto agregado correctamente.")
            st.info("🔁 Recarga la app para ver los cambios.")
        else:
            st.error("❌ Contraseña incorrecta.")
