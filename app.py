import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CSS ULTRA-COMPACTO E INQUEBRÁVEL ---
st.set_page_config(page_title="Finanças", layout="centered")

st.markdown("""
    <style>
    /* Trava o fundo e a fonte */
    html, body, [class*="css"] { background-color: #000000 !important; color: #FFFFFF; }
    
    /* Trava o tamanho do App no celular */
    .block-container { max-width: 320px !important; padding: 0.5rem !important; margin: auto; }

    /* FORÇA 3 COLUNAS - O segredo para não empilhar na vertical */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
        margin-bottom: -25px !important;
    }
    [data-testid="column"] { flex: 1 !important; min-width: 0px !important; }

    /* TECLAS PEQUENAS E ACHATADAS */
    .stButton > button {
        height: 42px !important;
        background: #1C1C1E !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: 1px solid #333 !important;
    }
    button[kind="primary"] { background: #32D74B !important; color: #000 !important; border: none !important; }

    /* CARDS DE LANÇAMENTO (ALTO CONTRASTE) */
    .card {
        background: #111;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 5px;
    }
    .card b { color: #FFFFFF !important; }
    .card span { color: #888 !important; font-size: 11px; }

    /* Esconde lixo visual */
    header, footer, #MainMenu { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. LÓGICA DO PIN ---
if "pin" not in st.session_state: st.session_state.pin = ""
if "auth" not in st.session_state: st.session_state.auth = False

def add(n):
    if len(st.session_state.pin) < 4: st.session_state.pin += str(n)

if not st.session_state.auth:
    st.markdown("<p style='text-align: center; color: #888; margin-top: 10px;'>PIN DE ACESSO</p>", unsafe_allow_html=True)
    
    # Display do PIN
    visor = " ● " * len(st.session_state.pin) + " ○ " * (4 - len(st.session_state.pin))
    st.markdown(f"<h2 style='text-align: center; color: #32D74B;'>{visor}</h2>", unsafe_allow_html=True)

    # Teclado 3x3 que não quebra
    for r in [[1,2,3],[4,5,6],[7,8,9]]:
        c1, c2, c3 = st.columns(3)
        if c1.button(str(r[0])): add(r[0]); st.rerun()
        if c2.button(str(r[1])): add(r[1]); st.rerun()
        if c3.button(str(r[2])): add(r[2]); st.rerun()
    
    c_del, c_zero, c_ok = st.columns(3)
    if c_del.button("⌫"): st.session_state.pin = st.session_state.pin[:-1]; st.rerun()
    if c_zero.button("0"): add(0); st.rerun()
    if c_ok.button("OK", type="primary"):
        if st.session_state.pin == "1234":
            st.session_state.auth = True; st.rerun()
        else:
            st.toast("PIN Errado!"); st.session_state.pin = ""
else:
    # --- 3. ÁREA LOGADA (CONTRASTE MÁXIMO) ---
    st.markdown("<h4 style='color: white;'>Saldo</h4>", unsafe_allow_html=True)
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
        saldo = pd.to_numeric(df["Valor"]).sum()
    except:
        saldo, df = 0, pd.DataFrame(columns=["Data", "Descrição", "Valor"])

    st.markdown(f"""
        <div style="background: #111; padding: 15px; border-radius: 15px; border: 1px solid #32D74B; text-align: center;">
            <h2 style="color: #32D74B; margin: 0;">R$ {saldo:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Novo Gasto")
        with st.form("f", clear_on_submit=True):
            d = st.text_input("O que?")
            v = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Salvar"):
                novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Descrição": d, "Valor": -v}])
                df = pd.concat([df, novo], ignore_index=True)
                conn.update(data=df)
                st.rerun()

    st.markdown("<br><b style='font-size: 12px;'>HISTÓRICO</b>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(10).iterrows():
        st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between;">
                    <b>{row['Descrição']}</b>
                    <b style="color: #FF453A;">R$ {abs(row['Valor']):,.2f}</b>
                </div>
                <span>{row['Data']}</span>
            </div>
        """, unsafe_allow_html=True)
