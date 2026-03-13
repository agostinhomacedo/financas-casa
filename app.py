import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE UI/UX DE ALTA PERFORMANCE ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💳")

# Injeção de CSS para recriar a interface de um App Nativo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #000000 !important; 
        color: #FFFFFF !important;
    }

    /* Trava o container para parecer um smartphone no Desktop também */
    .block-container {
        max-width: 400px !important;
        padding: 1rem !important;
    }

    /* --- TECLADO VIRTUAL INQUEBRÁVEL 3x3 --- */
    /* Esta regra força os botões a ficarem lado a lado mesmo em telas minúsculas */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
        margin-bottom: -15px !important;
    }
    
    div[data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }

    /* Design das Teclas (Glassmorphism Dark) */
    .stButton > button {
        height: 55px !important;
        border-radius: 16px !important;
        background: rgba(28, 28, 30, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        font-size: 22px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px);
        transition: 0.2s;
    }
    
    .stButton > button:active {
        background: #32D74B !important; /* Verde Neon ao tocar */
        color: #000 !important;
    }

    /* Botão OK (Ação Principal) */
    button[kind="primary"] {
        background: #32D74B !important;
        color: #000 !important;
        border: none !important;
        font-weight: 800 !important;
    }

    /* Cards de Transação Estilo Neo-Bank */
    .finance-card {
        background: #1C1C1E;
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 10px;
        border: 1px solid #2C2C2E;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Esconde elementos poluídos do Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. LOGIN COM PIN (TECLADO VIRTUAL COMPACTO) ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🏦</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8E8E93;'>Digite seu PIN de acesso</p>", unsafe_allow_html=True)
        
        # Display de PIN Dinâmico
        pins = "".join([f"<div style='width:12px; height:12px; border-radius:50%; background:{'#32D74B' if i < len(st.session_state.senha_digitada) else '#2C2C2E'}; margin:0 8px;'></div>" for i in range(4)])
        st.markdown(f"<div style='display:flex; justify-content:center; margin:30px 0;'>{pins}</div>", unsafe_allow_html=True)

        # Renderização do Teclado 3x3
        with st.container():
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                cols = st.columns(3)
                for i, num in enumerate(row):
                    if cols[i].button(str(num), key=f"k{num}", use_container_width=True):
                        if len(st.session_state.senha_digitada) < 4:
                            st.session_state.senha_digitada += str(num); st.rerun()

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
                    st.toast("Senha Incorreta ❌"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. DASHBOARD PREMIUM (APÓS LOGIN) ---
if check_password():
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # Saldo com Estilo de Cartão de Crédito Black
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1C1C1E 0%, #000000 100%); padding: 25px; border-radius: 24px; border: 1px solid #32D74B; margin-bottom: 25px;">
                <small style="color: #8E8E93;">Saldo Disponível</small>
                <h1 style="color: #32D74B; margin: 0; font-size: 38px;">{formatar_moeda(saldo)}</h1>
                <div style="margin-top: 15px; font-size: 10px; color: #444;">DATA SYNC: {datetime.now().strftime('%H:%M:%S')}</div>
            </div>
        """, unsafe_allow_html=True)

        # Insights Rápidos (Gráfico Donut Minimalista)
        df_g = df[df["Valor"] < 0].copy()
        if not df_g.empty:
            fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.8,
                         color_discrete_sequence=["#32D74B", "#1C1C1E", "#444", "#8E8E93"])
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=180, 
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    # Botão de Ação Flutuante (Add via Sidebar)
    with st.sidebar:
        st.markdown("### ⚡ Nova Transação")
        with st.form("add_form", clear_on_submit=True):
            tipo = st.radio("Operação", ["Saída", "Entrada"], horizontal=True)
            desc = st.text_input("Título", placeholder="Ex: Aluguel")
            val = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Confirmar", use_container_width=True):
                if desc and val > 0:
                    v_final = -val if tipo == "Saída" else val
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": desc, "Valor": v_final, "Categoria": "Geral", "Tipo": tipo}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.toast("Transação Salva! ✅"); st.rerun()

    # Timeline de Movimentações (Estilo Extrato Moderno)
    st.markdown("<p style='color: #8E8E93; font-weight: 600; font-size: 12px; letter-spacing: 1px;'>ATIVIDADE RECENTE</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(10).iterrows():
        v = float(row['Valor'])
        cor_v = "#32D74B" if v > 0 else "#FF453A"
        
        st.markdown(f"""
            <div class="finance-card">
                <div>
                    <div style="font-weight: 600; font-size: 14px;">{row['Descrição']}</div>
                    <small style="color: #8E8E93; font-size: 11px;">{row['Data']}</small>
                </div>
                <div style="color: {cor_v}; font-weight: 700; font-size: 15px;">
                    {formatar_moeda(v)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"r_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
