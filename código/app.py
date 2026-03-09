import streamlit as st
import pandas as pd

st.set_page_config(page_title="Leitor Interativo", layout="wide")

# CSS melhorado com estilos para botões proporcionais
st.markdown("""
    <style>
    .valor-positivo { color: #28a745; font-weight: bold; font-size: 32px; }
    .valor-negativo { color: #dc3545; font-weight: bold; font-size: 32px; }
    
    /* Estilo para botões compactos e proporcionais */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Container específico para o botão */
    .botao-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        height: 100%;
    }
    
    /* Botão compacto */
    .stButton button {
        background-color: #f0f2f6;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 0px 10px !important;
        margin: 0px !important;
        height: 36px !important;
        min-width: 45px !important;
        font-size: 18px !important;
        font-weight: normal;
        line-height: 1 !important;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Botão na coluna de conciliados */
    .stButton button:has(span:contains("⬅️")) {
        background-color: #e8f4fd;
        border-color: #b8d9f5;
    }
    
    /* Efeito hover */
    .stButton button:hover {
        background-color: #e6e9ef !important;
        border-color: #bbb !important;
        transform: scale(1.02);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Botão quando clicado */
    .stButton button:active {
        background-color: #d0d4dc !important;
        transform: scale(0.98);
    }
    
    /* Ajuste para o texto dentro do card */
    .stContainer {
        padding: 1rem !important;
    }
    
    /* Ajuste para captions */
    .stCaption {
        margin-bottom: 0.25rem !important;
        color: #666;
    }
    
    /* Melhor espaçamento no card */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.5rem;
    }
    
    /* Ajuste para as colunas dentro do card */
    div.row-widget.stHorizontal {
        align-items: center;
        margin-top: 0.25rem;
    }
    
    /* Esconder scrollbars internas se houver */
    section[data-testid="stSidebar"] .stButton button {
        height: 40px !important;
        padding: 0 16px !important;
    }
    
    /* Estilo para a linha de card + botão */
    .linha-card {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
    }
    
    .card-container {
        flex: 1;
    }
    
    .botao-lateral {
        width: 50px;
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE LIMPEZA ---
@st.cache_data
def processar_extrato(arquivo):
    df = pd.read_csv(arquivo, sep=";", encoding="ISO-8859-1")
    for col in ['Crédito (R$)', 'Débito (R$)']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Adicionamos um ID único e o Status inicial para controlar onde o card está
    df['ID_Transacao'] = range(len(df))
    df['Status_Conciliacao'] = 'Pendente'
    return df

# --- INTERFACE ---
st.title("📊 Extrato Interativo")

arquivo_subido = st.sidebar.file_uploader("Suba seu CSV aqui", type=["csv"])

if arquivo_subido:
    # Inicializa o DataFrame no session_state para podermos modificá-lo
    if 'df_dados' not in st.session_state:
        st.session_state.df_dados = processar_extrato(arquivo_subido)

    df = st.session_state.df_dados

    # --- MÉTRICAS GERAIS ---
    total_conciliado = 0.0
    itens_conciliados = df[df['Status_Conciliacao'] == 'Conciliado']
    
    for _, linha in itens_conciliados.iterrows():
        valor = linha['Crédito (R$)'] if linha['Crédito (R$)'] > 0 else -linha['Débito (R$)']
        total_conciliado += valor

    st.sidebar.divider()
    st.sidebar.metric("Total Conciliado", f"R$ {total_conciliado:,.2f}")
    
    if st.sidebar.button("Resetar Tudo", use_container_width=True):
        st.session_state.df_dados['Status_Conciliacao'] = 'Pendente'
        st.rerun()

    st.divider()

    # --- LAYOUT KANBAN (DUAS COLUNAS PRINCIPAIS) ---
    col_pendentes, espaco, col_conciliados = st.columns([1, 0.1, 1])

    # --- COLUNA 1: PENDENTES ---
    with col_pendentes:
        st.subheader("📥 Pendentes")
        df_pendentes = df[df['Status_Conciliacao'] == 'Pendente']
        
        if df_pendentes.empty:
            st.success("Tudo conciliado por aqui! 🎉")
        
        # Criar uma lista para armazenar os cards
        for idx, linha in df_pendentes.iterrows():
            e_credito = linha['Crédito (R$)'] > 0
            valor_exibir = linha['Crédito (R$)'] if e_credito else linha['Débito (R$)']
            classe_cor = "valor-positivo" if e_credito else "valor-negativo"
            
            # Usando colunas para alinhar card e botão na mesma linha
            col_card, col_btn = st.columns([0.9, 0.1])
            
            with col_card:
                # Card com a transação
                with st.container(border=True):
                    st.caption(f"📅 {linha['Data']} | {'Entrada' if e_credito else 'Saída'}")
                    st.markdown(f"**{linha['Lançamento']}**")
                    st.markdown(f"<span class='{classe_cor}'>R$ {valor_exibir:,.2f}</span>", unsafe_allow_html=True)
            
            with col_btn:
                # Botão fora do card, alinhado verticalmente
                st.write("")  # Espaço para alinhar com o topo do card
                if st.button("➡️", key=f"btn_ir_{linha['ID_Transacao']}", use_container_width=False):
                    st.session_state.df_dados.loc[idx, 'Status_Conciliacao'] = 'Conciliado'
                    st.rerun()

    # --- COLUNA 2: CONCILIADOS ---
    with col_conciliados:
        st.subheader("✅ Conciliados")
        
        if itens_conciliados.empty:
            st.info("Nenhuma transação conciliada ainda.")
        
        for idx, linha in itens_conciliados.iterrows():
            e_credito = linha['Crédito (R$)'] > 0
            valor_exibir = linha['Crédito (R$)'] if e_credito else linha['Débito (R$)']
            classe_cor = "valor-positivo" if e_credito else "valor-negativo"
            
            # Usando colunas para alinhar card e botão na mesma linha
            col_card, col_btn = st.columns([0.9, 0.1])
            
            with col_card:
                # Card com a transação
                with st.container(border=True):
                    st.caption(f"📅 {linha['Data']} | {'Entrada' if e_credito else 'Saída'}")
                    st.markdown(f"**{linha['Lançamento']}**")
                    st.markdown(f"<span class='{classe_cor}'>R$ {valor_exibir:,.2f}</span>", unsafe_allow_html=True)
            
            with col_btn:
                # Botão fora do card, alinhado verticalmente
                st.write("")  # Espaço para alinhar com o topo do card
                if st.button("⬅️", key=f"btn_voltar_{linha['ID_Transacao']}", use_container_width=False):
                    st.session_state.df_dados.loc[idx, 'Status_Conciliacao'] = 'Pendente'
                    st.rerun()

else:
    st.info("Faça o upload do extrato para começar.")