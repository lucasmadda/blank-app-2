import streamlit as st
import requests
from datetime import datetime, timedelta

def obter_taxas_selic(data_inicial, data_final):
    """
    Obtém as taxas Selic diárias entre as datas especificadas.
    """
    url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados'
    params = {
        'formato': 'json',
        'dataInicial': data_inicial.strftime('%d/%m/%Y'),
        'dataFinal': data_final.strftime('%d/%m/%Y')
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        dados = response.json()
        taxas = {datetime.strptime(item['data'], '%d/%m/%Y'): float(item['valor'].replace(',', '.')) for item in dados}
        return taxas
    else:
        st.error("Erro ao acessar a API do Banco Central.")
        return None

def corrigir_valor_simples(valor_inicial, data_inicial, data_final):
    """
    Corrige o valor monetário aplicando as taxas Selic diárias de forma simples.
    """
    taxas = obter_taxas_selic(data_inicial, data_final)
    if not taxas:
        return None

    total_juros = 0.0
    data_atual = data_inicial

    while data_atual <= data_final:
        if data_atual in taxas:
            taxa_diaria = taxas[data_atual] / 100
            juros_diarios = valor_inicial * taxa_diaria
            total_juros += juros_diarios
        data_atual += timedelta(days=1)

    valor_corrigido = valor_inicial + total_juros
    return valor_corrigido

def corrigir_valor_composto(valor_inicial, data_inicial, data_final):
    """
    Corrige o valor monetário aplicando as taxas Selic diárias de forma composta.
    """
    taxas = obter_taxas_selic(data_inicial, data_final)
    if not taxas:
        return None

    valor_corrigido = valor_inicial
    data_atual = data_inicial

    while data_atual <= data_final:
        if data_atual in taxas:
            taxa_diaria = taxas[data_atual] / 100
            valor_corrigido *= (1 + taxa_diaria)
        data_atual += timedelta(days=1)

    return valor_corrigido

# Interface do Streamlit
st.title("Calculadora de Correção Monetária com Taxa Selic")
st.write("Este aplicativo calcula a correção monetária de um valor utilizando a taxa Selic diária, permitindo escolher entre juros simples ou compostos.")

valor_inicial = st.number_input("Digite o valor a ser corrigido:", min_value=0.0, format="%.2f")
data_inicial = st.date_input("Selecione a data inicial:",
                             value=datetime.today().date()-timedelta(days=365),
                             format="DD/MM/YYYY")

data_final = st.date_input("Selecione a data final:",
                           value="today",
                           format="DD/MM/YYYY")

tipo_juros = st.radio("Selecione o tipo de juros:", ('Simples', 'Compostos'))

if st.button("Calcular"):
    if data_final < data_inicial:
        st.error("A data final deve ser posterior à data inicial.")
    else:
        data_inicial_dt = datetime.combine(data_inicial, datetime.min.time())
        data_final_dt = datetime.combine(data_final, datetime.min.time())

        if tipo_juros == 'Simples':
            valor_corrigido = corrigir_valor_simples(valor_inicial, data_inicial_dt, data_final_dt)
        else:
            valor_corrigido = corrigir_valor_composto(valor_inicial, data_inicial_dt, data_final_dt)

        if valor_corrigido:
            st.success(f"Valor corrigido: R$ {valor_corrigido:.2f}")
        else:
            st.error("Não foi possível calcular o valor corrigido.")
