import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE ALTA PERFORMANCE ---
st.set_page_config(page_title="Finanças", layout="centered", page_icon="💸")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #000; color: white; }

    /* Ajuste de Container para Celulares Estreitos */
    .block-container { max-width: 360px !important; padding: 0.5rem !important; }

    /* --- TECLADO GHOST DESIGN (COMPACTO) --- */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 4px !important;
        margin-bottom: -22px !important;
    }
    
    [data-testid="column"] { width: 33% !important; flex: 1 1 33% !important; }

    .stButton > button {
        height: 48px !important;
        border-radius: 12px !important;
        background: #121212 !important;
        border: 1px solid #222 !important;
        color: #fff !important;
        font-size: 1.2rem !important;
        transition: 0.1s;
    }
    
    .stButton > button:active { background: #333 !important; }
    
    /* Botão de confirmação com cor vibrante */
    button[kind="primary"] { background: #34C759 !important; color: black !important; border: none !important; }

    /* Estilo de Cartões de Transação */
    .card {
        background: #111;
        padding: 10px 15px;
        border-radius: 12px;
        border-left: 4px solid #333;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Esconde elementos nativos que ocupam espaço */
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. ACESSO BIOMÉTRICO SIMULADO (TECLADO) ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h4 style='text-align: center; margin-top: 2rem;'>Digite o PIN</h4>", unsafe_allow_html=True)
        
        # Indicador de PIN
        pins = "".join([f"<span style='font-size: 30px; margin: 0 8px; color: {'#34C759' if i < len(st.session_state.senha_digitada) else '#333'};'>●</span>" for i in range(4)])
        st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'>{pins}</div>", unsafe_allow_html=True)

        with st.container():
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                c1, c2, c3 = st.columns(3)
                if c1.button(str(row[0]), key=f"k{row[0]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[0]); st.rerun()
                if c2.button(str(row[1]), key=f"k{row[1]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[1]); st.rerun()
                if c3.button(str(row[2]), key=f"k{row[2]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[2]); st.rerun()

            c_del, c_zero, c_ok = st.columns(3)
            if c_del.button("⌫", key="del", use_container_width=True):
                st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
            if c_zero.button("0", key="k0", use_container_width=True):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += "0"; st.rerun()
            if c_ok.button("OK", type="primary", key="ok", use_container_width=True):
                if st.session_state.senha_digitada == "1234":
                    st.session_state.password = True; st.rerun()
                else:
                    st.toast("Senha Errada!"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. INTERFACE PRINCIPAL ---
if check_password():
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # SALDO FLUTUANTE
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        st.markdown(f"""
            <div style="background: #111; padding: 15px; border-radius: 20px; border: 1px solid #222; margin-bottom: 15px;">
                <p style="color: #666; margin: 0; font-size: 12px;">Saldo Atual</p>
                <h2 style="margin: 0; color: {'#34C759' if saldo >= 0 else '#FF453A'};">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

    # GRÁFICOS EM ABAS MINI
    if not df.empty:
        t1, t2 = st.tabs(["Categorias", "Histórico"])
        with t1:
            df_g = df[df["Valor"] < 0]
            if not df_g.empty:
                fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.8)
                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=150, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        with t2:
            st.bar_chart(df.tail(5), x="Data", y="Valor", color="Tipo", height=150)

    # MENU DE ADIÇÃO (SIDEBAR)
    with st.sidebar:
        st.markdown("### ➕ Lançamento")
        with st.form("f", clear_on_submit=True):
            tipo = st.radio("Operação", ["Saída", "Entrada"], horizontal=True)
            desc = st.text_input("Título")
            val = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Confirmar", use_container_width=True):
                if desc and val > 0:
                    v = -val if tipo == "Saída" else val
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Descrição": desc, "Valor": v, "Categoria": "Geral", "Tipo": tipo}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.rerun()

    # TIMELINE MINIMALISTA
    st.markdown("<p style='font-size: 12px; color: #666; font-weight: bold;'>ÚLTIMAS MOVIMENTAÇÕES</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(15).iterrows():
        v = float(row['Valor'])
        cor = "#34C759" if v > 0 else "#FF453A"
        
        st.markdown(f"""
            <div class="card" style="border-left-color: {cor};">
                <div>
                    <span style="font-size: 14px; font-weight: bold;">{row['Descrição']}</span><br>
                    <span style="font-size: 10px; color: #666;">{row['Data']}</span>
                </div>
                <div style="color: {cor}; font-weight: bold; font-size: 14px;">
                    {formatar_moeda(v)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"r_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
