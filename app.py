import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Diárias",
    page_icon="💰",
    layout="wide"
)

# Título principal
st.title("💰 Calculadora de Diárias de Viagem")
st.caption("Baseado no Decreto nº 6.358/2024")

# Valores da tabela conforme o decreto
VALORES_DIARIAS = {
    "Distrito Federal": {
        "alimentacao": 140.43,
        "pousada": 327.68,
        "total": 468.12
    },
    "Capitais de Estado": {
        "alimentacao": 111.38,
        "pousada": 259.88,
        "total": 371.26
    },
    "Demais Municípios": {
        "alimentacao": 87.17,
        "pousada": 203.39,
        "total": 290.55
    }
}

# Sidebar para inputs
st.sidebar.header("📋 Dados da Viagem")

# Destino
destino = st.sidebar.selectbox(
    "Destino da viagem:",
    ["Distrito Federal", "Capitais de Estado", "Demais Municípios"]
)

# Tipo de deslocamento
tipo_deslocamento = st.sidebar.selectbox(
    "Tipo de deslocamento:",
    [
        "Até 6 horas (sem diária)",
        "6 a 8 horas consecutivas (sem pernoite)",
        "Mais de 8 horas consecutivas (sem pernoite)",
        "Com pernoite (hospedagem apenas)",
        "Mais de 12 horas com pernoite (completa)",
        "Tripulante aeronave 6-10h (80% do valor)"
    ]
)

# Número de dias
num_dias = st.sidebar.number_input(
    "Número de dias de viagem:",
    min_value=1,
    max_value=365,
    value=1,
    step=1
)

# Alimentação e hospedagem gratuitas
col1, col2 = st.sidebar.columns(2)
with col1:
    alimentacao_gratuita = st.checkbox("Alimentação gratuita fornecida")
with col2:
    hospedagem_gratuita = st.checkbox("Hospedagem gratuita fornecida")

# Função para calcular a diária
def calcular_diaria(destino, tipo_deslocamento, num_dias, alimentacao_gratuita, hospedagem_gratuita):
    valores = VALORES_DIARIAS[destino]
    valor_alimentacao = valores["alimentacao"]
    valor_pousada = valores["pousada"]
    valor_total_dia = valores["total"]
    
    # Inicializar valores
    diaria_alimentacao = 0
    diaria_hospedagem = 0
    percentual_aplicado = 0
    observacoes = []
    
    # Aplicar regras conforme o tipo de deslocamento
    if tipo_deslocamento == "Até 6 horas (sem diária)":
        diaria_alimentacao = 0
        diaria_hospedagem = 0
        percentual_aplicado = 0
        observacoes.append("Deslocamento inferior a 6 horas não gera direito à diária")
        
    elif tipo_deslocamento == "6 a 8 horas consecutivas (sem pernoite)":
        if not alimentacao_gratuita:
            diaria_alimentacao = valor_alimentacao * 0.5  # 50% do valor
            percentual_aplicado = 50
            observacoes.append("50% do valor de alimentação (6-8h sem pernoite)")
        else:
            observacoes.append("Alimentação gratuita fornecida - sem diária")
            
    elif tipo_deslocamento == "Mais de 8 horas consecutivas (sem pernoite)":
        if not alimentacao_gratuita:
            diaria_alimentacao = valor_alimentacao  # 100% do valor
            percentual_aplicado = 100
            observacoes.append("100% do valor de alimentação (>8h sem pernoite)")
        else:
            observacoes.append("Alimentação gratuita fornecida - sem diária")
            
    elif tipo_deslocamento == "Com pernoite (hospedagem apenas)":
        if not hospedagem_gratuita:
            diaria_hospedagem = valor_pousada  # 100% hospedagem
            percentual_aplicado = 100
            observacoes.append("100% do valor de hospedagem (com pernoite)")
        else:
            observacoes.append("Hospedagem gratuita fornecida - sem diária")
            
    elif tipo_deslocamento == "Mais de 12 horas com pernoite (completa)":
        if not alimentacao_gratuita:
            diaria_alimentacao = valor_alimentacao
        if not hospedagem_gratuita:
            diaria_hospedagem = valor_pousada
        percentual_aplicado = 100
        observacoes.append("100% do valor total (>12h com pernoite)")
        
    elif tipo_deslocamento == "Tripulante aeronave 6-10h (80% do valor)":
        if not alimentacao_gratuita and not hospedagem_gratuita:
            diaria_total = valor_total_dia * 0.8  # 80% do total
            diaria_alimentacao = valor_alimentacao * 0.8
            diaria_hospedagem = valor_pousada * 0.8
            percentual_aplicado = 80
            observacoes.append("80% do valor total (tripulante aeronave 6-10h)")
    
    # Calcular totais
    diaria_diaria = diaria_alimentacao + diaria_hospedagem
    total_viagem = diaria_diaria * num_dias
    
    return {
        "diaria_alimentacao": diaria_alimentacao,
        "diaria_hospedagem": diaria_hospedagem,
        "diaria_total": diaria_diaria,
        "total_viagem": total_viagem,
        "percentual": percentual_aplicado,
        "observacoes": observacoes,
        "num_dias": num_dias
    }

