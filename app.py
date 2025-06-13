import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Diárias",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar expandida por padrão
)

# Configurar formatação brasileira
import os
os.environ['LC_ALL'] = 'pt_BR.UTF-8'

# Tentar configurar locale para português brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except:
            # Se não conseguir, usar formato manual
            pass

# Função para formatar moeda
def format_currency(value):
    """Formata valor para moeda brasileira: R$ 1.234,56"""
    # Converter para float se necessário
    if isinstance(value, str):
        value = float(value)
    
    # Formatação manual para garantir padrão brasileiro
    valor_str = f"{value:.2f}"  # Formato: 1234.56
    partes = valor_str.split('.')
    inteira = partes[0]
    decimal = partes[1]
    
    # Adicionar pontos para milhares
    if len(inteira) > 3:
        # Reverter string, adicionar pontos a cada 3 dígitos, reverter novamente
        inteira_invertida = inteira[::-1]
        inteira_com_pontos = '.'.join([inteira_invertida[i:i+3] for i in range(0, len(inteira_invertida), 3)])
        inteira = inteira_com_pontos[::-1]
    
    return f"R$ {inteira},{decimal}"

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
    ["Demais Municípios", "Distrito Federal", "Capitais de Estado"],
    index=0  # Demais Municípios como padrão
)

# Datas da viagem
st.sidebar.subheader("📅 Período da Viagem")

# CSS personalizado para melhorar a formatação
st.markdown("""
<style>
    /* Customização para inputs de data */
    .stDateInput > div > div > input {
        text-align: center;
    }
    
    /* Tooltip para formato de data */
    .date-help {
        font-size: 0.8em;
        color: #666;
        font-style: italic;
        margin-top: -10px;
        margin-bottom: 10px;
    }
    
    /* Forçar sidebar aberta - Classes mais recentes do Streamlit */
    .st-emotion-cache-1cypcdb,
    .st-emotion-cache-10trblm,
    .css-1d391kg {
        width: 21rem !important;
        min-width: 21rem !important;
    }
    
    /* Para dispositivos móveis - manter sidebar visível */
    @media (max-width: 768px) {
        .st-emotion-cache-1cypcdb,
        .st-emotion-cache-10trblm,
        .css-1d391kg {
            width: 18rem !important;
            min-width: 18rem !important;
            max-width: 18rem !important;
            transform: translateX(0px) !important;
            position: relative !important;
        }
        
        /* Esconder botão de toggle em mobile */
        .st-emotion-cache-14xtw13,
        .css-14xtw13 {
            display: none !important;
        }
        
        /* Ajustar container principal */
        .block-container,
        .st-emotion-cache-1y4p8pa {
            padding-left: 19rem !important;
            max-width: calc(100% - 19rem) !important;
        }
    }
    
    /* Desktop - garantir sidebar sempre visível */
    @media (min-width: 769px) {
        .st-emotion-cache-1cypcdb,
        .css-1cypcdb {
            transform: translateX(0px) !important;
            position: relative !important;
        }
    }
</style>

<script>
// JavaScript para expandir sidebar automaticamente
window.addEventListener('load', function() {
    // Tentar expandir sidebar após carregar
    setTimeout(function() {
        const sidebarButtons = document.querySelectorAll('[data-testid="baseButton-header"]');
        sidebarButtons.forEach(button => {
            if (button.getAttribute('aria-expanded') === 'false') {
                button.click();
            }
        });
    }, 1000);
});
</script>
""", unsafe_allow_html=True)

data_ida = st.sidebar.date_input(
    "Data de ida:",
    value=datetime.now().date(),
    min_value=datetime.now().date() - timedelta(days=365),
    max_value=datetime.now().date() + timedelta(days=365),
    format="DD/MM/YYYY"
)

# Definir valor padrão para retorno (sempre >= data de ida)
valor_padrao_retorno = max(data_ida, datetime.now().date())

