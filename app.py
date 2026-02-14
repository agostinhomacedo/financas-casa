import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Minha Casa Finanças", layout="centered", page_icon="💰")

# Função para formatar moeda no padrão BR: 1.234,56
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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

    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=COLunas)
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)
        if len(df.columns) != len(COLunas):
            df = pd.DataFrame(columns=COLunas)
            df.to_csv(DB_FILE, index=False)

    # --- ENTRADA DE DADOS ---
    with st.sidebar:
        st.header("➕ Novo Registro")
        with st.form("meu_formulario", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Descrição", placeholder="Ex: Aluguel")
            
            # Campo de entrada (no padrão do sistema para cálculo)
            valor_input = st.number_input("Valor", min_value=0.0, format="%.2f", step=1.0)
            
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Saúde", "Outros"])
            
            # Formato de data configurado para o padrão brasileiro
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            enviado = st.form_submit_button("💾 Salvar Registro")
            
            if enviado:
                if desc == "" or valor_input == 0:
                    st.warning("Preencha a descrição e o valor!")
                else:
                    valor_final = -valor_input if tipo == "Saída (Gasto)" else valor_input
                    # Salvando a data no formato dd/mm/yyyy
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

        # Métricas com formatação brasileira
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", formatar_moeda(ganhos))
        c2.metric("Saídas", formatar_moeda(abs(gastos)), delta_color="inverse")
        c3.metric("Saldo Atual", formatar_moeda(saldo))

        df_gastos = df[df["Valor"] < 0].copy()
        if not df_gastos.empty:
            st.subheader("🍕 Divisão de Gastos")
            df_gastos["Valor_Abs"] = df_gastos["Valor"].abs()
            fig = px.pie(df_gastos, values='Valor_Abs', names='Categoria', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📄 Histórico e Exclusão")
        
        # Histórico formatado
        for i, row in df.iloc[::-1].iterrows():
            col_data, col_desc, col_val, col_btn = st.columns([2, 3, 2, 1])
            cor = "red" if row['Valor'] < 0 else "green"
            
            col_data.write(row['Data']) # Já está como dd/mm/yyyy
            col_desc.write(row['Descrição'])
            col_val.write(f":{cor}[{formatar_moeda(row['Valor'])}]")
            
            if col_btn.button("🗑️", key=f"del_{i}"):
                df = df.drop(i)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
    else:
        st.info("Ainda não há registros. Use o menu lateral!")
