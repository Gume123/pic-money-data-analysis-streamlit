# 📊 PicMoney Analytics Platform

**Dashboards Estratégicos para Gestão de Cupons e Parcerias**

## 🚀 Visão Geral

A PicMoney Analytics evoluiu para uma plataforma de BI (Business Intelligence) ágil, permitindo que executivos visualizem indicadores críticos em tempo real. Utilizando **Streamlit**, a plataforma consolida dados financeiros e de comportamento do usuário para fornecer insights imediatos às frentes de **CEO**, **CFO** e **Gestão de Parcerias**.

## 🛠️ Stack Tecnológica

- **Linguagem:** Python 3.11+
- **Interface/Dashboard:** Streamlit
- **Processamento de Dados:** Pandas & NumPy
- **Visualização:** Plotly Express & Graph Objects
- **Geolocalização:** Mapbox (Density Heatmaps)

## 📂 Estrutura do Projeto

O ecossistema de dashboards está segmentado por domínios de decisão:

```text
picmoney-analytics/
├── app.py                  # Ponto de entrada (Dashboard Unificado)
├── 1_CEO.py                # Visão Estratégica e Engajamento
├── 2_CFO.py                # Métricas Financeiras e LTV
├── 3_PARCERIAS.py          # Gestão de Lojas e Performance de Cupons
├── data/                   # Bases de dados (CSV)
│   ├── analise-ceo.csv
│   ├── analise-cfo.csv
│   └── cupons_capturados-limpo.csv
└── charts/                 # Módulos de lógica visual (Encapsulamento)
    ├── ceo_charts.py       # Gráficos de idade, calor e comportamento
    ├── cfo_charts.py       # Séries temporais e KPIs financeiros
    └── parcerias_charts.py # Rankings de lojas e margens
```

## 🏁 Como Começar

### Pré-requisitos
- Python 3.11 ou superior installed.

### Instalação e Execução

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/picmoney-analytics.git
   cd picmoney-analytics
   ```

2. **Instalar dependências:**
   ```bash
   pip install streamlit pandas plotly numpy
   ```

3. **Executar a plataforma:**
   ```bash
   # Para abrir o dashboard principal unificado
   streamlit run app.py
   ```

## 📈 Inteligência de Dados (KPIs por Visão)

### 👑 Visão CEO (Estratégico)
* **Distribuição Demográfica:** Análise de faixa etária dos usuários ativos.
* **Mapa de Calor:** Identificação geográfica de capturas via Mapbox.
* **Comportamento:** Relação entre o tipo de cupom e a categoria de loja preferida.
* **Engajamento:** Valor capturado por idade e tipo de oferta.

### 💰 Visão CFO (Financeiro)
* **Séries Temporais:** Evolução da Receita Líquida e Ticket Médio (ATV).
* **Eficiência de Cupons:** Relação entre valor do cupom e valor da compra.
* **LTV Simplificado:** Ticket médio líquido por usuário único.
* **Análise Semanal:** Distribuição de transações por dia da semana.

### 🤝 Visão Parcerias (Operacional)
* **Performance por Loja:** Ranking de faturamento e número de transações.
* **Análise de Margem:** Monitoramento da margem percentual por categoria.
* **Detalhamento:** Tabela dinâmica com registros individuais de transações por parceiro.

## ⚙️ Configurações de Dados

O projeto utiliza processamento em memória com cache otimizado (`@st.cache_data`) para garantir fluidez na navegação entre abas. Os dados são carregados a partir de arquivos CSV na pasta `data/`, com tratamento automático para:
* Limpeza de coordenadas geográficas.
* Conversão de formatos monetários brasileiros (BRL).
* Normalização de colunas de data e hora.

## 📌 Próximos Passos
- [ ] Integração direta com Snowflake ou Google BigQuery.
- [ ] Implementação de modelos preditivos para *Churn* de usuários.
- [ ] Exportação automática de relatórios em PDF.

---
**Equipe PicMoney Analytics** 📧 [contato@picmoney.com](mailto:contato@picmoney.com)