# Calcular resultado
resultado = calcular_diaria(destino, tipo_deslocamento, num_dias, alimentacao_gratuita, hospedagem_gratuita)

# Layout principal com colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Resultado do Cálculo")
    
    # Mostrar valores base
    st.info(f"**Valores base para {destino}:**\n"
            f"• Alimentação: R$ {VALORES_DIARIAS[destino]['alimentacao']:.2f}\n"
            f"• Hospedagem: R$ {VALORES_DIARIAS[destino]['pousada']:.2f}\n"
            f"• Total diário: R$ {VALORES_DIARIAS[destino]['total']:.2f}")
    
    # Resultado do cálculo
    if resultado["diaria_total"] > 0:
        st.success(f"**💰 Valor da diária calculada: R$ {resultado['diaria_total']:.2f}**")
        
        # Detalhamento
        if resultado["diaria_alimentacao"] > 0:
            st.write(f"• Alimentação: R$ {resultado['diaria_alimentacao']:.2f}")
        if resultado["diaria_hospedagem"] > 0:
            st.write(f"• Hospedagem: R$ {resultado['diaria_hospedagem']:.2f}")
        
        if resultado["num_dias"] > 1:
            st.write(f"**🗓️ Total para {resultado['num_dias']} dias: R$ {resultado['total_viagem']:.2f}**")
            
        if resultado["percentual"] > 0:
            st.write(f"📈 Percentual aplicado: {resultado['percentual']}%")
            
    else:
        st.warning("⚠️ Nenhuma diária calculada para esta situação")
    
    # Observações
    if resultado["observacoes"]:
        st.subheader("📝 Observações")
        for obs in resultado["observacoes"]:
            st.write(f"• {obs}")

with col2:
    st.subheader("📋 Resumo da Viagem")
    
    # Card com resumo
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;">
        <h4>🎯 Destino</h4>
        <p>{destino}</p>
        
        <h4>⏰ Tipo de Deslocamento</h4>
        <p>{tipo_deslocamento}</p>
        
        <h4>📅 Duração</h4>
        <p>{num_dias} dia(s)</p>
        
        <h4>💰 Valor Total</h4>
        <h3 style="color: #1f77b4;">R$ {resultado['total_viagem']:.2f}</h3>
    </div>
    """, unsafe_allow_html=True)

# Seção de informações legais
st.subheader("⚖️ Base Legal")
with st.expander("Ver detalhes do Decreto nº 6.358/2024"):
    st.markdown("""
    **Artigo 10:** As diárias serão concedidas por dia de afastamento da sede, em valor equivalente a:
    - 70% para hospedagem
    - 30% para alimentação
    
    **Artigo 11:** Os valores são concedidos conforme a duração do deslocamento:
    - **50%** do valor de alimentação: 6-8h consecutivas (sem pernoite)
    - **100%** do valor de alimentação: >8h consecutivas (sem pernoite)
    - **100%** do valor de hospedagem: com pernoite em alojamento não gratuito
    - **100%** do valor total: >12h consecutivas com pernoite
    - **80%** do valor total: tripulante de aeronave (6-10h consecutivas)
    """)

# Tabela de referência
st.subheader("📊 Tabela de Valores de Referência")
df_valores = pd.DataFrame(VALORES_DIARIAS).T
df_valores.columns = ['Alimentação (R$)', 'Hospedagem (R$)', 'Total (R$)']
df_valores.index.name = 'Destino'
st.dataframe(df_valores, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Calculadora baseada no Decreto nº 6.358/2024 - Tabela de Valores Limites para Diárias em Viagens em Território Nacional")
