import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection # Biblioteca necessária

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Minha Casa Finanças", layout="centered", page_icon="💰")

# Conexão com Google Sheets
# Nota: Você precisará configurar o link da planilha no arquivo .streamlit/secrets.toml
conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if not st.session_state.password:
        st.title("🔐 Acesso Restrito")
        # Troque a linha da senha por esta:
senha = st.number_input("Digite a senha da casa:", step=1, value=None, placeholder="____")
        if st.button("Entrar"):
            if senha == "1234":
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

if check_password():
    st.title("🏠 Finanças da Família")

    # --- LER DADOS DO GOOGLE SHEETS ---
    # O comando abaixo lê a planilha configurada
    try:
        df = conn.read(ttl="0") # ttl="0" garante que ele sempre pegue o dado mais atual
        df = df.dropna(how="all") # Limpa linhas vazias
    except:
        st.error("Erro ao conectar com a planilha. Verifique as configurações.")
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
            
            enviado = st.form_submit_button("💾 Salvar Registro")
            
            if enviado:
                if desc == "" or valor_input == 0:
                    st.warning("Preencha a descrição e o valor!")
                else:
                    valor_final = -valor_input if tipo == "Saída (Gasto)" else valor_input
                    
                    # Criar nova linha
                    novo_registro = pd.DataFrame([{
                        "Data": data.strftime("%d/%m/%Y"),
                        "Descrição": desc,
                        "Valor": valor_final,
                        "Categoria": cat,
                        "Tipo": tipo
                    }])
                    
                    # Adicionar ao DF atual e atualizar Planilha
                    df_atualizado = pd.concat([df, novo_registro], ignore_index=True)
                    conn.update(data=df_atualizado)
                    
                    st.success("Salvo no Google Sheets!")
                    st.rerun()

    # --- PAINEL VISUAL ---
    if not df.empty:
        # Garantir que Valor é numérico
        df["Valor"] = pd.to_numeric(df["Valor"])
        
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = df[df["Valor"] < 0]["Valor"].sum()
        saldo = ganhos + gastos

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
        st.subheader("📄 Histórico")
        
        # Exibição do histórico
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
