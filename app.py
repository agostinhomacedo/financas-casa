import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E CSS PARA TRAVAR O LAYOUT 3x3 ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💳")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* --- FORÇA 3 COLUNAS NA VERTICAL (MOBILE) --- */
    /* Este bloco impede que o Streamlit empilhe os botões no celular */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important; /* Espaçamento lateral mínimo */
        margin-bottom: -18px !important; /* "Cola" as linhas verticalmente */
    }
    
    [data-testid="column"] {
        width: 33.33% !important;
        flex: 1 1 33.33% !important;
        min-width: 33.33% !important;
    }

    /* Estilo das Teclas: Compactas e Quadradas */
    .stButton > button {
        height: 50px !important;
        border-radius: 10px !important;
        background: white !important;
        border: 1px solid #ddd !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        padding: 0px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Botão OK e Controles */
    button[kind="primary"] {
        background: #1a1a1a !important;
        color: white !important;
    }

    /* Centraliza e limita a largura do teclado no smartphone */
    .block-container { 
        max-width: 340px !important; 
        padding-top: 2rem !important;
        margin: auto;
    }

    /* Ajuste para o texto de erro não deslocar o teclado */
    .stAlert { margin-top: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. ACESSO COM TECLADO 3x3 TRAVADO ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h4 style='text-align: center; margin-bottom: 0;'>🔒 Acesso</h4>", unsafe_allow_html=True)
        
        # Display de bolinhas
        display = " ● " * len(st.session_state.senha_digitada)
        placeholder = " ○ " * (4 - len(st.session_state.senha_digitada))
        st.markdown(f"<h1 style='text-align: center; letter-spacing: 5px; margin-bottom: 25px;'>{display}{placeholder}</h1>", unsafe_allow_html=True)

        with st.container():
            # Linhas de números (Forçadas a 3 colunas)
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

            # Linha final de controles
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
                    st.error("Senha Incorreta")
                    st.session_state.senha_digitada = ""
        
        return False
    return True

# --- 3. DASHBOARD (SOMENTE APÓS LOGIN) ---
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
            <div style="background: #1a1a1a; padding: 15px; border-radius: 15px; color: white; margin-bottom: 20px; text-align: center;">
                <small style="opacity:0.7;">Saldo Total</small>
                <h2 style="margin:0;">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

    # Sidebar para novos registros
    with st.sidebar:
        st.header("➕ Lançar")
        with st.form("add"):
            t = st.selectbox("Tipo", ["Saída", "Entrada"])
            d = st.text_input("O que?")
            v = st.number_input("Valor", min_value=0.0)
            c = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Outros"])
            if st.form_submit_button("Salvar Registro", use_container_width=True):
                if d and v > 0:
                    vf = -v if t == "Saída" else v
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": d, "Valor": vf, "Categoria": c, "Tipo": t}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.rerun()

    # Histórico estilo Timeline
    for i, row in df.iloc[::-1].head(10).iterrows():
        cor = "#e63946" if float(row['Valor']) < 0 else "#2a9d8f"
        st.markdown(f"""
            <div style="background:white; padding:10px; border-radius:12px; margin-bottom:8px; border-left: 4px solid {cor}; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size: 13px;"><b>{row['Descrição']}</b></div>
                    <small style="color:gray; font-size:10px;">{row['Data']} • {row['Categoria']}</small>
                </div>
                <div style="color:{cor}; font-weight:700; font-size:14px;">{formatar_moeda(float(row['Valor']))}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
