import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E CSS PARA TECLADO MINI 3x3 ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💳")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* --- ESTREITAR O TECLADO --- */
    .block-container { 
        max-width: 280px !important; /* Caixa do teclado bem estreita */
        padding-top: 1rem !important;
        margin: auto;
    }

    /* Forçar 3 colunas sem quebra */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important; 
        margin-bottom: -22px !important; /* Cola as teclas verticalmente */
    }
    
    [data-testid="column"] {
        width: 33.33% !important;
        flex: 1 1 33.33% !important;
    }

    /* Teclas Menores */
    .stButton > button {
        height: 42px !important; /* Altura reduzida */
        border-radius: 8px !important;
        background: white !important;
        border: 1px solid #ddd !important;
        font-size: 16px !important; /* Fonte menor para combinar */
        font-weight: 600 !important;
        padding: 0px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    button[kind="primary"] {
        background: #1a1a1a !important;
        color: white !important;
    }

    /* Ajuste de margens para o display de senha */
    h1 { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. ACESSO COM TECLADO MINI ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<p style='text-align: center; margin-bottom: -10px; font-size: 14px; color: gray;'>Senha da Casa</p>", unsafe_allow_html=True)
        
        display = " ● " * len(st.session_state.senha_digitada)
        placeholder = " ○ " * (4 - len(st.session_state.senha_digitada))
        st.markdown(f"<h2 style='text-align: center; letter-spacing: 3px;'>{display}{placeholder}</h2>", unsafe_allow_html=True)

        with st.container():
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                c1, c2, c3 = st.columns(3)
                if c1.button(str(row[0]), key=f"k{row[0]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(row[0]); st.rerun()
                if c2.button(str(row[1]), key=f"k{row[1]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(row[1]); st.rerun()
                if c3.button(str(row[2]), key=f"k{row[2]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(row[2]); st.rerun()

            c_del, c_zero, c_ok = st.columns(3)
            if c_del.button("⌫", key="del", use_container_width=True):
                st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
            if c_zero.button("0", key="k0", use_container_width=True):
                if len(st.session_state.senha_digitada) < 4:
                    st.session_state.senha_digitada += "0"; st.rerun()
            if c_ok.button("OK", type="primary", key="ok", use_container_width=True):
                if st.session_state.senha_digitada == "1234":
                    st.session_state.password = True; st.rerun()
                else:
                    st.error("Incorreta"); st.session_state.senha_digitada = ""
        
        return False
    return True

# --- 3. CONTEÚDO (DASHBOARD) ---
if check_password():
    st.markdown("### Finanças 🏠")
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        st.markdown(f"""
            <div style="background: #1a1a1a; padding: 15px; border-radius: 12px; color: white; margin-bottom: 15px; text-align: center;">
                <h3 style="margin:0;">{formatar_moeda(saldo)}</h3>
            </div>
        """, unsafe_allow_html=True)

    # Sidebar para novos registros
    with st.sidebar:
        st.header("➕ Lançar")
        with st.form("add"):
            t = st.selectbox("Tipo", ["Saída", "Entrada"])
            d = st.text_input("Descrição")
            v = st.number_input("Valor", min_value=0.0)
            c = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Outros"])
            if st.form_submit_button("Salvar", use_container_width=True):
                if d and v > 0:
                    vf = -v if t == "Saída" else v
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": d, "Valor": vf, "Categoria": c, "Tipo": t}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.rerun()

    # Histórico simplificado
    for i, row in df.iloc[::-1].head(10).iterrows():
        cor = "#e63946" if float(row['Valor']) < 0 else "#2a9d8f"
        st.markdown(f"""
            <div style="background:white; padding:8px; border-radius:8px; margin-bottom:5px; border-left: 4px solid {cor}; display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size: 12px;"><b>{row['Descrição']}</b></div>
                <div style="color:{cor}; font-weight:700; font-size:13px;">{formatar_moeda(float(row['Valor']))}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
