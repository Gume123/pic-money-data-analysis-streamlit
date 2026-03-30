import streamlit as st
import pandas as pd
import sys
import os
import numpy as np

# Adiciona a pasta charts ao path para importar os gráficos
# A estrutura de pastas deve ser:
# cfo_dashboard/
# ├── app.py
# ├── Analise-CFO.csv
# ├── cupons_capturados-limpo.csv
# └── charts/
#     └── cfo_charts.py
sys.path.append(os.path.abspath("charts"))
from charts import cfo_charts

# Configuração inicial
st.set_page_config(layout="wide", page_title="Dashboard Financeiro de Cupons - CFO")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, 'data', 'Analise-CFO.csv')

# --- Funções de Carregamento e Pré-processamento de Dados ---

@st.cache_data
def load_data():
    """Carrega e pré-processa os dados de análise CFO."""
    try:
        df = pd.read_csv("/src/data/Analise-CFO.csv", sep=";", decimal=',')
        
        # Tratamento de colunas numéricas (removendo pontos como separador de milhar e convertendo para float)
        if 'valor_compra' in df.columns:
            df['valor_compra'] = df['valor_compra'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        if 'valor_cupom' in df.columns:
            df['valor_cupom'] = df['valor_cupom'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        
        # Tratamento de datas
        if 'data_captura' in df.columns:
            df['data_captura'] = pd.to_datetime(df['data_captura'], format='%d/%m/%Y', errors='coerce')
            df = df.dropna(subset=['data_captura'])
            df['mes_ano'] = df['data_captura'].dt.to_period('M')
            df['dia_semana'] = df['data_captura'].dt.day_name(locale='pt_BR')
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar ou processar o arquivo {file_path}: {e}")
        return pd.DataFrame()

@st.cache_data
def load_demographic_data(file_path, sep=','):
    """Carrega e pré-processa os dados demográficos."""
    try:
        df = pd.read_csv("/src/data/Analise-CFO.csv", sep=sep, decimal='.')
        
        # Tratamento de colunas
        if 'celular' in df.columns:
            df = df.rename(columns={'celular': 'numero_celular'})
        
        # Garantir que a coluna de celular esteja no mesmo formato para merge
        if 'numero_celular' in df.columns:
            df['numero_celular'] = df['numero_celular'].astype(str).str.replace(r'[() -]', '', regex=True)
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar ou processar o arquivo {file_path}: {e}")
        return pd.DataFrame()

# --- Carregamento e Combinação de Dados ---

df_cfo = load_data('data/Analise-CFO.csv', sep=';')
df_dem = load_demographic_data('data/cupons_capturados-limpo.csv', sep=',')

# Padronizar a coluna de celular em df_cfo para o merge
if 'numero_celular' in df_cfo.columns:
    df_cfo['numero_celular'] = df_cfo['numero_celular'].astype(str).str.replace(r'[() -]', '', regex=True)

# Merge dos DataFrames
if not df_cfo.empty and not df_dem.empty:
    df_merged = pd.merge(df_cfo, df_dem, on='numero_celular', how='left')
else:
    st.error("Não foi possível carregar os dados. Verifique se os arquivos CSV estão no diretório correto.")
    st.stop()

# --- Cálculo de Métricas Financeiras Chave ---

df_merged['valor_liquido'] = df_merged['valor_compra'] - df_merged['valor_cupom']
df_merged['margem_cupom'] = (df_merged['valor_cupom'] / df_merged['valor_compra']) * 100
df_merged['margem_cupom'] = df_merged['margem_cupom'].apply(lambda x: x if x <= 100 else 100) # Limitar a 100%

# --- Layout do Dashboard ---

st.title("💰 Dashboard Financeiro de Cupons - CFO")
st.markdown("Análise do impacto financeiro e demográfico das campanhas de cupons de desconto.")

# --- Sidebar para Filtros ---
st.sidebar.header("Filtros de Análise")

# Filtro de Data
min_date = df_merged['data_captura'].min().date()
max_date = df_merged['data_captura'].max().date()
date_range = st.sidebar.date_input("Selecione o Período", 
                                   value=(min_date, max_date),
                                   min_value=min_date,
                                   max_value=max_date)

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    df_filtered = df_merged[(df_merged['data_captura'] >= start_date) & (df_merged['data_captura'] <= end_date)]
else:
    df_filtered = df_merged.copy()

# Filtro de Tipo de Cupom
tipos_cupom = ['Todos'] + list(df_filtered['tipo_cupom'].unique())
selected_cupom = st.sidebar.multiselect("Tipo de Cupom", tipos_cupom, default=['Todos'])
if 'Todos' not in selected_cupom:
    df_filtered = df_filtered[df_filtered['tipo_cupom'].isin(selected_cupom)]

# Filtro de Tipo de Loja
tipos_loja = ['Todas'] + list(df_filtered['tipo_loja'].unique())
selected_loja = st.sidebar.multiselect("Tipo de Loja", tipos_loja, default=['Todas'])
if 'Todas' not in selected_loja:
    df_filtered = df_filtered[df_filtered['tipo_loja'].isin(selected_loja)]

# Criação das abas
tabs = st.tabs([
    "📈 KPIs e Análise Temporal",
    "📊 Análise de Segmento",
])

# === ABA 1: KPIs e Análise Temporal ===
with tabs[0]:
    st.subheader("Indicadores Chave de Performance (KPIs)")

    col1, col2, col3, col4 = st.columns(4)

    # Cálculo de KPIs
    total_compras = df_filtered['valor_compra'].sum()
    total_desconto = df_filtered['valor_cupom'].sum()
    total_liquido = df_filtered['valor_liquido'].sum()
    num_cupons = df_filtered.shape[0]

    # Delta (Comparação com o período anterior - simplificado)
    mid_date = df_merged['data_captura'].max() - (df_merged['data_captura'].max() - df_merged['data_captura'].min()) / 2
    df_prev = df_merged[df_merged['data_captura'] < mid_date]
    df_curr = df_merged[df_merged['data_captura'] >= mid_date]

    total_liquido_prev = df_prev['valor_liquido'].sum()
    delta_liquido = ((total_liquido - total_liquido_prev) / total_liquido_prev) * 100 if total_liquido_prev != 0 else 0

    with col1:
        cfo_charts.create_kpi_card("Valor Total de Compras (GMV)", total_compras, help_text="Soma do valor de todas as compras antes do desconto.")

    with col2:
        cfo_charts.create_kpi_card("Valor Total de Desconto Concedido", total_desconto, help_text="Soma do valor de todos os cupões utilizados.")

    with col3:
        cfo_charts.create_kpi_card("Valor Líquido (Receita)", total_liquido, delta=delta_liquido, help_text="Valor total das compras após a aplicação dos cupões.")

    with col4:
        st.metric(label="Total de Cupões Utilizados", value=f"{num_cupons:,}".replace(",", "X").replace(".", ",").replace("X", "."), help="Número total de transações com cupões no período.")

    # --- KPIs Adicionais ---
    st.subheader("KPIs Adicionais")

    col_add1, col_add2, col_add3, col_add4 = st.columns(4)

    # Ticket Médio (ATV)
    ticket_medio = df_filtered['valor_compra'].mean()
    # Desconto Médio
    desconto_medio = df_filtered['valor_cupom'].mean()
    # Margem Média de Cupóm
    margem_media = df_filtered['margem_cupom'].mean()
    # Taxa de Utilização Diária
    num_dias = (df_filtered['data_captura'].max() - df_filtered['data_captura'].min()).days + 1
    taxa_diaria = num_cupons / num_dias if num_dias > 0 else 0

    with col_add1:
        cfo_charts.create_kpi_card("Ticket Médio (ATV)", ticket_medio, help_text="Valor médio de compra por cupóm utilizado.")

    with col_add2:
        cfo_charts.create_kpi_card("Desconto Médio", desconto_medio, help_text="Valor médio de desconto concedido por cupóm.")

    with col_add3:
        st.metric(label="Margem Média de Cupóm", value=f"{margem_media:.2f}%", help="Percentual médio de desconto em relação ao valor da compra.")

    with col_add4:
        st.metric(label="Taxa de Utilização Diária", value=f"{taxa_diaria:.2f}", help="Média de cupões utilizados por dia.")

    # --- Análise Temporal Principal ---
    st.header("Análise Temporal - Receita e Desconto")

    col5, col6 = st.columns(2)

    with col5:
        st.plotly_chart(cfo_charts.plot_time_series(df_filtered, 'valor_liquido', 'Receita Líquida ao Longo do Tempo'), use_container_width=True)

    with col6:
        st.plotly_chart(cfo_charts.plot_time_series(df_filtered, 'valor_cupom', 'Desconto Concedido ao Longo do Tempo'), use_container_width=True)

    # --- Análise de Médias Temporais ---
    st.header("Análise Temporal - Médias")

    col7, col8 = st.columns(2)

    with col7:
        st.plotly_chart(cfo_charts.plot_average_time_series(df_filtered, 'valor_compra', 'Ticket Médio (ATV) ao Longo do Tempo'), use_container_width=True)

    with col8:
        st.plotly_chart(cfo_charts.plot_average_time_series(df_filtered, 'valor_cupom', 'Desconto Médio ao Longo do Tempo'), use_container_width=True)

    # --- Análise por Dia da Semana ---
    st.header("Análise por Dia da Semana")

    col9, col10 = st.columns(2)

    with col9:
        st.plotly_chart(cfo_charts.plot_day_of_week_analysis(df_filtered, 'valor_liquido', 'Receita Líquida por Dia da Semana'), use_container_width=True)

    with col10:
        st.plotly_chart(cfo_charts.plot_day_of_week_analysis(df_filtered, 'valor_cupom', 'Desconto Concedido por Dia da Semana'), use_container_width=True)

    # --- Análise de Tipo de Cupóm ao Longo do Tempo ---
    st.header("Análise Temporal por Tipo de Cupóm")

    col11, col12 = st.columns(2)

    with col11:
        st.plotly_chart(cfo_charts.plot_stacked_area_time_series(df_filtered, 'valor_liquido', 'Receita Líquida ao Longo do Tempo por Tipo de Cupóm'), use_container_width=True)

    with col12:
        st.plotly_chart(cfo_charts.plot_stacked_area_time_series(df_filtered, 'valor_cupom', 'Desconto Concedido ao Longo do Tempo por Tipo de Cupóm'), use_container_width=True)

# === ABA 2: Análise de Segmento ===
with tabs[1]:
    st.subheader("📊 Análise Profunda de Segmento")

    # --- Receita e Desconto por Tipo de Loja ---
    col7, col8 = st.columns(2)

    with col7:
        st.plotly_chart(cfo_charts.plot_bar_chart(df_filtered, 'tipo_loja', 'valor_liquido', 'Top 10 Tipos de Loja por Receita Líquida'), use_container_width=True)

    with col8:
        st.plotly_chart(cfo_charts.plot_pie_chart(df_filtered, 'tipo_cupom', 'valor_cupom', 'Distribuição do Desconto por Tipo de Cupom'), use_container_width=True)

    # --- Margem de Lucro por Tipo de Loja ---
    st.subheader("Margem de Cupom por Tipo de Loja")
    st.plotly_chart(cfo_charts.plot_segment_metric(df_filtered, 'tipo_loja', 'margem_cupom', 'Margem de Cupom (%) por Tipo de Loja'), use_container_width=True)
    st.markdown("_Quanto maior a margem, maior o custo do cupom em relação ao valor da compra._")

    # --- Ticket Médio por Tipo de Loja ---
    st.subheader("Ticket Médio por Tipo de Loja")
    st.plotly_chart(cfo_charts.plot_segment_metric(df_filtered, 'tipo_loja', 'valor_compra', 'Ticket Médio (R$) por Tipo de Loja', sort_ascending=False), use_container_width=True)
    st.markdown("_Identifica quais tipos de loja têm maior poder de compra._")

    # --- ROI por Tipo de Loja ---
    st.subheader("Retorno sobre Investimento (ROI) por Tipo de Loja")
    st.plotly_chart(cfo_charts.plot_segment_roi(df_filtered), use_container_width=True)
    st.markdown("_ROI = Receita Líquida / Desconto Concedido. Quanto maior, melhor o retorno por R$ gasto em cupons._")

    # --- Análise de Concentração (Pareto) ---
    st.subheader("Análise de Concentração (Pareto) da Receita Líquida")
    st.plotly_chart(cfo_charts.plot_concentration_analysis(df_filtered), use_container_width=True)
    st.markdown("_A linha vermelha mostra qual % da receita é gerada pelos primeiros tipos de loja. Identifica lojas estratégicas vs. periféricas._")

    # --- Série Temporal por Segmento ---
    st.subheader("Evolução Temporal da Receita Líquida (Top 5 Tipos de Loja)")
    st.plotly_chart(cfo_charts.plot_segment_time_series(df_filtered, 'tipo_loja', 'valor_liquido', 'Receita Líquida ao Longo do Tempo por Tipo de Loja'), use_container_width=True)
    st.markdown("_Mostra tendências e sazonalidade por segmento._")

    # --- Heatmap de Tipo de Loja vs. Tipo de Cupom ---
    st.subheader("Matriz de Interação: Tipo de Loja vs. Tipo de Cupom")
    st.plotly_chart(cfo_charts.plot_coupon_type_heatmap(df_filtered), use_container_width=True)
    st.markdown("_Heatmap mostrando a receita líquida gerada pela combinação de cada tipo de loja com cada tipo de cupom._")

    # --- Scatter Plot: Ticket Médio vs. Desconto Médio ---
    st.subheader("Ticket Médio vs. Desconto Médio por Tipo de Loja")
    st.plotly_chart(cfo_charts.plot_ticket_discount_scatter(df_filtered), use_container_width=True)
    st.markdown("_Scatter plot mostrando a relação entre ticket médio e desconto médio. O tamanho da bolha representa o volume de cupons._")



    # Métrica de Engajamento (Cupons por Usuário)
    df_user_summary = df_filtered.groupby('numero_celular').agg(
        total_compras=('valor_compra', 'sum'),
        total_desconto=('valor_cupom', 'sum'),
        total_liquido=('valor_liquido', 'sum'),
        num_cupons=('numero_celular', 'count'),
        idade=('idade', 'first'),
        sexo=('sexo', 'first'),
        cidade_residencial=('cidade_residencial', 'first')
    ).reset_index()

    # LTV Simplificado (Valor Líquido Médio por Usuário)
    ltv_simplificado = df_user_summary['total_liquido'].mean()

    col9, col10 = st.columns(2)

    with col9:
        cfo_charts.create_kpi_card("LTV Simplificado (Ticket Médio Líquido por Usuário)", 
                                   ltv_simplificado,
                                   help_text="Média do valor líquido total gasto por usuário no período.")

    with col10:
        cupons_por_usuario = df_user_summary['num_cupons'].mean()
        st.metric(label="Cupons Médios por Usuário", 
                  value=f"{cupons_por_usuario:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                  help="Média de cupons utilizados por usuário no período.")

    st.subheader("Distribuição de Usuários por Idade e Sexo")
    st.plotly_chart(cfo_charts.plot_age_gender_distribution(df_user_summary), use_container_width=True)

    st.subheader("Top 10 Categorias Frequentadas")
    st.plotly_chart(cfo_charts.plot_top_categories(df_filtered), use_container_width=True)

# --- Tabela de Dados (Opcional) ---
if st.checkbox("Mostrar Tabela de Dados Brutos"):
    st.subheader("Dados Brutos (Filtrados)")
    st.dataframe(df_filtered)

# --- Instruções para Execução ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Instruções de Execução:**
1. Crie a pasta `charts` e coloque o arquivo `cfo_charts.py` dentro dela.
2. Coloque este arquivo (`app.py`) e os arquivos CSV (`Analise-CFO.csv` e `cupons_capturados-limpo.csv`) no diretório principal.
3. Instale as bibliotecas: `pip install streamlit pandas numpy plotly`
4. Execute no terminal: `streamlit run app.py`
""")
