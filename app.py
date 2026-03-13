import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Finanças Casa", layout="centered")

# CSS QUE TRAVA O TECLADO (Melhores práticas de design mobile)
st.markdown("""
    <style>
    /* Trava o container para não esticar */
    .block-container { max-width: 320px !important; padding: 1rem !important; margin: auto; }
    
    /* FORÇA 3 COLUNAS - O Streamlit não consegue quebrar isso */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
    }
    [data-testid="column"] { flex: 1 !important; min-width: 0px !important; }

    /* Estilo das teclas */
    .stButton > button {
        height: 55px !important;
        background: #1A1A1A !important;
        color: white !important;
        border-radius: 12px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border: 1px solid #333 !important;
    }
    button[kind="primary"] { background: #32D74B !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DO PIN ---
if "pin" not in st.session_state: st.session_state.pin = ""
if "autenticado" not in st.session_state: st.session_state.autenticado = False

def add_num(v):
    if len(st.session_state.pin) < 4: st.session_state.pin += str(v)

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center;'>🔐 PIN</h2>", unsafe_allow_html=True)
    
    # Visualização da senha
    senha_visivel = " ● " * len(st.session_state.pin) + " ○ " * (4 - len(st.session_state.pin))
    st.markdown(f"<h1 style='text-align: center; color: #32D74B;'>{senha_visivel}</h1>", unsafe_allow_html=True)

    # TECLADO INQUEBRÁVEL
    for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
        c1, c2, c3 = st.columns(3)
        if c1.button(str(row[0])): add_num(row[0]); st.rerun()
        if c2.button(str(row[1])): add_num(row[1]); st.rerun()
        if c3.button(str(row[2])): add_num(row[2]); st.rerun()
    
    c_del, c_zero, c_ok = st.columns(3)
    if c_del.button("⌫"): st.session_state.pin = st.session_state.pin[:-1]; st.rerun()
    if c_zero.button("0"): add_num(0); st.rerun()
    if c_ok.button("OK", type="primary"):
        if st.session_state.pin == "1234":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha Errada")
            st.session_state.pin = ""

else:
    # --- ÁREA DO DASHBOARD ---
    st.success("Bem-vindo de volta!")
    if st.button("Sair"): 
        st.session_state.autenticado = False
        st.session_state.pin = ""
        st.rerun()
    
    # Aqui entra o seu código do Google Sheets que já estava funcionando
    st.info("Conectando ao Google Sheets...")
