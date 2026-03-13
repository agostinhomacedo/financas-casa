import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. DESIGN SYSTEM (TRAVA MOBILE) ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💰")

st.markdown("""
    <style>
    /* Trava o app para não espalhar no desktop e ficar perfeito no mobile */
    .block-container { max-width: 350px !important; padding: 1rem !important; margin: auto; }
    
    /* FORÇA 3 COLUNAS SEM QUEBRA - RESOLVE A FOTO QUE VOCÊ MANDOU */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        margin-bottom: -20px !important;
    }
    [data-testid="column"] { flex: 1 !important; min-width: 0px !important; }

    /* BOTÕES ESTILO APP DE BANCO (INCLUINDO CORES CLARAS NOS TEXTOS) */
    .stButton > button {
        height: 55px !important;
        background: #1A1A1A !important;
        color: white !important;
        border-radius: 14px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border: 1px solid #333 !important;
    }
    /* Botão OK verde para destaque */
    button[kind="primary"] { background: #32D74B !important; color: black !important; border: none !important; }

    /* TEXTOS DOS LANÇAMENTOS (CORREÇÃO DE VISIBILIDADE) */
    .gasto-card {
        background: #1A1A1A;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #32D74B;
        margin-bottom: 10px;
    }
    .gasto-card b { color: #FFFFFF !important; font-size: 16px; }
    .gasto-card span { color: #CCCCCC !important; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# Conexão GSheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. LÓGICA DO TECLADO ---
if "pin" not in st.session_state: st.session_state.pin = ""
if "auth" not in st.session_state: st.session_state.auth = False

def teclou(n):
    if len(st.session_state.pin) < 4: st.session_state.pin += str(n)

if not st.session_state.auth:
    st.markdown("<h2 style='text-align: center; color: white;'>Acesso Familiar</h2>", unsafe_allow_html=True)
    
    # PIN Display
    visual = " ● " * len(st.session_state.pin) + " ○ " * (4 - len(st.session_state.pin))
    st.markdown(f"<h1 style='text-align: center; color: #32D74B;'>{visual}</h1>", unsafe_allow_html=True)

    # Teclado 3x3 Blindado
    for r in [[1,2,3],[4,5,6],[7,8,9]]:
        c1, c2, c3 = st.columns(3)
        if c1.button(str(r[0])): teclou(r[0]); st.rerun()
        if c2.button(str(r[1])): teclou(r[1]); st.rerun()
        if c3.button(str(r[2])): teclou(r[2]); st.rerun()
    
    c_del, c_zero, c_ok = st.columns(3)
    if c_del.button("⌫"): st.session_state.pin = st.session_state.pin[:-1]; st.rerun()
    if c_zero.button("0"): teclou(0); st.rerun()
    if c_ok.button("OK", type="primary"):
        if st.session_state.pin == "1234": # <--- SUA SENHA AQUI
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("PIN incorreto")
            st.session_state.pin = ""
else:
    # --- 3. ÁREA LOGADA (MODERNA E VISÍVEL) ---
    st.markdown("<h3 style='color: white;'>Olá! 👋</h3>", unsafe_allow_html=True)
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
        saldo = pd.to_numeric(df["Valor"]).sum()
    except:
        saldo = 0
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor"])

    # Saldo em destaque
    st.markdown(f"""
        <div style="background: #1A1A1A; padding: 20px; border-radius: 20px; border: 1px solid #32D74B; text-align: center; margin-bottom: 20px;">
            <p style="color: #888; margin: 0;">SALDO TOTAL</p>
            <h1 style="color: #32D74B; margin: 0;">R$ {saldo:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    # Botão de Lançar (na Sidebar para não poluir)
    with st.sidebar:
        st.header("➕ Novo Gasto")
        with st.form("add"):
            d = st.text_input("Descrição")
            v = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Salvar"):
                novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Descrição": d, "Valor": -v}])
                df = pd.concat([df, novo], ignore_index=True)
                conn.update(data=df)
                st.rerun()

    # Histórico de Lançamentos
    st.markdown("<p style='color: white; font-weight: bold;'>ÚLTIMOS LANÇAMENTOS</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(10).iterrows():
        st.markdown(f"""
            <div class="gasto-card">
                <div style="display: flex; justify-content: space-between;">
                    <b>{row['Descrição']}</b>
                    <b style="color: #FF453A;">R$ {abs(row['Valor']):,.2f}</b>
                </div>
                <span>{row['Data']}</span>
            </div>
        """, unsafe_allow_html=True)
