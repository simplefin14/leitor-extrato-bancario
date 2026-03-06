
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conversor de Extrato", layout="wide")

st.title("📂 Leitor de Extrato Interativo")
st.markdown("Suba seu arquivo CSV para categorizar os lançamentos automaticamente.")

# --- SIDEBAR PARA UPLOAD ---
st.sidebar.header("Configurações")
arquivo_subido = st.sidebar.file_uploader("Escolha o arquivo CSV", type=['csv'])

# --- LÓGICA DE PROCESSAMENTO ---
if arquivo_subido is not None:
    # O Streamlit lê o arquivo subido diretamente como um buffer
    try:
        # Aqui usamos o encoding que descobrimos antes
        df = pd.read_csv(arquivo_subido, sep=";", encoding="ISO-8859-1")
        
        # Limpeza robusta (aquela que testamos no BDD)
        for col in ['Crédito (R$)', 'Débito (R$)', 'Saldo (R$)']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Aplicando a lógica de Status que validamos no Behave
        df['Status'] = df['Crédito (R$)'].apply(lambda x: 'Crédito' if x > 0 else 'Débito')

        # --- EXIBIÇÃO ---
        st.success("Arquivo processado com sucesso!")
        
        # Layout de métricas
        c1, c2 = st.columns(2)
        c1.metric("Entradas (Crédito)", f"R$ {df['Crédito (R$)'].sum():,.2f}")
        c2.metric("Saídas (Débito)", f"R$ {df['Débito (R$)'].sum():,.2f}")

        st.divider()
        st.subheader("Visualização dos Dados")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    st.info("Aguardando upload do arquivo CSV para iniciar a análise.")
        


