import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE UI ULTRA-COMPACTA ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💰")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #000000 !important; 
    }

    /* Ajuste do container principal para não criar rolagem desnecessária */
    .block-container {
        max-width: 400px !important;
        padding: 0.5rem !important;
        margin: auto;
    }

    /* --- TECLADO COMPACTO (REDUZIDO) --- */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
        margin-bottom: -22px !important; /* "Cola" as linhas para o teclado ficar baixo */
    }
    
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }

    /* Botões do Teclado: Menores e com mais brilho */
    .stButton > button {
        height: 45px !important; /* Altura reduzida para caber na tela */
        border-radius: 12px !important;
        background: #1C1C1E !important;
        border: 1px solid #3A3A3C !important;
        color: #FFFFFF !important;
        font-size: 18px !important;
        padding: 0px !important;
    }
    
    /* Botão OK em destaque */
    button[kind="primary"] {
        background: #32D74B !important;
        color: #000 !important;
        font-weight: 700 !important;
    }

    /* --- CORES DOS LANÇAMENTOS (ALTO CONTRASTE) --- */
    .finance-card {
        background: #1C1C1E;
        padding: 12px;
        border-radius: 15px;
        margin-bottom: 8px;
        border: 1px solid #3A3A3C;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Texto dentro dos cards - Branco Puro para leitura fácil */
    .card-title { color: #FFFFFF; font-weight: 600; font-size: 14px; }
    .card-sub { color: #A1A1AA; font-size: 11px; }
    
    /* Esconde elementos poluídos */
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. ACESSO COM PIN ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h4 style='text-align: center; color: white; margin-top: 20px;'>Digite o PIN</h4>", unsafe_allow_html=True)
        
        # Display de PIN (Bolinhas)
        pins = "".join([f"<div style='width:10px; height:10px; border-radius:50%; background:{'#32D74B' if i < len(st.session_state.senha_digitada) else '#333'}; margin:0 6px;'></div>" for i in range(4)])
        st.markdown(f"<div style='display:flex; justify-content:center; margin:20px 0;'>{pins}</div>", unsafe_allow_html=True)

        # Teclado 3x3
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
                    st.toast("Incorreta!"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. DASHBOARD ---
if check_password():
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # Saldo principal
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        st.markdown(f"""
            <div style="background: #1C1C1E; padding: 20px; border-radius: 20px; border: 1px solid #32D74B; margin-bottom: 15px; text-align: center;">
                <p style="color: #A1A1AA; margin: 0; font-size: 12px;">Saldo da Casa</p>
                <h2 style="color: #32D74B; margin: 0;">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico Compacto em Abas
    if not df.empty:
        t1, t2 = st.tabs(["Pizza", "Fluxo"])
        with t1:
            df_g = df[df["Valor"] < 0]
            if not df_g.empty:
                fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.7)
                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=140, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        with t2:
            st.bar_chart(df.tail(5), x="Data", y="Valor", color="Tipo", height=140)

    # Novo Registro na Sidebar
    with st.sidebar:
        st.header("➕ Lançar")
        with st.form("f", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída", "Entrada"], horizontal=True)
            desc = st.text_input("O que é?")
            val = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Salvar", use_container_width=True):
                if desc and val > 0:
                    v = -val if tipo == "Saída" else val
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Descrição": desc, "Valor": v, "Categoria": "Geral", "Tipo": tipo}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.rerun()

    # Histórico de Lançamentos (ALTO CONTRASTE)
    st.markdown("<p style='font-size: 12px; color: #A1A1AA; font-weight: bold; margin-top: 15px;'>MOVIMENTAÇÕES</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(10).iterrows():
        v = float(row['Valor'])
        cor_v = "#32D74B" if v > 0 else "#FF453A"
        
        st.markdown(f"""
            <div class="finance-card">
                <div>
                    <div class="card-title">{row['Descrição']}</div>
                    <div class="card-sub">{row['Data']}</div>
                </div>
                <div style="color: {cor_v}; font-weight: bold; font-size: 14px;">
                    {formatar_moeda(v)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"r_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
