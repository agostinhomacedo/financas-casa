import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E CSS "BLINDADO" ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💰")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000; }
    .block-container { max-width: 350px !important; padding: 1rem !important; margin: auto; }

    /* --- O TECLADO VIRTUAL FIXO --- */
    .grid-teclado {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin: 20px auto;
        max-width: 280px;
    }
    
    /* Estilização dos botões para parecerem App nativo */
    .stButton > button {
        width: 100% !important;
        height: 60px !important;
        border-radius: 15px !important;
        background-color: #1c1c1e !important;
        color: #fff !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border: 1px solid #333 !important;
    }
    
    /* Botão de Entrar (OK) */
    div.stButton > button[kind="primary"] {
        background: #32D74B !important;
        color: #000 !important;
        border: none !important;
    }

    /* Cards de Movimentação com Alto Contraste */
    .card {
        background: #1c1c1e;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    .card b { color: #FFFFFF !important; font-size: 16px; }
    .card span { color: #A1A1AA !important; font-size: 12px; }
    
    /* Esconde cabeçalhos inúteis */
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. LÓGICA DO PIN ---
if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""
if "password" not in st.session_state: st.session_state.password = False

def add_num(num):
    if len(st.session_state.senha_digitada) < 4:
        st.session_state.senha_digitada += str(num)

if not st.session_state.password:
    st.markdown("<h2 style='text-align: center; color: white;'>Acesso</h2>", unsafe_allow_html=True)
    
    # PIN Display
    dots = "".join([f"<span style='font-size: 40px; color: {'#32D74B' if i < len(st.session_state.senha_digitada) else '#333'}; margin: 0 10px;'>●</span>" for i in range(4)])
    st.markdown(f"<div style='text-align: center; margin-bottom: 30px;'>{dots}</div>", unsafe_allow_html=True)

    # Teclado (Aqui usamos o sistema de botões do Streamlit, mas agrupados)
    # Para garantir o 3x3 no celular, usamos colunas fixas e removemos o gap no CSS
    with st.container():
        # Linha 1
        c1, c2, c3 = st.columns(3)
        if c1.button("1"): add_num(1); st.rerun()
        if c2.button("2"): add_num(2); st.rerun()
        if c3.button("3"): add_num(3); st.rerun()
        # Linha 2
        c4, c5, c6 = st.columns(3)
        if c4.button("4"): add_num(4); st.rerun()
        if c5.button("5"): add_num(5); st.rerun()
        if c6.button("6"): add_num(6); st.rerun()
        # Linha 3
        c7, c8, c9 = st.columns(3)
        if c7.button("7"): add_num(7); st.rerun()
        if c8.button("8"): add_num(8); st.rerun()
        if c9.button("9"): add_num(9); st.rerun()
        # Linha 4
        c_del, c_zero, c_ok = st.columns(3)
        if c_del.button("⌫"): st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
        if c_zero.button("0"): add_num(0); st.rerun()
        if c_ok.button("OK", type="primary"):
            if st.session_state.senha_digitada == "1234":
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha Incorreta")
                st.session_state.senha_digitada = ""

# --- 3. ÁREA LOGADA ---
else:
    st.markdown("<h3 style='color: white;'>Olá, Família 👋</h3>", unsafe_allow_html=True)
    
    df = conn.read(ttl="0").dropna(how="all")
    saldo = pd.to_numeric(df["Valor"]).sum() if not df.empty else 0
    
    # Saldo com Alto Brilho
    st.markdown(f"""
        <div style="background: #1c1c1e; padding: 25px; border-radius: 20px; border: 1px solid #32D74B; text-align: center;">
            <p style="color: #A1A1AA; margin: 0;">SALDO DISPONÍVEL</p>
            <h1 style="color: #32D74B; margin: 0; font-size: 40px;">R$ {saldo:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar para adicionar
    with st.sidebar:
        st.header("Novo Lançamento")
        with st.form("add"):
            desc = st.text_input("Descrição")
            valor = st.number_input("Valor", min_value=0.0)
            tipo = st.radio("Tipo", ["Saída", "Entrada"])
            if st.form_submit_button("Salvar"):
                v = -valor if tipo == "Saída" else valor
                n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Descrição": desc, "Valor": v}])
                df = pd.concat([df, n], ignore_index=True)
                conn.update(data=df)
                st.rerun()

    # Histórico em Cards (Preto com Branco puro para enxergar bem)
    st.markdown("<br><p style='color: white; font-weight: bold;'>MOVIMENTAÇÕES</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(10).iterrows():
        cor = "#32D74B" if row['Valor'] > 0 else "#FF453A"
        st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between;">
                    <b>{row['Descrição']}</b>
                    <b style="color: {cor} !important;">R$ {abs(row['Valor']):,.2f}</b>
                </div>
                <span>{row['Data']}</span>
            </div>
        """, unsafe_allow_html=True)
