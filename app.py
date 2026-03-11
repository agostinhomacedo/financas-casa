import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
# O layout="centered" ajuda a manter a interface elegante em desktops e celulares
st.set_page_config(page_title="Minha Casa Finanças", layout="centered", page_icon="💰")

# CSS Customizado para melhorar a experiência mobile (ajusta o preenchimento)
st.markdown("""
    <style>
    .main > div { padding-top: 2rem; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if "senha_digitada" not in st.session_state:
        st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.title("🔐 Acesso")
        
        # Centraliza a visualização da senha
        display = " ● " * len(st.session_state.senha_digitada)
        st.markdown(f"<h2 style='text-align: center;'>{display if display else '____'}</h2>", unsafe_allow_html=True)

        # Teclado Virtual Responsivo
        for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            cols = st.columns(3)
            for i, num in enumerate(row):
                if cols[i].button(str(num), use_container_width=True, key=f"k_{num}"):
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(num)
                        st.rerun()

        c1, c2, c3 = st.columns(3)
        if c1.button("Limpar", use_container_width=True):
            st.session_state.senha_digitada = ""
            st.rerun()
        if c2.button("0", use_container_width=True, key="k_0"):
            if len(st.session_state.senha_digitada) < 4:
                st.session_state.senha_digitada += "0"
                st.rerun()
        if c3.button("Entrar", type="primary", use_container_width=True):
            if st.session_state.senha_digitada == "2804":
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                st.session_state.senha_digitada = ""
        return False
    return True

if check_password():
    st.title("🏠 Finanças")

    # LER DADOS
    try:
        df = conn.read(ttl="0")
        df = df.dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # ENTRADA DE DADOS (Sidebar recolhe no mobile, o que é ótimo)
    with st.sidebar:
        st.header("➕ Novo Registro")
        with st.form("form_novo", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Descrição")
            valor_input = st.number_input("Valor", min_value=0.0, format="%.2f")
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Saúde", "Outros", "Cartão", "Investimento"])
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            if st.form_submit_button("💾 Salvar", use_container_width=True):
                if desc and valor_input > 0:
                    valor_final = -valor_input if tipo == "Saída (Gasto)" else valor_input
                    novo = pd.DataFrame([{"Data": data.strftime("%d/%m/%Y"), "Descrição": desc, "Valor": valor_final, "Categoria": cat, "Tipo": tipo}])
                    df = pd.concat([df, novo], ignore_index=True)
                    conn.update(data=df)
                    st.success("Salvo!")
                    st.rerun()

    # MÉTRICAS RESPONSIVAS
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = df[df["Valor"] < 0]["Valor"].sum()
        
        # Em telas muito pequenas, o Streamlit empilha essas colunas automaticamente
        m1, m2, m3 = st.columns(3)
        m1.metric("Ganhos", formatar_moeda(ganhos))
        m2.metric("Gastos", formatar_moeda(abs(gastos)))
        m3.metric("Saldo", formatar_moeda(ganhos + gastos))

        # GRÁFICO
        df_gastos = df[df["Valor"] < 0].copy()
        if not df_gastos.empty:
            st.subheader("🍕 Gastos")
            fig = px.pie(df_gastos, values=df_gastos["Valor"].abs(), names='Categoria', hole=0.4)
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20)) # Melhora uso de espaço no mobile
            st.plotly_chart(fig, use_container_width=True)

        # HISTÓRICO (Ajustado para telas estreitas)
        st.divider()
        st.subheader("📄 Histórico")
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                # No mobile, dividimos em 2 linhas se necessário ou colunas bem curtas
                cols = st.columns([3, 4, 1]) 
                cor = "red" if float(row['Valor']) < 0 else "green"
                
                cols[0].write(f"**{row['Data']}**")
                cols[1].write(f":{cor}[{formatar_moeda(float(row['Valor']))}]")
                if cols[2].button("🗑️", key=f"d_{i}"):
                    df = df.drop(i)
                    conn.update(data=df)
                    st.rerun()
                st.caption(f"{row['Descrição']} | {row['Categoria']}")
                st.write("---")
    else:
        st.info("Nenhum dado encontrado.")
