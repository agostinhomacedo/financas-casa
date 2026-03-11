import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Minha Casa Finanças", layout="centered", page_icon="💰")

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    
    # Inicializa a string da senha se não existir
    if "senha_digitada" not in st.session_state:
        st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.title("🔐 Acesso Restrito")
        st.markdown("### Digite a senha da casa:")
        
        # Exibe visualmente o progresso da senha (asteriscos)
        display_senha = " * " * len(st.session_state.senha_digitada)
        st.subheader(f"[{display_senha if display_senha else ' Aguardando... '}]")
        
        # Cria o teclado numérico 3x3 usando colunas
        for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            cols = st.columns(3)
            for i, num in enumerate(row):
                if cols[i].button(str(num), use_container_width=True, key=f"btn_{num}"):
                    st.session_state.senha_digitada += str(num)
                    st.rerun()

        # Linha inferior: Limpar, Zero e Entrar
        c1, c2, c3 = st.columns(3)
        if c1.button("Limpar ❌", use_container_width=True):
            st.session_state.senha_digitada = ""
            st.rerun()
            
        if c2.button("0", use_container_width=True, key="btn_0"):
            st.session_state.senha_digitada += "0"
            st.rerun()
            
        if c3.button("Entrar 🔓", type="primary", use_container_width=True):
            if st.session_state.senha_digitada == "1234": # <--- COLOQUE SUA SENHA AQUI
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                st.session_state.senha_digitada = ""
        
        return False
    return True
        
        # Usando number_input para forçar o teclado numérico no celular
        # O value=None e o placeholder ajudam na estética
        senha = st.number_input("Digite a senha da casa:", step=1, value=None, placeholder="Senha numérica")
        
        if st.button("Entrar", use_container_width=True):
            if str(senha) == "1234": # <--- SUA SENHA (como string para comparar)
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

if check_password():
    st.title("🏠 Finanças da Família")

    # --- LER DADOS DO GOOGLE SHEETS ---
    try:
        df = conn.read(ttl="0")
        df = df.dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # --- ENTRADA DE DADOS ---
    with st.sidebar:
        st.header("➕ Novo Registro")
        with st.form("meu_formulario", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Descrição", placeholder="Ex: Aluguel")
            valor_input = st.number_input("Valor", min_value=0.0, format="%.2f", step=1.0)
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Saúde", "Outros", "Cartão Crédito", "Aplicação Financeira"])
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            enviado = st.form_submit_button("💾 Salvar Registro", use_container_width=True)
            
            if enviado:
                if desc == "" or valor_input == 0:
                    st.warning("Preencha a descrição e o valor!")
                else:
                    valor_final = -valor_input if tipo == "Saída (Gasto)" else valor_input
                    novo_registro = pd.DataFrame([{
                        "Data": data.strftime("%d/%m/%Y"),
                        "Descrição": desc,
                        "Valor": valor_final,
                        "Categoria": cat,
                        "Tipo": tipo
                    }])
                    df_atualizado = pd.concat([df, novo_registro], ignore_index=True)
                    conn.update(data=df_atualizado)
                    st.success("Salvo!")
                    st.rerun()

    # --- PAINEL VISUAL ---
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = df[df["Valor"] < 0]["Valor"].sum()
        saldo = ganhos + gastos

        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", formatar_moeda(ganhos))
        c2.metric("Saídas", formatar_moeda(abs(gastos)))
        c3.metric("Saldo Atual", formatar_moeda(saldo))

        # Gráfico
        df_gastos = df[df["Valor"] < 0].copy()
        if not df_gastos.empty:
            st.subheader("🍕 Divisão de Gastos")
            df_gastos["Valor_Abs"] = df_gastos["Valor"].abs()
            fig = px.pie(df_gastos, values='Valor_Abs', names='Categoria', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📄 Histórico")
        for i, row in df.iloc[::-1].iterrows():
            col_data, col_desc, col_val, col_btn = st.columns([2, 3, 2, 1])
            cor = "red" if float(row['Valor']) < 0 else "green"
            col_data.write(row['Data'])
            col_desc.write(row['Descrição'])
            col_val.write(f":{cor}[{formatar_moeda(float(row['Valor']))}]")
            
            if col_btn.button("🗑️", key=f"del_{i}"):
                df_exclusao = df.drop(i)
                conn.update(data=df_exclusao)
                st.rerun()
    else:
        st.info("Ainda não há registros. Use o menu lateral!")
