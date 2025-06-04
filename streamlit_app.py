import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Configuración general
st.set_page_config(page_title="Presupuesto Público 2015", layout="centered")
st.title("📊 Ley de Presupuestos del Sector Público - Año 2015")
st.markdown("Visualización interactiva por **Partida** y **Subtitulo** del presupuesto público.")

# Conexión con la API
url = "https://datos.gob.cl/api/3/action/datastore_search?resource_id=372b0680-d5f0-4d53-bffa-7997cf6e6512&limit=1000"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    records = data['result']['records']
    df = pd.DataFrame(records)

    # Mostrar vista previa
    st.write("### Vista previa de los primeros 10 registros:")
    st.dataframe(df.head(10), use_container_width=True)

    # Limpieza de datos
    df['Monto Pesos'] = pd.to_numeric(df['Monto Pesos'], errors='coerce')
    df = df[df['Monto Pesos'] > 0]
    df = df.dropna(subset=['Partida', 'Subtitulo'])

    # Filtro por Partida
    partidas = sorted(df['Partida'].unique())
    partida_seleccionada = st.selectbox("Selecciona una Partida:", partidas)

    # Agrupar y ordenar por Subtitulo
    df_filtrado = df[df['Partida'] == partida_seleccionada]
    resumen = df_filtrado.groupby('Subtitulo')['Monto Pesos'].sum().reset_index()
    resumen = resumen.sort_values(by='Monto Pesos', ascending=False)

    # Slider para cantidad de subtítulos
    top_n = st.slider("¿Cuántos subtítulos quieres mostrar?", 5, min(20, len(resumen)), 10)
    resumen_top = resumen.head(top_n)

    # Mostrar tabla de resumen
    st.subheader(f"Subtítulos con mayor presupuesto (Partida {partida_seleccionada})")
    st.dataframe(resumen_top, use_container_width=True)

    # Gráfico de línea
    st.subheader("Visualización del presupuesto por Subtitulo (línea)")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(resumen_top['Subtitulo'], resumen_top['Monto Pesos'], marker='o', linestyle='-', color='royalblue')
    ax.set_xlabel("Subtitulo")
    ax.set_ylabel("Monto en Pesos")
    ax.set_title(f"Top {top_n} Subtítulos - Partida {partida_seleccionada}")
    plt.xticks(rotation=45)

    # Etiquetas encima de los puntos
    for i, row in resumen_top.iterrows():
        ax.text(i, row['Monto Pesos'] + max(resumen_top['Monto Pesos']) * 0.02,
                f"{int(row['Monto Pesos']):,}", ha='center', fontsize=8)

    st.pyplot(fig)

else:
    st.error(f"Error al acceder a la API: {response.status_code}")
