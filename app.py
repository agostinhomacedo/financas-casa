import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE PWA (APP NATIVO) ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💰")

# CSS Avançado: Design System Minimalista e Grid "Inquebrável"
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #000000 !important; 
    }

    /* Remove margens do Streamlit para focar no conteúdo */
    .block-container { 
        max-width: 360px !important; 
        padding: 1rem !important; 
        margin: auto; 
    }

    /* --- TECLADO GRID CSS (Melhor Prática) --- */
    /* Criamos um grid real que ignora o sistema de colunas do Streamlit */
    .num-pad {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        max-width: 280px;
        margin: 0 auto;
    }

    /* Estilização das Teclas Estilo iOS/Glassmorphism */
    .stButton > button {
        width: 100% !important;
        height: 52px !important;
        border-radius: 16px !important;
        background: #1C1C1E !important;
        border: 1px solid #2C2C2E !important;
        color: #FFFFFF !important;
        font-size: 22px !important;
        font-weight: 600 !important;
        transition: all 0.1s ease-in-out;
    }

    .stButton > button:active {
        background: #32D74B !important;
        color: #000 !important;
        transform: scale(0.95);
    }

    /* Botão Primário (OK) */
    button[kind="primary"] {
        background: #32D74B !important;
        color: #000 !important;
        border: none !important;
    }

    /* --- CARDS DE TRANSAÇÃO --- */
    .finance-card {
        background: #151515;
        padding: 14px;
        border-radius: 18px;
        margin-bottom: 8px;
        border-left: 4px solid #32D74B;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Esconde elementos desnecessários */
    header, footer, #MainMenu { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. TECLADO VIRTUAL COM GRID FIXO ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h4 style='text-align: center; color: #8E8E93; margin-top: 30px;'>Código de Acesso</h4>", unsafe_allow_html=True)
        
        # Indicador de PIN Visual
        pins = "".join([f"<span style='font-size: 35px; color: {'#32D74B' if i < len(st.session_state.senha_digitada) else '#2C2C2E'}; margin: 0 10px;'>●</span>" for i in range(4)])
        st.markdown(f"<div style='text-align: center; margin-bottom: 30px;'>{pins}</div>", unsafe_allow_html=True)

        # Teclado usando contêiner para travar o layout
        with st.container():
            # Aqui forçamos o Streamlit a não quebrar as colunas usando o CSS injetado lá em cima
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                c1, c2, c3 = st.columns(3)
                if c1.button(str(row[0]), key=f"k{row[0]}"):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[0]); st.rerun()
                if c2.button(str(row[1]), key=f"k{row[1]}"):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[1]); st.rerun()
                if c3.button(str(row[2]), key=f"k{row[2]}"):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[2]); st.rerun()

            c1, c2, c3 = st.columns(3)
            if c1.button("⌫", key="del"): st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
            if c2.button("0", key="k0"):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += "0"; st.rerun()
            if c3.button("OK", type="primary", key="ok"):
                if st.session_state.senha_digitada == "1234":
                    st.session_state.password = True; st.rerun()
                else:
                    st.toast("Acesso Negado ❌"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. DASHBOARD MOBILE-FIRST ---
if check_password():
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # HEADER DE SALDO (Neo-Bank Style)
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1C1C1E 0%, #000000 100%); padding: 20px; border-radius: 24px; border: 1px solid #32D74B; margin-bottom: 20px;">
                <p style="color: #8E8E93; margin: 0; font-size: 13px; font-weight: 600;">SALDO DISPONÍVEL</p>
                <h2 style="color: #32D74B; margin: 0; font-size: 34px;">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

    # GRÁFICO RESUMIDO (Donut)
    if not df.empty:
        df_g = df[df["Valor"] < 0]
        if not df_g.empty:
            fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.85, 
                         color_discrete_sequence=["#32D74B", "#1C1C1E", "#444", "#8E8E93"])
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=140, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    # LANÇAMENTO RÁPIDO (SIDEBAR)
    with st.sidebar:
        st.markdown("### ➕ Lançar")
        with st.form("f", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída", "Entrada"], horizontal=True)
            desc = st.text_input("O que foi?")
            val = st.number_input("Quanto?", min_value=0.0)
            if st.form_submit_button("Confirmar", use_container_width=True):
                if desc and val > 0:
                    v = -val if tipo == "Saída" else val
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Descrição": desc, "Valor": v, "Categoria": "Geral", "Tipo": tipo}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.toast("Registrado! ✅"); st.rerun()

    # LISTA DE MOVIMENTAÇÕES (CARDS)
    st.markdown("<p style='font-size: 12px; color: #444; font-weight: 800; letter-spacing: 1px;'>ATIVIDADE RECENTE</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(10).iterrows():
        v = float(row['Valor'])
        cor_v = "#32D74B" if v > 0 else "#FF453A"
        
        st.markdown(f"""
            <div class="finance-card" style="border-left-color: {cor_v};">
                <div>
                    <div style="color: white; font-weight: 600; font-size: 15px;">{row['Descrição']}</div>
                    <div style="color: #444; font-size: 11px; font-weight: 600;">{row['Data']}</div>
                </div>
                <div style="color: {cor_v}; font-weight: 800; font-size: 16px;">
                    {formatar_moeda(v)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"r_{i}"):
            df = df.drop(i); conn.update(data=df); st.rerun()
