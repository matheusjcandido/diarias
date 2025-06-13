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
📋 **Como funciona (baseado em marco temporal):**
- **Marco temporal**: O horário de saída no primeiro dia determina o cálculo
- **Até 6h**: Sem direito à diária
- **6h a 8h**: 50% da diária de alimentação  
- **Mais de 8h (mesmo dia)**: 100% da diária de alimentação
- **Com pernoite**: Diária completa para cada período de 24h + cálculo do último dia baseado nas horas restantes
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
    
    /* Desktop - sidebar expandida por padrão */
    @media (min-width: 769px) {
        .st-emotion-cache-1cypcdb,
        .css-1cypcdb {
            transform: translateX(0px) !important;
            position: relative !important;
        }
    }
    
    /* Mobile - comportamento responsivo normal */
    @media (max-width: 768px) {
        /* Quando sidebar ABERTA */
        .st-emotion-cache-1cypcdb:not([aria-hidden="true"]),
        .css-1cypcdb:not([aria-hidden="true"]) {
            width: 18rem !important;
            min-width: 18rem !important;
        }
        
        /* Container principal quando sidebar ABERTA */
        .st-emotion-cache-1cypcdb:not([aria-hidden="true"]) ~ .block-container,
        .css-1cypcdb:not([aria-hidden="true"]) ~ .block-container {
            padding-left: 19rem !important;
            max-width: calc(100% - 19rem) !important;
        }
        
        /* Container principal quando sidebar FECHADA - volta ao normal */
        .st-emotion-cache-1cypcdb[aria-hidden="true"] ~ .block-container,
        .css-1cypcdb[aria-hidden="true"] ~ .block-container,
        .block-container {
            padding-left: 1rem !important;
            max-width: 100% !important;
            width: 100% !important;
        }
        
        /* Garantir que conteúdo se expanda quando sidebar fechada */
        .stApp > .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        
        /* Quando sidebar está visível, ajustar conteúdo */
        .stApp:has(.st-emotion-cache-1cypcdb:not([style*="translateX(-100%)"]):not([style*="translateX(-18rem)"])) .block-container {
            padding-left: 19rem !important;
            max-width: calc(100% - 19rem) !important;
        }
    }
</style>

<script>
// JavaScript apenas para ajustar layout - SEM interferir nos controles da sidebar
window.addEventListener('load', function() {
    // Função para ajustar layout baseado no estado da sidebar
    function adjustLayout() {
        const sidebar = document.querySelector('.st-emotion-cache-1cypcdb, .css-1cypcdb');
        const container = document.querySelector('.block-container');
        
        if (sidebar && container && window.innerWidth <= 768) {
            const sidebarStyle = window.getComputedStyle(sidebar);
            const transform = sidebarStyle.transform;
            
            // Se sidebar está fechada (translateX negativo)
            if (transform.includes('translateX(-') || sidebar.style.transform.includes('translateX(-')) {
                container.style.paddingLeft = '1rem';
                container.style.maxWidth = '100%';
                container.style.width = '100%';
            } else {
                // Sidebar aberta
                container.style.paddingLeft = '19rem';
                container.style.maxWidth = 'calc(100% - 19rem)';
            }
        }
    }
    
    // Observar APENAS mudanças de estilo na sidebar (não interferir em cliques)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            // Ajustar layout apenas quando há mudança real no estilo da sidebar
            if (mutation.type === 'attributes' && 
                (mutation.attributeName === 'style' || mutation.attributeName === 'aria-hidden')) {
                setTimeout(adjustLayout, 50); // Pequeno delay para garantir aplicação
            }
        });
    });
    
    const sidebar = document.querySelector('.st-emotion-cache-1cypcdb, .css-1cypcdb');
    
    if (sidebar) {
        observer.observe(sidebar, {
            attributes: true,
            attributeFilter: ['style', 'aria-hidden'] // Apenas observar mudanças de estilo
        });
    }
    
    // Ajustar no resize da janela
    window.addEventListener('resize', adjustLayout);
    
    // Ajuste inicial APENAS - sem interferir nos controles
    setTimeout(adjustLayout, 500);
});

