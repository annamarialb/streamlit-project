import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px

# Funções de Gráficos

def grafico_vendas_por_vendedor(df_vendas, df_vendedores):
    resumo = df_vendas.groupby("vendedor_id")["total"].sum().reset_index()
    resumo = resumo.merge(df_vendedores, on="vendedor_id")
    resumo = resumo.sort_values(by="total", ascending=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.barh(resumo["nome"], resumo["total"])
    ax.set_xlabel("Total em R$")
    ax.set_title("Vendas por Vendedor")
    ax.invert_yaxis()
    return fig


def grafico_vendas_por_produto(df_vendas, df_produtos):
    resumo = df_vendas.groupby("produto_id")["total"].sum().reset_index()
    resumo = resumo.merge(df_produtos, on="produto_id")
    resumo = resumo.sort_values(by="total", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(resumo["nome"], resumo["total"])
    ax.set_xticklabels(resumo["nome"], rotation=45, ha='right')
    ax.set_ylabel("Total em R$")
    ax.set_title("Vendas por Produto")
    return fig


def grafico_pizza_categoria(df_vendas, df_produtos):
    resumo = df_vendas.groupby("produto_id")["total"].sum().reset_index()
    resumo = resumo.merge(df_produtos, on="produto_id")
    categorias = resumo.groupby("categoria")["total"].sum()
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(categorias, labels=categorias.index, autopct="%1.1f%%")
    ax.set_title("Distribuição das Vendas por Categoria")
    return fig


def grafico_linha_temporal(df_vendas):
    df_vendas["mes"] = df_vendas["data"].dt.to_period("M").dt.to_timestamp()
    mensal = df_vendas.groupby("mes")["total"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(mensal["mes"], mensal["total"], marker='o')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_title("Vendas Mensais")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Total em R$")
    fig.autofmt_xdate()
    return fig


def grafico_vendas_por_estado(df_vendas, df_clientes):
    resumo = df_vendas.groupby("cliente_id")["total"].sum().reset_index()
    resumo = resumo.merge(df_clientes, on="cliente_id")
    estado_total = resumo.groupby("estado")["total"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(estado_total.index, estado_total.values)
    ax.set_ylabel("Total em R$")
    ax.set_title("Vendas por Estado")
    return fig


# Carregar dados
produtos = pd.read_csv("produtos.csv")
clientes = pd.read_csv("clientes.csv")
vendedores = pd.read_csv("vendedores.csv")
fornecedores = pd.read_csv("fornecedores.csv")
vendas = pd.read_csv("vendas.csv", parse_dates=["data"])

st.set_page_config(page_title="Painel de Vendas", layout="wide")
st.title("📊 Painel Analítico de Vendas")

# Criar abas
aba = st.tabs(["📈 Vendas", "🛍️ Produtos e Clientes", "📋 Relatórios"])

# --------- ABA 1: Vendas ---------
with aba[0]:
    st.header("Resumo de Vendas")
    filtro_data = st.date_input("Filtrar por Data:", [vendas["data"].min(), vendas["data"].max()])
    if len(filtro_data) == 2:
        vendas_filtradas = vendas[(vendas["data"] >= pd.to_datetime(filtro_data[0])) & 
                                  (vendas["data"] <= pd.to_datetime(filtro_data[1]))]
    else:
        vendas_filtradas = vendas
    st.dataframe(vendas_filtradas)
    st.subheader("🔹 Vendas por Vendedor (Barras Horizontais)")
    st.pyplot(grafico_vendas_por_vendedor(vendas_filtradas, vendedores))
    st.subheader("🔹 Vendas por Produto")
    st.pyplot(grafico_vendas_por_produto(vendas_filtradas, produtos))
    st.subheader("🔹 Distribuição por Categoria de Produto")
    st.pyplot(grafico_pizza_categoria(vendas_filtradas, produtos))
    st.subheader("🔹 Evolução das Vendas ao Longo do Tempo")
    st.pyplot(grafico_linha_temporal(vendas_filtradas))
    st.subheader("🔹 Vendas por Estado do Cliente")
    st.pyplot(grafico_vendas_por_estado(vendas_filtradas, clientes))

# --------- ABA 2: Produtos e Clientes ---------
with aba[1]:
    st.header("Produtos e Clientes")
    st.subheader("📦 Produtos")
    st.dataframe(produtos)
    st.subheader("👥 Clientes")
    st.dataframe(clientes)

# --------- ABA 3: Relatórios ---------
with aba[2]:
    
    st.header("Relatórios de Vendas")
    st.subheader("🔹 Evolução Mensal das Vendas")
    st.pyplot(grafico_linha_temporal(vendas))

    st.subheader("📍 Mapa Colométrico de Vendas por Estado")
    resumo_estado = vendas.merge(clientes, on="cliente_id")
    resumo_estado = resumo_estado.groupby("estado")["total"].sum().reset_index()
    resumo_estado["estado_nome"] = resumo_estado["estado"].map({
        "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
        "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
        "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
        "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
        "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
    })
    # Carregar GeoJSON dos estados brasileiros
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    fig_mapa = px.choropleth(
        resumo_estado,
        geojson=geojson_url,
        locations="estado_nome",
        featureidkey="properties.name",
        color="total",
        color_continuous_scale="YlOrRd",
        title="Total de Vendas por Estado"
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_mapa)
