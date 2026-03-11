import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Minha Casa Finanças", layout="centered", page_icon="💰")

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def check_password():
    # Inicializa variáveis de controle na memória do navegador
    if "password" not in st.session_state:
        st.session_state.password = False
    if "senha_digitada" not in st.session_state:
        st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.title("🔐 Acesso Restrito")
        st.write("Digite a senha de 4 dígitos:")

        # Exibe os asteriscos da senha
        display = " ● " * len(st.session_state.senha_digitada)
        st.subheader(f"Senha: {display if display else '____'}")

        # Teclado Virtual (Botões 1-9)
        for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            cols = st.columns(3)
            for i, num in enumerate(row):
                if cols[i].button(str(num), use_container_width=True, key=f"key_{num}"):
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(num)
                        st.rerun()

        # Linha inferior do teclado
        c1, c2, c3 = st.columns(3)
        if c1.button("Limpar ❌", use_container_width=True):
            st.session_state.senha_digitada = ""
            st.rerun()
            
        if c2.button("0", use_container_width=True, key="key_0"):
            if len(st.session_state.senha_digitada) < 4:
                st.session_state.senha_digitada += "0"
                st.rerun()
            
        if c3.button("Entrar 🔓", type="primary", use_container_width=True):
            if st.session_state.senha_digitada == "2804": # <--- COLOQUE SUA SENHA AQUI
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                st.session_state.senha_digitada = ""
        
        return False
    return True

# --- EXECUÇÃO DO APP ---
if check_password():
    st.title("🏠 Finanças da Família")

    # LER DADOS
    try:
        df = conn.read(ttl="0")
        df = df.dropna(how="all")
    except Exception:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # BARRA LATERAL - NOVO REGISTRO
    with st.sidebar:
        st.header("➕ Novo Registro")
        with st.form("meu_formulario", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Descrição")
            valor_input = st.number_input("Valor", min_value=0.0, format="%.2f")
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Saúde", "Outros", "Cartão Crédito", "Aplicação Financeira"])
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            if st.form_submit_button("💾 Salvar Registro", use_container_width=True):
                if desc and valor_input > 0:
                    valor_final = -valor_input if tipo == "Saída (Gasto)" else valor_input
                    novo = pd.DataFrame([{"Data": data.strftime("%d/%m/%Y"), "Descrição": desc, "Valor": valor_final, "Categoria": cat, "Tipo": tipo}])
                    df = pd.concat([df, novo], ignore_index=True)
                    conn.update(data=df)
                    st.success("Salvo!")
                    st.rerun()
                else:
                    st.warning("Preencha tudo!")

    # PAINEL PRINCIPAL
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = df[df["Valor"] < 0]["Valor"].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", formatar_moeda(ganhos))
        c2.metric("Saídas", formatar_moeda(abs(gastos)))
        c3.metric("Saldo", formatar_moeda(ganhos + gastos))

        # Gráfico de Pizza
        df_gastos = df[df["Valor"] < 0].copy()
        if not df_gastos.empty:
            st.subheader("🍕 Gastos por Categoria")
            fig = px.pie(df_gastos, values=df_gastos["Valor"].abs(), names='Categoria', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📄 Histórico")
        for i, row in df.iloc[::-1].iterrows():
            cols = st.columns([2, 3, 2, 1])
            cor = "red" if float(row['Valor']) < 0 else "green"
            cols[0].write(row['Data'])
            cols[1].write(row['Descrição'])
            cols[2].write(f":{cor}[{formatar_moeda(float(row['Valor']))}]")
            if cols[3].button("🗑️", key=f"del_{i}"):
                df = df.drop(i)
                conn.update(data=df)
                st.rerun()
    else:
        st.info("Nenhum registro encontrado.")
