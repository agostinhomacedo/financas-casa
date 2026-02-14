import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Minha Casa Finanças", layout="wide", page_icon="💰")

# Função para formatar moeda no padrão BR
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
    st.title("🏠 Painel Financeiro da Casa")

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
            desc = st.text_input("Descrição", placeholder="Ex: Fatura Nubank")
            valor_input = st.number_input("Valor", min_value=0.0, format="%.2f", step=1.0)
            
            # --- LISTA DE CATEGORIAS ATUALIZADA ---
            categorias = sorted([
                "Alimentação", "Cartão de Crédito", "Lazer", 
                "Moradia", "Salário", "Saúde", "Transporte", "Outros"
            ])
            cat = st.selectbox("Categoria", categorias)
            
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            enviado = st.form_submit_button("💾 Salvar Registro")
            
            if enviado:
                if desc == "" or valor_input == 0:
                    st.warning("Preencha a descrição e o valor!")
                else:
                    valor_final = -valor_input if tipo == "Saída (Gasto)" else valor_input
                    novo = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, valor_final, cat, tipo]], columns=COLunas)
                    df = pd.concat([df, novo], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Salvo!")
                    st.rerun()

    # --- PAINEL VISUAL ---
    if not df.empty:
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = abs(df[df["Valor"] < 0]["Valor"].sum())
        saldo = ganhos - gastos

        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Entradas", formatar_moeda(ganhos))
        m2.metric("Total de Saídas", formatar_moeda(gastos), delta_color="inverse")
        m3.metric("Saldo Atual", formatar_moeda(saldo))

        st.divider()

        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            st.subheader("📊 Entradas vs Saídas")
            df_comp = pd.DataFrame({
                "Tipo": ["Entradas", "Saídas"],
                "Valor": [ganhos, gastos]
            })
            fig_comp = px.bar(df_comp, x="Tipo", y="Valor", color="Tipo",
                             color_discrete_map={"Entradas": "#2ecc71", "Saídas": "#e74c3c"},
                             text_auto='.2s')
            st.plotly_chart(fig_comp, use_container_width=True)

        with col_graf2:
            st.subheader("🍕 Divisão por Categoria")
            df_gastos = df[df["Valor"] < 0].copy()
            if not df_gastos.empty:
                df_gastos["Valor_Abs"] = df_gastos["Valor"].abs()
                fig_pizza = px.pie(df_gastos, values='Valor_Abs', names='Categoria', hole=0.4)
                st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                st.info("Sem gastos para exibir a pizza.")

        st.subheader("📉 Ranking de Despesas por Categoria")
        if not df_gastos.empty:
            resumo_cat = df_gastos.groupby("Categoria")["Valor_Abs"].sum().reset_index().sort_values(by="Valor_Abs", ascending=True)
            fig_barras = px.bar(resumo_cat, y="Categoria", x="Valor_Abs", orientation='h',
                               labels={'Valor_Abs': 'Valor Total (R$)'},
                               color="Valor_Abs", color_continuous_scale="Reds")
            st.plotly_chart(fig_barras, use_container_width=True)

        st.divider()
        with st.expander("📄 Ver Histórico de Lançamentos e Excluir"):
            for i, row in df.iloc[::-1].iterrows():
                c_data, c_desc, c_cat, c_val, c_btn = st.columns([1.5, 2, 1.5, 2, 0.5])
                cor = "red" if row['Valor'] < 0 else "green"
                c_data.write(row['Data'])
                c_desc.write(row['Descrição'])
                c_cat.caption(row['Categoria'])
                c_val.write(f":{cor}[{formatar_moeda(row['Valor'])}]")
                if c_btn.button("🗑️", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
    else:
        st.info("Nenhum dado cadastrado ainda. Use o menu lateral para começar!")
