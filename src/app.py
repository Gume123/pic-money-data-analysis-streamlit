import sys
import os

sys.path.append(os.path.abspath("charts"))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from charts import cfo_charts
from charts import ceo_charts
import streamlit as st
import pandas as pd
import re


# =========================
# FORMATAÇÃO DE NÚMEROS
# =========================
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_inteiro(valor):
    return f"{valor:,}".replace(",", ".")


def formatar_decimal(valor):
    return f"{valor:.1f}".replace(".", ",")


# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_ceo_data():
    try:
        df_ceo = pd.read_csv("data/Analise-CEO.csv", sep=";")
        df_teste_em_massa = pd.read_csv(
            "data/teste_em_massa-limpo.csv", sep=",", engine="python")

        def limpar_coord(valor):
            valor = str(valor)
            valor = re.sub(r"[^0-9\.-]", "", valor)
            valor = valor.replace(".", "")
            if not valor.startswith("-"):
                valor = "-" + valor
            if len(valor) > 3:
                valor = valor[:3] + "." + valor[3:]
            try:
                return float(valor)
            except:
                return None

        if "latitude" in df_ceo.columns and "longitude" in df_ceo.columns:
            df_ceo["latitude"] = df_ceo["latitude"].apply(limpar_coord)
            df_ceo["longitude"] = df_ceo["longitude"].apply(limpar_coord)

        return df_ceo, df_teste_em_massa
    except Exception as e:
        st.error(f"Erro CEO: {e}")
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data
def load_cfo_data():
    try:
        df_cfo = pd.read_csv('data/Analise-CFO.csv', sep=';', decimal=',')
        df_dem = pd.read_csv(
            'data/cupons_capturados-limpo.csv', sep=',', decimal='.')

        if 'valor_compra' in df_cfo.columns:
            df_cfo['valor_compra'] = df_cfo['valor_compra'].astype(str)\
                .str.replace('.', '', regex=False)\
                .str.replace(',', '.', regex=False).astype(float)

        if 'valor_cupom' in df_cfo.columns:
            df_cfo['valor_cupom'] = df_cfo['valor_cupom'].astype(str)\
                .str.replace('.', '', regex=False)\
                .str.replace(',', '.', regex=False).astype(float)

        if 'data_captura' in df_cfo.columns:
            df_cfo['data_captura'] = pd.to_datetime(
                df_cfo['data_captura'], format='%d/%m/%Y', errors='coerce')
            df_cfo = df_cfo.dropna(subset=['data_captura'])

        if 'numero_celular' in df_cfo.columns:
            df_cfo['numero_celular'] = df_cfo['numero_celular'].astype(
                str).str.replace(r'[() -]', '', regex=True)

        if 'celular' in df_dem.columns:
            df_dem = df_dem.rename(columns={'celular': 'numero_celular'})

        if 'numero_celular' in df_dem.columns:
            df_dem['numero_celular'] = df_dem['numero_celular'].astype(
                str).str.replace(r'[() -]', '', regex=True)

        df = pd.merge(df_cfo, df_dem, on='numero_celular', how='left')
        df['valor_liquido'] = df['valor_compra'] - df['valor_cupom']

        return df
    except Exception as e:
        st.error(f"Erro CFO: {e}")
        return pd.DataFrame()


# =========================
# LOAD
# =========================
df_ceo, df_teste_em_massa = load_ceo_data()
df_cfo = load_cfo_data()

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="PicStats", layout="wide")

st.title("Visão Geral Executiva")


# =========================
# KPIs
# =========================
if not df_cfo.empty:
    total_liquido = df_cfo['valor_liquido'].sum()
    total_desconto = df_cfo['valor_cupom'].sum()
    ticket_medio = df_cfo['valor_compra'].mean()
    num_cupons = df_cfo.shape[0]

    idade_media = df_ceo['idade'].mean() if not df_ceo.empty else 0

    st.subheader("Resumo Geral")

    # linha 1
    col1, col2 = st.columns(2)
    col1.metric("Receita Líquida", formatar_moeda(total_liquido))
    col2.metric("Desconto", formatar_moeda(total_desconto))

    # linha 2
    col3, col4 = st.columns(2)
    col3.metric("Ticket Médio", formatar_moeda(ticket_medio))
    col4.metric("Cupons", formatar_inteiro(num_cupons))

    # linha 3
    col5, col6 = st.columns(2)
    col5.metric("Idade Média", f"{formatar_decimal(idade_media)} anos")
    col6.empty()  # mantém alinhamento

    st.markdown("---")


# =========================
# CEO
# =========================
st.header("Visão do CEO")

if not df_ceo.empty:

    st.subheader("1. Distribuição de Usuários por Idade")
    st.plotly_chart(
        ceo_charts.grafico_usuarios_por_idade(df_ceo),
        use_container_width=True
    )

    st.subheader("2. Mapa de Clusters de Usuários")
    st.plotly_chart(
        ceo_charts.grafico_mapa_clusters(df_ceo),
        use_container_width=True
    )

    st.subheader("3. Categorias de Lojas")
    if not df_teste_em_massa.empty:
        st.plotly_chart(
            ceo_charts.grafico_categorias_frequentes(df_teste_em_massa),
            use_container_width=True
        )

else:
    st.warning("Dados do CEO indisponíveis.")


st.markdown("---")


# =========================
# CFO
# =========================
st.header("Visão do CFO")

if not df_cfo.empty:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Receita Líquida")
        st.plotly_chart(
            cfo_charts.plot_time_series(df_cfo, 'valor_liquido', ''),
            use_container_width=True
        )

    with c2:
        st.subheader("Ticket Médio")
        st.plotly_chart(
            cfo_charts.plot_average_time_series(df_cfo, 'valor_compra', ''),
            use_container_width=True
        )

    with c3:
        st.subheader("Desconto")
        st.plotly_chart(
            cfo_charts.plot_time_series(df_cfo, 'valor_cupom', ''),
            use_container_width=True
        )

else:
    st.warning("Dados do CFO indisponíveis.")