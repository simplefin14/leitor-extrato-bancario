import streamlit as st
import pandas as pd
import datetime
from io import StringIO

# ---------------- Configurações da página ----------------
st.set_page_config(
    page_title="Consolidador de Extratos - Bradesco",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Função de parse robusta ----------------
def parse_bradesco_csv(content: str) -> pd.DataFrame:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    transacoes = []
    lendo_extrato = False

    for line in lines:
        # Detecta o cabeçalho real do extrato
        if "Data;Lançamento;Dcto.;Crédito" in line or "Data;Lançamento;Crédito" in line:
            lendo_extrato = True
            continue
        if not lendo_extrato:
            continue

        parts = [p.strip() for p in line.split(';')]

        # Remove coluna vazia inicial (muito comum no Bradesco)
        if parts and parts[0] == "":
            parts = parts[1:]

        if len(parts) < 5:
            continue

        data_str = parts[0]
        try:
            data = datetime.datetime.strptime(data_str, "%d/%m/%Y")
        except:
            continue

        lancamento = parts[1]
        if lancamento.upper() == "SALDO ANTERIOR":
            continue  # ignora linha de saldo anterior

        documento = parts[2] if len(parts) > 2 else ""
        credito_str = parts[3] if len(parts) > 3 else ""
        debito_str = parts[4] if len(parts) > 4 else ""
        saldo_str = parts[5] if len(parts) > 5 else ""

        def to_float(val):
            if not val:
                return 0.0
            return float(str(val).replace(".", "").replace(",", "."))

        credito = to_float(credito_str)
        debito = to_float(debito_str)
        saldo = to_float(saldo_str)
        valor = credito - debito

        transacoes.append({
            "Data": data,
            "Lançamento": lancamento,
            "Documento": documento,
            "Crédito": credito,
            "Débito": debito,
            "Saldo": saldo,
            "Valor": valor
        })

    df = pd.DataFrame(transacoes)
    if df.empty:
        st.error("Nenhuma transação encontrada. Verifique o arquivo.")
        st.stop()

    df = df.sort_values("Data", ascending=False).reset_index(drop=True)
    df["id"] = df.index
    return df

# ---------------- Interface ----------------
st.title("🏦 Consolidador de Extratos Bradesco")
st.markdown("**Substitua planilhas por uma interface visual limpa e rápida.**")

uploaded_file = st.file_uploader(
    "Faça upload do CSV do extrato (exportado do Internet Banking Bradesco)",
    type="csv"
)

if uploaded_file:
    try:
        content = uploaded_file.read().decode("latin-1")  # encoding correto para Bradesco
        df = parse_bradesco_csv(content)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.stop()

    # Inicializa session_state
    if "selected" not in st.session_state:
        st.session_state.selected = set()
    if "categorias" not in st.session_state:
        st.session_state.categorias = {i: "Não categorizado" for i in df["id"]}

    # ---------------- Sidebar - Resumo em tempo real ----------------
    with st.sidebar:
        st.header("📊 Resumo dos Selecionados")

        selected_df = df[df["id"].isin(st.session_state.selected)]

        total_cred = selected_df["Crédito"].sum()
        total_deb = selected_df["Débito"].sum()
        liquido = total_cred - total_deb

        def fmt(v):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Créditos", fmt(total_cred))
            st.metric("Débito", fmt(total_deb))
        with col2:
            st.metric("Líquido", fmt(liquido))

        if liquido > 0:
            st.success(f"+ {fmt(liquido)}")
        elif liquido < 0:
            st.error(fmt(liquido))
        else:
            st.info("Zero")

        if st.button("Limpar seleção", type="secondary"):
            st.session_state.selected = set()
            st.rerun()

        st.divider()

        # Filtro por categoria (opcional mas muito útil)
        todas_cats = ["Receita", "Despesa", "Transferência", "Investimento", "PIX", "Boleto", "Salário", "Outros", "Não categorizado"]
        cats_usadas = set(st.session_state.categorias.values())
        opcoes_filtro = todas_cats + list(cats_usadas - set(todas_cats))

        filtro = st.multiselect("Filtrar por categoria", options=["Todas"] + opcoes_filtro, default=["Todas"])
        if "Todas" in filtro or not filtro:
            df_visivel = df.copy()
        else:
            df_visivel = df[df["id"].apply(lambda x: st.session_state.categorias.get(x) in filtro)]

    # ---------------- Cards das transações ----------------
    st.markdown(f"**{len(df_visivel)} transações carregadas** • Marque as desejadas")

    cores_categoria = {
        "Receita": "#10B981",       # verde
        "Salário": "#10B981",
        "PIX": "#8B5CF6",           # roxo
        "Despesa": "#EF4444",       # vermelho
        "Boleto": "#F59E0B",        # laranja
        "Transferência": "#3B82F6", # azul
        "Investimento": "#6366F1",
        "Outros": "#6B7280",
        "Não categorizado": "#9CA3AF"
    }

    for _, row in df_visivel.iterrows():
        idx = row["id"]
        checked = idx in st.session_state.selected

        with st.container(border=True):
            col_check, col_info, col_valor = st.columns([0.5, 5, 2.5])

            with col_check:
                if st.checkbox("", value=checked, key=f"chk_{idx}"):
                    st.session_state.selected.add(idx)
                else:
                    st.session_state.selected.discard(idx)

            with col_info:
                st.write(f"**{row['Data'].strftime('%d/%m/%Y')}** • {row['Lançamento'][:80]}{'...' if len(row['Lançamento']) > 80 else ''}")
                
                cat_atual = st.session_state.categorias[idx]
                nova_cat = st.selectbox(
                    "Categoria",
                    options=todas_cats + ["Customizar..."],
                    index=todas_cats.index(cat_atual) if cat_atual in todas_cats else len(todas_cats),
                    key=f"cat_{idx}",
                    label_visibility="collapsed"
                )
                
                if nova_cat == "Customizar...":
                    custom = st.text_input("Nome da categoria", key=f"custom_{idx}", label_visibility="collapsed")
                    if custom:
                        nova_cat = custom.strip()
                        if nova_cat not in todas_cats:
                            todas_cats.append(nova_cat)

                st.session_state.categorias[idx] = nova_cat
                
                cor = cores_categoria.get(nova_cat, "#9CA3AF")
                st.markdown(
                    f"<span style='background-color:{cor}; color:white; padding:4px 10px; border-radius:16px; font-size:0.85em; font-weight:500'>{nova_cat.upper()}</span>",
                    unsafe_allow_html=True
                )

            with col_valor:
                if row["Valor"] > 0:
                    st.success(f"+ {fmt(row['Valor'])}")
                elif row["Valor"] < 0:
                    st.error(f"- {fmt(abs(row['Valor']))}")
                else:
                    st.write("R$ 0,00")
                    
                st.caption(f"Saldo: {fmt(row['Saldo'])}")

    # ---------------- Rodapé ----------------
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Dica:** Você pode selecionar várias transações e copiar o resumo do sidebar.")
    with col2:
        st.write("Total de transações selecionadas: **{}**".format(len(st.session_state.selected)))
    with col3:
        if st.button("Exportar seleção como CSV"):
            export = selected_df[["Data", "Lançamento", "Crédito", "Débito", "Valor"]].copy()
            export["Data"] = export["Data"].dt.strftime("%d/%m/%Y")
            csv = export.to_csv(index=False, sep=";", decimal=",")
            st.download_button("Baixar CSV", csv, "selecao_extrato.csv", "text/csv")

else:
    st.info("Faça upload do arquivo CSV do extrato Bradesco para começar.")
    st.markdown("""
    ### Como usar:
    1. Entre no Internet Banking Bradesco → Extrato → Exportar → CSV
    2. Faça upload aqui
    3. Marque as transações que quiser somar/agrupar
    4. Veja o resultado em tempo real no painel lateral
    """)