data_retorno = st.sidebar.date_input(
    "Data de retorno:",
    value=valor_padrao_retorno,
    min_value=data_ida,
    max_value=datetime.now().date() + timedelta(days=365),
    format="DD/MM/YYYY"
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
def calcular_diaria(destino, tipo_deslocamento, num_dias, data_ida, data_retorno, alimentacao_gratuita, hospedagem_gratuita):
    valores = VALORES_DIARIAS[destino]
    valor_alimentacao = valores["alimentacao"]
    valor_pousada = valores["pousada"]
    valor_total_dia = valores["total"]
    
    # Inicializar valores
    diaria_alimentacao = 0
    diaria_hospedagem = 0
    percentual_aplicado = 0
    observacoes = []
    
    # Verificar se é viagem com pernoite
    tem_pernoite = data_ida != data_retorno
    
    if tem_pernoite:
        # Viagem com pernoite - lógica especial
        dias_com_pernoite = num_dias - 1  # Todos os dias exceto o último
        dia_retorno = 1  # Apenas o último dia
        
        total_viagem = 0
        
        # Calcular diárias para dias com pernoite (ida + dias intermediários)
        if dias_com_pernoite > 0:
            # Para dias com pernoite, usar o valor total da tabela se não há gratuidades
            # ou calcular parcialmente se há gratuidades
            if not alimentacao_gratuita and not hospedagem_gratuita:
                # Usar valor total da tabela
                diaria_completa_por_dia = valor_total_dia
            else:
                # Calcular parcialmente se há gratuidades
                diaria_completa_por_dia = 0
                if not alimentacao_gratuita:
                    diaria_completa_por_dia += valor_alimentacao
                if not hospedagem_gratuita:
                    diaria_completa_por_dia += valor_pousada
            
            total_dias_pernoite = diaria_completa_por_dia * dias_com_pernoite
            total_viagem += total_dias_pernoite
        
        # Calcular diária para o dia de retorno (apenas alimentação)
        diaria_retorno = 0
        if not alimentacao_gratuita:
            diaria_retorno = valor_alimentacao
        
        total_viagem += diaria_retorno
        
        # Para exibição (usar valores da tabela quando possível)
        if not alimentacao_gratuita and not hospedagem_gratuita:
            # Usar valor total da tabela para exibição
            valor_dia_completo = valor_total_dia
        else:
            # Calcular parcialmente para exibição
            valor_dia_completo = 0
            if not alimentacao_gratuita:
                valor_dia_completo += valor_alimentacao
            if not hospedagem_gratuita:
                valor_dia_completo += valor_pousada
        
        diaria_alimentacao = valor_alimentacao if not alimentacao_gratuita else 0
        diaria_hospedagem = valor_pousada if not hospedagem_gratuita else 0
        percentual_aplicado = 100
        
        if dias_com_pernoite > 0 and diaria_retorno > 0:
            observacoes.append(f"Viagem com pernoite: {dias_com_pernoite} dia(s) completo(s) + 1 dia retorno (só alimentação)")
        elif dias_com_pernoite > 0:
            observacoes.append(f"Viagem com pernoite: {dias_com_pernoite} dia(s) completo(s)")
        elif diaria_retorno > 0:
            observacoes.append("Dia de retorno: apenas alimentação")
        else:
            observacoes.append("Viagem com pernoite - alimentação/hospedagem gratuitas")
        
        return {
            "diaria_alimentacao": diaria_alimentacao,
            "diaria_hospedagem": diaria_hospedagem,
            "diaria_total": valor_dia_completo,
            "total_viagem": total_viagem,
            "percentual": percentual_aplicado,
            "observacoes": observacoes,
            "num_dias": num_dias,
            "dias_pernoite": dias_com_pernoite,
            "dia_retorno": dia_retorno,
            "valor_dia_pernoite": valor_dia_completo if dias_com_pernoite > 0 else 0,
            "valor_dia_retorno": diaria_retorno
        }
    
    else:
        # Viagem no mesmo dia - lógica original
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
resultado = calcular_diaria(destino, tipo_deslocamento, num_dias, data_ida, data_retorno, alimentacao_gratuita, hospedagem_gratuita)

# Layout principal com colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Resultado do Cálculo")
    
    # Resultado do cálculo
    if resultado["total_viagem"] > 0:
        st.success(f"**💰 Valor total da viagem: {format_currency(resultado['total_viagem'])}**")
        
        # Detalhamento para viagem com pernoite
        if 'dias_pernoite' in resultado and resultado['dias_pernoite'] > 0:
            st.write("**📋 Detalhamento:**")
            if resultado['valor_dia_pernoite'] > 0:
                valor_total_pernoite = resultado['valor_dia_pernoite'] * resultado['dias_pernoite']
                st.write(f"• {resultado['dias_pernoite']} dia(s) com pernoite: {resultado['valor_dia_pernoite']:.2f} × {resultado['dias_pernoite']} = {valor_total_pernoite:.2f}")
            if 'valor_dia_retorno' in resultado and resultado['valor_dia_retorno'] > 0:
                st.write(f"• 1 dia de retorno (só alimentação): {resultado['valor_dia_retorno']:.2f}")
                
        # Detalhamento para viagem no mesmo dia
        else:
            if resultado["diaria_alimentacao"] > 0:
                st.write(f"• Alimentação: {resultado['diaria_alimentacao']:.2f}")
            if resultado["diaria_hospedagem"] > 0:
                st.write(f"• Hospedagem: {resultado['diaria_hospedagem']:.2f}")
            
            if resultado["num_dias"] > 1:
                st.write(f"**🗓️ Total para {resultado['num_dias']} dias: {resultado['total_viagem']:.2f}**")
                
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
    
    **Observação importante:** No dia de retorno não há pernoite, sendo calculada apenas a diária de alimentação.
    """)

# Tabela de referência
st.subheader("📊 Tabela Completa de Valores")
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
