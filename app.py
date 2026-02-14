import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="Minha Casa Finanças", layout="centered", page_icon="💰")

def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if not st.session_state.password:
        st.title("🔐 Acesso Restrito")
        senha = st.text_input("Digite a senha da casa:", type="password")
        if st.button("Entrar"):
            if senha == "1234": # <--- COLOQUE SUA SENHA AQUI
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

if check_password():
    st.title("🏠 Finanças da Família")

    DB_FILE = "dados_financeiros.csv"
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria"])
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)

    # --- ENTRADA DE DADOS ---
    with st.sidebar:
        st.header("➕ Novo Registro")
        desc = st.text_input("O que comprou?")
        valor = st.number_input("Valor (Use - para gastos)", format="%.2f", step=1.0)
        cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Saúde", "Outros"])
        data = st.date_input("Data", datetime.now())
        
        if st.button("💾 Salvar no Sistema"):
            novo = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, valor, cat]], columns=df.columns)
            df = pd.concat([df, novo], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("Salvo!")
            st.rerun()

    # --- PAINEL VISUAL (DASHBOARD) ---
    if not df.empty:
        # Cálculos Rápidos
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = df[df["Valor"] < 0]["Valor"].sum()
        saldo = ganhos + gastos

        col1, col2, col3 = st.columns(3)
        col1.metric("Entradas", f"R$ {ganhos:.2f}")
        col2.metric("Saídas", f"R$ {abs(gastos):.2f}", delta_color="inverse")
        col3.metric("Saldo Atual", f"R$ {saldo:.2f}")

        st.divider()

        # Gráfico de Pizza (Apenas Despesas)
        st.subheader("🍕 Onde está o dinheiro?")
        df_gastos = df[df["Valor"] < 0].copy()
        df_gastos["Valor"] = df_gastos["Valor"].abs() # Gráfico precisa de valores positivos
        
        if not df_gastos.empty:
            fig = px.pie(df_gastos, values='Valor', names='Categoria', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ainda não há gastos registrados para gerar o gráfico.")

        # Tabela de Histórico
        with st.expander("📄 Ver Histórico Completo"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
            
            if st.button("🗑️ Apagar tudo e recomeçar"):
                os.remove(DB_FILE)
                st.rerun()
    else:
        st.info("Bem-vindo! Use o menu lateral para fazer seu primeiro registro.")
