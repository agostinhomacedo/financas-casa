import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E CSS "BLINDADO" ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💰")

# Este CSS usa seletores universais para garantir que o 3x3 se mantenha
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* --- TRAVA DO TECLADO 3X3 --- */
    /* Força o container de colunas a ser um Grid fixo */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 4px !important;
        margin-bottom: -20px !important;
    }
    
    /* Impede que as colunas individuais quebrem a linha */
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }

    /* Botões: Tamanho fixo e sem margens extras */
    .stButton > button {
        width: 100% !important;
        height: 50px !important;
        border-radius: 8px !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
        padding: 0px !important;
    }

    /* Botão OK (Entrar) */
    button[kind="primary"] {
        background-color: #007AFF !important;
        color: white !important;
        border: none !important;
    }

    /* Centraliza o teclado no celular sem esticar */
    .login-box {
        max-width: 300px;
        margin: 0 auto;
        padding-top: 2rem;
    }

    /* Ajuste para o conteúdo do App não cortar */
    .app-content {
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. TELA DE ACESSO ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>🔐 PIN de Acesso</h3>", unsafe_allow_html=True)
        
        # Display de PIN
        pin_dots = "".join([f"<span style='font-size: 30px; color: {'#007AFF' if i < len(st.session_state.senha_digitada) else '#DDD'}; margin: 0 5px;'>●</span>" for i in range(4)])
        st.markdown(f"<div style='text-align: center; margin-bottom: 15px;'>{pin_dots}</div>", unsafe_allow_html=True)

        # Teclado 3x3
        for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            c1, c2, c3 = st.columns(3)
            if c1.button(str(row[0]), key=f"k{row[0]}"):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[0]); st.rerun()
            if c2.button(str(row[1]), key=f"k{row[1]}"):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[1]); st.rerun()
            if c3.button(str(row[2]), key=f"k{row[2]}"):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[2]); st.rerun()

        c_del, c_zero, c_ok = st.columns(3)
        if c_del.button("⌫", key="del"): st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
        if c_zero.button("0", key="k0"):
            if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += "0"; st.rerun()
        if c_ok.button("OK", type="primary", key="ok"):
            if st.session_state.senha_digitada == "1234":
                st.session_state.password = True; st.rerun()
            else:
                st.error("Senha Incorreta"); st.session_state.senha_digitada = ""
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# --- 3. DASHBOARD ---
if check_password():
    st.markdown('<div class="app-content">', unsafe_allow_html=True)
    st.title("🏠 Minha Casa")
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        # Saldo em destaque
        st.metric("Saldo Atual", formatar_moeda(saldo))

        # Gráfico simplificado para não bugar no celular
        df_g = df[df["Valor"] < 0].copy()
        if not df_g.empty:
            st.write("🍕 **Gastos por Categoria**")
            fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.5)
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # Cadastro (na Sidebar para economizar tela)
    with st.sidebar:
        st.header("➕ Lançamento")
        with st.form("add_new"):
            t = st.selectbox("Tipo", ["Saída", "Entrada"])
            d = st.text_input("Descrição")
            v = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Salvar"):
                if d and v > 0:
                    vf = -v if t == "Saída" else v
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": d, "Valor": vf, "Categoria": "Geral", "Tipo": t}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.rerun()

    # Histórico simplificado
    st.write("---")
    st.write("📄 **Histórico Recente**")
    for i, row in df.iloc[::-1].head(10).iterrows():
        cor = "red" if float(row['Valor']) < 0 else "green"
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{row['Descrição']}**\n{row['Data']}")
        col2.write(f":{cor}[{formatar_moeda(float(row['Valor']))}]")
        if st.button("🗑️", key=f"d_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
