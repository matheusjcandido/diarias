import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Diárias",
    page_icon="💰",
    layout="wide"
)

# Tentar configurar locale para português brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        # Se não conseguir, usar formato manual
        pass

# Função para formatar moeda
def format_currency(value):
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Título principal
st.title("💰 Calculadora de Diárias de Viagem")
st.caption("Baseado no Decreto nº 6.358/2024")

# Informações sobre como usar
st.info("""
📋 **Como funciona:**
- **Mesmo dia** (ida = retorno): Selecione a duração da viagem (6h, 8h, etc.)
- **Dias diferentes** (ida ≠ retorno): Automaticamente aplicará diária completa com pernoite
- **Gratuidades**: Marque se alimentação ou hospedagem são fornecidas gratuitamente
""")

st.markdown("---")

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

# Datas da viagem
st.sidebar.subheader("📅 Período da Viagem")
data_ida = st.sidebar.date_input(
    "Data de ida:",
    value=datetime.now().date(),
    min_value=datetime.now().date() - timedelta(days=365),
    max_value=datetime.now().date() + timedelta(days=365)
)

data_retorno = st.sidebar.date_input(
    "Data de retorno:",
    value=datetime.now().date(),
    min_value=data_ida,
    max_value=datetime.now().date() + timedelta(days=365)
)

# Validação de datas
if data_retorno < data_ida:
    st.sidebar.error("❌ A data de retorno não pode ser anterior à data de ida!")
    st.stop()

# Calcular número de dias e tipo de deslocamento
num_dias = (data_retorno - data_ida).days + 1
tem_pernoite = data_ida != data_retorno

# Tipo de deslocamento (apenas para viagens no mesmo dia)
if tem_pernoite:
    tipo_deslocamento = "Mais de 12 horas com pernoite (completa)"
    st.sidebar.success("🏨 Viagem com pernoite detectada - Diária completa aplicada")
else:
    st.sidebar.info("📅 Viagem no mesmo dia - Selecione a duração:")
    tipo_deslocamento = st.sidebar.selectbox(
        "Tipo de deslocamento (mesmo dia):",
        [
            "Até 6 horas (sem diária)",
            "6 a 8 horas consecutivas (sem pernoite)",
            "Mais de 8 horas consecutivas (sem pernoite)"
        ]
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
            
    elif tipo_deslocamento == "Mais de 12 horas com pernoite (completa)":
        if not alimentacao_gratuita:
            diaria_alimentacao = valor_alimentacao
        if not hospedagem_gratuita:
            diaria_hospedagem = valor_pousada
        percentual_aplicado = 100
        observacoes.append("100% do valor total (viagem com pernoite)")
    
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
            f"• Alimentação: {format_currency(VALORES_DIARIAS[destino]['alimentacao'])}\n"
            f"• Hospedagem: {format_currency(VALORES_DIARIAS[destino]['pousada'])}\n"
            f"• Total diário: {format_currency(VALORES_DIARIAS[destino]['total'])}")
    
    # Resultado do cálculo
    if resultado["diaria_total"] > 0:
        st.success(f"**💰 Valor da diária calculada: {format_currency(resultado['diaria_total'])}**")
        
        # Detalhamento
        if resultado["diaria_alimentacao"] > 0:
            st.write(f"• Alimentação: {format_currency(resultado['diaria_alimentacao'])}")
        if resultado["diaria_hospedagem"] > 0:
            st.write(f"• Hospedagem: {format_currency(resultado['diaria_hospedagem'])}")
        
        if resultado["num_dias"] > 1:
            st.write(f"**🗓️ Total para {resultado['num_dias']} dias: {format_currency(resultado['total_viagem'])}**")
            
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
    st.markdown("**🎯 Destino**")
    st.write(f"{destino}")
    
    st.markdown("**📅 Período da Viagem**")
    st.write(f"**Ida:** {data_ida.strftime('%d/%m/%Y')}")
    st.write(f"**Retorno:** {data_retorno.strftime('%d/%m/%Y')}")
    st.write(f"**Duração:** {num_dias} dia(s)")
    
    st.markdown("**⏰ Tipo de Deslocamento**")
    st.write(f"{tipo_deslocamento}")
    
    st.markdown("**💰 Valor Total**")
    st.markdown(f"### {format_currency(resultado['total_viagem'])}")

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
    - **100%** do valor total: viagem com pernoite (hospedagem + alimentação)
    """)

# Tabela de referência
st.subheader("📊 Tabela de Valores de Referência")
df_valores = pd.DataFrame(VALORES_DIARIAS).T
# Aplicar formatação de moeda
for col in df_valores.columns:
    df_valores[col] = df_valores[col].apply(format_currency)
df_valores.columns = ['Alimentação', 'Hospedagem', 'Total']
df_valores.index.name = 'Destino'
st.dataframe(df_valores, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Calculadora baseada no Decreto nº 6.358/2024 - Tabela de Valores Limites para Diárias em Viagens em Território Nacional")
