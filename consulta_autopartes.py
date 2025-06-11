import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Consulta de Inventario - Autopartes", page_icon="🔎", layout="wide")
st.title("🔎 Consulta de Inventario - Autopartes")

# Función para cargar y limpiar los datos
@st.cache_data
def load_data():
    df = pd.read_excel('INVENTARIO FINAL AUTOPARTES Phyton.xlsx')

    # Limpiar y formatear columnas
    df['Marca'] = df['Marca'].astype(str).str.strip().str.upper()
    df['Categoria'] = df['Categoria'].astype(str).str.strip().str.title()
    df['Descripción'] = df['Descripción'].astype(str).str.strip()

    # Eliminar la columna "Precio Original"
    if 'Precio Original' in df.columns:
        df.drop(columns=['Precio Original'], inplace=True)

    return df

df = load_data()

# Inicializar sesión para limpiar filtros
if "reset" not in st.session_state:
    st.session_state.reset = False

# Botón para limpiar filtros
if st.button("🔄 Limpiar filtros"):
    st.session_state.reset = True

# UI de filtros
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

# Limpiar estado después de aplicar filtros
if st.session_state.reset:
    st.session_state.reset = False

# Aplicar filtros
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

# Mostrar resultados
st.markdown(f"**Resultados filtrados: {len(filtered_df)}**")
if filtered_df.empty:
    st.warning("No se encontraron resultados para los filtros seleccionados.")
else:
    st.dataframe(filtered_df)

    # Exportar como CSV
    csv_data = filtered_df.to_csv(index=False)
    st.download_button("💾 Exportar resultados filtrados", data=csv_data, file_name="resultados_filtrados.csv", mime="text/csv")
