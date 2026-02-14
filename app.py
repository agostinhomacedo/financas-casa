import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Minha Casa Finanças", layout="centered", page_icon="💰")

def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if not st.session_state.password:
        st.title("🔐 Acesso Restrito")
        senha = st.text_input("Digite a senha da casa:", type="password")
        if st.button("Entrar"):
            if senha == "2804": # <--- SUA SENHA
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

if check_password():
    st.title("🏠 Finanças da Família")

    DB_FILE = "dados_financeiros.csv"
    COLunas = ["Data", "Descrição", "Valor", "Categoria", "Tipo"]

    # --- TRAVA DE SEGURANÇA PARA O ERRO DE COLUNAS ---
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=COLunas)
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)
        # Se o arquivo antigo tiver menos colunas que o novo, a gente reseta ele para evitar o erro
        if len(df.columns) != len(COLunas):
            df = pd.DataFrame(columns=COLunas)
            df.to_csv(DB_FILE, index=False)

    # --- ENTRADA DE DADOS ---
    with st.sidebar:
        st.header("➕ Novo Registro")
        tipo = st.radio("Tipo de Transação", ["Saída (Gasto)", "Entrada (Ganho)"])
        desc = st.text_input("Descrição", placeholder="Ex: Aluguel")
        valor_input = st.number_input("Valor", min_value=0.0, format="%.2f", step=1.0)
        cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Saúde", "Outros"])
        data = st.date_input("Data", datetime.now())
        
        if st.button("💾 Salvar Registro"):
            valor_final = -valor_input if tipo == "Saída (Gasto)" else valor_input
            novo = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, valor_final, cat, tipo]], columns=COLunas)
            df = pd.concat([df, novo], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("Salvo!")
            st.rerun()

    # --- PAINEL VISUAL ---
    if not df.empty:
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = df[df["Valor"] < 0]["Valor"].sum()
        saldo = ganhos + gastos

        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", f"R$ {ganhos:.2f}")
        c2.metric("Saídas", f"R$ {abs(gastos):.2f}", delta_color="inverse")
        c3.metric("Saldo Atual", f"R$ {saldo:.2f}")

        df_gastos = df[df["Valor"] < 0].copy()
        if not df_gastos.empty:
            st.subheader("🍕 Divisão de Gastos")
            df_gastos["Valor_Abs"] = df_gastos["Valor"].abs()
            fig = px.pie(df_gastos, values='Valor_Abs', names='Categoria', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📄 Histórico e Exclusão")
        
        for i, row in df.iloc[::-1].iterrows():
            col_data, col_desc, col_val, col_btn = st.columns([2, 3, 2, 1])
            cor = "red" if row['Valor'] < 0 else "green"
            col_data.write(row['Data'])
            col_desc.write(row['Descrição'])
            col_val.write(f":{cor}[R$ {row['Valor']:.2f}]")
            if col_btn.button("🗑️", key=f"del_{i}"):
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
    else:
        st.info("Ainda não há registros. Use o menu lateral!")