// Prevenir comportamentos automáticos indesejados
document.addEventListener('click', function(e) {
    // NÃO interceptar cliques em campos de data ou outros controles
    // Deixar o Streamlit gerenciar normalmente
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

# Horário de saída
st.sidebar.subheader("⏰ Horário de Saída")
col_hora, col_min = st.sidebar.columns(2)
with col_hora:
    hora_saida = st.selectbox(
        "Hora:",
        options=list(range(0, 24)),
        index=8,  # 8h como padrão
        format_func=lambda x: f"{x:02d}"
    )
with col_min:
    minuto_saida = st.selectbox(
        "Minuto:",
        options=[0, 15, 30, 45],
        index=0,  # 00 como padrão
        format_func=lambda x: f"{x:02d}"
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

# Horário de retorno (apenas se data diferente)
if data_ida != data_retorno:
    st.sidebar.subheader("🔙 Horário de Retorno")
    col_hora_ret, col_min_ret = st.sidebar.columns(2)
    with col_hora_ret:
        hora_retorno = st.selectbox(
            "Hora:",
            options=list(range(0, 24)),
            index=17,  # 17h como padrão
            format_func=lambda x: f"{x:02d}",
            key="hora_retorno"
        )
    with col_min_ret:
        minuto_retorno = st.selectbox(
            "Minuto:",
            options=[0, 15, 30, 45],
            index=0,  # 00 como padrão
            format_func=lambda x: f"{x:02d}",
            key="minuto_retorno"
        )
else:
    # Viagem no mesmo dia - horário de retorno
    st.sidebar.subheader("🔙 Horário de Retorno")
    col_hora_ret, col_min_ret = st.sidebar.columns(2)
    with col_hora_ret:
        hora_retorno = st.selectbox(
            "Hora:",
            options=list(range(0, 24)),
            index=17,  # 17h como padrão
            format_func=lambda x: f"{x:02d}",
            key="hora_retorno"
        )
    with col_min_ret:
        minuto_retorno = st.selectbox(
            "Minuto:",
            options=[0, 15, 30, 45],
            index=0,  # 00 como padrão
            format_func=lambda x: f"{x:02d}",
            key="minuto_retorno"
        )

# Validação de datas e horários
if data_retorno < data_ida:
    st.sidebar.error("❌ A data de retorno não pode ser anterior à data de ida!")
    st.stop()

# Validação de horários para mesmo dia
if data_ida == data_retorno:
    hora_saida_total = hora_saida * 60 + minuto_saida
    hora_retorno_total = hora_retorno * 60 + minuto_retorno
    
    if hora_retorno_total <= hora_saida_total:
        st.sidebar.error("❌ O horário de retorno deve ser posterior ao horário de saída!")
        st.stop()

# Calcular datetime completos para saída e retorno
datetime_saida = datetime.combine(data_ida, datetime.min.time().replace(hour=hora_saida, minute=minuto_saida))
datetime_retorno = datetime.combine(data_retorno, datetime.min.time().replace(hour=hora_retorno, minute=minuto_retorno))

# Calcular total de horas
total_horas = (datetime_retorno - datetime_saida).total_seconds() / 3600
num_dias = (data_retorno - data_ida).days + 1

# Mostrar informações calculadas
st.sidebar.success(f"⏱️ Duração total: {total_horas:.1f} horas")
if num_dias > 1:
    st.sidebar.info(f"📅 Período: {num_dias} dia(s)")

# Remover seleção manual de tipo de deslocamento
# A lógica será automática baseada nas horas

# Alimentação e hospedagem gratuitas
col1, col2 = st.sidebar.columns(2)
with col1:
    alimentacao_gratuita = st.checkbox("Alimentação gratuita fornecida")
with col2:
    hospedagem_gratuita = st.checkbox("Hospedagem gratuita fornecida")

# Função para calcular a diária baseada em horários
def calcular_diaria_por_horario(destino, datetime_saida, datetime_retorno, total_horas, num_dias, alimentacao_gratuita, hospedagem_gratuita):
    valores = VALORES_DIARIAS[destino]
    valor_alimentacao = valores["alimentacao"]
    valor_pousada = valores["pousada"]
    valor_total_dia = valores["total"]
    
    # Inicializar valores
    total_viagem = 0
    observacoes = []
    detalhamento = []
    
    # Determinar tipo de viagem baseado nas horas
    if total_horas <= 6:
        # Até 6 horas - sem diária
        observacoes.append(f"Deslocamento de {total_horas:.1f}h - inferior a 6 horas, sem direito à diária")
        return {
            "total_viagem": 0,
            "observacoes": observacoes,
            "detalhamento": ["• Nenhuma diária calculada (menos de 6 horas)"],
            "tipo_calculado": "Até 6 horas (sem diária)"
        }
    
    elif total_horas <= 8:
        # 6 a 8 horas - 50% alimentação
        if not alimentacao_gratuita:
            diaria = valor_alimentacao * 0.5
            total_viagem = diaria
            detalhamento.append(f"• Alimentação (50%): {diaria:.2f}")
            observacoes.append(f"Deslocamento de {total_horas:.1f}h - 50% da diária de alimentação")
        else:
            observacoes.append("Alimentação gratuita fornecida - sem diária")
            detalhamento.append("• Alimentação gratuita fornecida")
        
        return {
            "total_viagem": total_viagem,
            "observacoes": observacoes,
            "detalhamento": detalhamento,
            "tipo_calculado": "6 a 8 horas (50% alimentação)"
        }
    
    elif num_dias == 1:
        # Mais de 8 horas no mesmo dia - 100% alimentação
        if not alimentacao_gratuita:
            diaria = valor_alimentacao
            total_viagem = diaria
            detalhamento.append(f"• Alimentação (100%): {diaria:.2f}")
            observacoes.append(f"Deslocamento de {total_horas:.1f}h no mesmo dia - 100% da diária de alimentação")
        else:
            observacoes.append("Alimentação gratuita fornecida - sem diária")
            detalhamento.append("• Alimentação gratuita fornecida")
        
        return {
            "total_viagem": total_viagem,
            "observacoes": observacoes,
            "detalhamento": detalhamento,
            "tipo_calculado": "Mais de 8 horas (100% alimentação)"
        }
    
    else:
        # Viagem com pernoite - lógica especial baseada no marco temporal
        observacoes.append(f"Viagem com pernoite - {total_horas:.1f}h totais em {num_dias} dia(s)")
        
        # Calcular diárias por período de 24h a partir do horário de saída
        data_atual = datetime_saida.date()
        horario_marco = datetime_saida.time()
        
        while data_atual < datetime_retorno.date():
            # Período de 24h completo - diária completa
            if not alimentacao_gratuita and not hospedagem_gratuita:
                diaria_dia = valor_total_dia
            else:
                diaria_dia = 0
                if not alimentacao_gratuita:
                    diaria_dia += valor_alimentacao
                if not hospedagem_gratuita:
                    diaria_dia += valor_pousada
            
            total_viagem += diaria_dia
            data_str = data_atual.strftime('%d/%m/%Y')
            detalhamento.append(f"• {data_str} (24h completas): {diaria_dia:.2f}")
            
            data_atual += timedelta(days=1)
        
        # Último dia - calcular horas restantes
        inicio_ultimo_dia = datetime.combine(data_atual, horario_marco)
        horas_ultimo_dia = (datetime_retorno - inicio_ultimo_dia).total_seconds() / 3600
        
        if horas_ultimo_dia > 6:
            # Mais de 6h no último dia - diária de alimentação
            if not alimentacao_gratuita:
                diaria_ultimo = valor_alimentacao
                total_viagem += diaria_ultimo
                data_str = data_atual.strftime('%d/%m/%Y')
                detalhamento.append(f"• {data_str} ({horas_ultimo_dia:.1f}h - só alimentação): {diaria_ultimo:.2f}")
            else:
                data_str = data_atual.strftime('%d/%m/%Y')
                detalhamento.append(f"• {data_str} ({horas_ultimo_dia:.1f}h - alimentação gratuita): 0.00")
        else:
            # Menos de 6h no último dia - sem diária
            data_str = data_atual.strftime('%d/%m/%Y')
            detalhamento.append(f"• {data_str} ({horas_ultimo_dia:.1f}h - menos de 6h): 0.00")
        
        return {
            "total_viagem": total_viagem,
            "observacoes": observacoes,
            "detalhamento": detalhamento,
            "tipo_calculado": "Viagem com pernoite (marco temporal)",
            "horas_ultimo_dia": horas_ultimo_dia
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
        
        # Detalhamento baseado no novo sistema
        if len(resultado["detalhamento"]) > 1:
            st.write("**📋 Detalhamento por período:**")
            for item in resultado["detalhamento"]:
                st.write(item)
        elif len(resultado["detalhamento"]) == 1:
            st.write("**📋 Composição:**")
            st.write(resultado["detalhamento"][0])
            
    else:
        st.warning("⚠️ Nenhuma diária calculada para esta situação")
    
    # Observações
    if resultado["observacoes"]:
        st.subheader("📝 Observações")
        for obs in resultado["observacoes"]:
            st.write(f"• {obs}")
    
    # Mostrar tipo de cálculo aplicado
    if "tipo_calculado" in resultado:
        st.info(f"**🔍 Tipo de cálculo aplicado:** {resultado['tipo_calculado']}")

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
    
    **Artigo 11:** Os valores são concedidos conforme a duração do deslocamento **a partir do marco temporal (horário de saída)**:
    - **0%**: Até 6 horas totais
    - **50%** do valor de alimentação: 6 a 8 horas totais
    - **100%** do valor de alimentação: Mais de 8 horas no mesmo dia
    - **100%** do valor total: Para cada período completo de 24h (viagem com pernoite)
    - **Último dia**: Calculado conforme horas restantes a partir do marco temporal
    
    **Marco Temporal:** O horário de saída no primeiro dia é a referência para todo o cálculo.
    
    **Exemplo:** Saída às 8h do dia 13/06, retorno às 9h do dia 14/06
    - Das 8h do dia 13 às 8h do dia 14: 24h (diária completa)
    - Das 8h às 9h do dia 14: 1h (menos de 6h, sem diária adicional)
    """)

# Valores de referência
st.subheader("💰 Valores de Referência")
st.caption(f"Valores base para {destino}: Alimentação: {format_currency(VALORES_DIARIAS[destino]['alimentacao'])} | Hospedagem: {format_currency(VALORES_DIARIAS[destino]['pousada'])} | Total diário: {format_currency(VALORES_DIARIAS[destino]['total'])}")

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
