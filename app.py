import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E DESIGN SYSTEM ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💳")

# CSS para Teclado 3x3 Compacto e Design Moderno
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* FORÇAR 3 COLUNAS LADO A LADO E REMOVER ESPAÇOS EXCESSIVOS */
    [data-testid="column"] {
        width: calc(33.33% - 5px) !important;
        flex: 1 1 calc(33.33% - 5px) !important;
        min-width: calc(33.33% - 5px) !important;
    }
    
    /* Reduz o espaço (gap) entre as colunas */
    [data-testid="stHorizontalBlock"] {
        gap: 5px !important;
    }

    /* Estilo das Teclas: Menores e mais próximas */
    .stButton > button {
        height: 55px !important;
        border-radius: 12px !important;
        background: white !important;
        border: 1px solid #eee !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: -15px !important; /* Aproxima as linhas verticalmente */
    }

    /* Botão OK e Destaques */
    button[kind="primary"] {
        background: #1a1a1a !important;
        color: white !important;
    }

    .block-container { max-width: 350px !important; padding: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. TECLADO 3x3 COMPACTO ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h3 style='text-align: center; margin-top: 1rem;'>🔒 Senha</h3>", unsafe_allow_html=True)
        
        display = " ● " * len(st.session_state.senha_digitada)
        placeholder = " ○ " * (4 - len(st.session_state.senha_digitada))
        st.markdown(f"<h1 style='text-align: center; letter-spacing: 5px;'>{display}{placeholder}</h1>", unsafe_allow_html=True)

        # Teclado em formato 3x3
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

        # Linha inferior: Apagar, 0, OK
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

# --- 3. DASHBOARD ---
if check_password():
    st.markdown("### Finanças 🏠")
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        # Card de Saldo
        st.markdown(f"""
            <div style="background: #1a1a1a; padding: 20px; border-radius: 20px; color: white; margin-bottom: 20px;">
                <small style="opacity:0.7;">Saldo Geral</small>
                <h2 style="margin:0;">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico Donut Moderno
        df_g = df[df["Valor"] < 0].copy()
        if not df_g.empty:
            fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.7)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=180)
            st.plotly_chart(fig, use_container_width=True)

    # Adicionar (Sidebar)
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

    # Histórico estilo Timeline
    for i, row in df.iloc[::-1].head(10).iterrows():
        cor = "#e63946" if float(row['Valor']) < 0 else "#2a9d8f"
        st.markdown(f"""
            <div style="background:white; padding:10px; border-radius:12px; margin-bottom:8px; border-left: 4px solid {cor}; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:600; font-size:13px;">{row['Descrição']}</div>
                    <small style="color:#aaa; font-size:10px;">{row['Data']}</small>
                </div>
                <div style="color:{cor}; font-weight:700; font-size:14px;">{formatar_moeda(float(row['Valor']))}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
