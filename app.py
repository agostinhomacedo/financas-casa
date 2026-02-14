import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="Minha Casa Finanças", layout="centered")

# Senha simples para privacidade (Altere '1234' para sua senha)
def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if not st.session_state.password:
        senha = st.text_input("Digite a senha da casa:", type="password")
        if senha == "2804": # <--- ALTERE AQUI
            st.session_state.password = True
            st.rerun()
        return False
    return True

if check_password():
    st.title("🏠 Controle Financeiro Doméstico")

    # Arquivo para salvar os dados
    DB_FILE = "dados_financeiros.csv"

    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria"])
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)

    # --- ENTRADA DE DADOS ---
    with st.expander("➕ Registrar Novo Gasto/Ganho", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            desc = st.text_input("Descrição", placeholder="Ex: Supermercado")
            valor = st.number_input("Valor (Negativo para gastos)", format="%.2f")
        with col2:
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Outros"])
            data = st.date_input("Data", datetime.now())

        if st.button("Salvar Registro"):
            novo_dado = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, valor, cat]], 
                                    columns=["Data", "Descrição", "Valor", "Categoria"])
            df = pd.concat([df, novo_dado], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("Registrado com sucesso!")
            st.rerun()

    # --- RESUMO FINANCEIRO ---
    st.divider()
    saldo = df["Valor"].sum()
    cor_saldo = "green" if saldo >= 0 else "red"
    st.markdown(f"### Saldo Atual: :{cor_saldo}[R$ {saldo:.2f}]")

    # Exibir Tabela
    if not df.empty:
        st.write("#### Últimos Lançamentos")
        st.dataframe(df.tail(10), use_container_width=True)
        
        if st.button("Limpar Tudo (Cuidado!)"):
            os.remove(DB_FILE)
            st.rerun()
