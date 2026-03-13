import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE UI MOBILE-FIRST ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💰")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #000000 !important; 
    }

    /* Limita a largura do app para o teclado não espalhar */
    .block-container {
        max-width: 340px !important;
        padding: 0.5rem !important;
        margin: auto;
    }

    /* --- TECLADO COMPACTO E ACHATADO --- */
    /* Remove o espaço entre colunas e linhas */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 6px !important;
        margin-bottom: -22px !important; 
    }
    
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }

    /* Ajuste fino dos botões: Menores na vertical */
    .stButton > button {
        height: 42px !important; /* Altura reduzida para não ficar gigante */
        border-radius: 10px !important;
        background: #1C1C1E !important;
        border: 1px solid #333 !important;
        color: #FFFFFF !important;
        font-size: 18px !important;
        padding: 0px !important;
        font-weight: 600 !important;
    }
    
    /* Botão OK (Verde vibrante) */
    button[kind="primary"] {
        background: #32D74B !important;
        color: #000 !important;
        border: none !important;
    }

    /* --- ESTILO DOS LANÇAMENTOS (ALTO CONTRASTE) --- */
    .finance-card {
        background: #111;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 6px;
        border: 1px solid #222;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .card-txt { color: #FFFFFF !important; font-size: 14px; font-weight: 600; }
    .card-sub { color: #888 !important; font-size: 11px; }

    /* Esconde cabeçalho e menu para ganhar tela */
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. LOGIN (TECLADO ACHATADO) ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<p style='text-align: center; color: #888; margin-top: 10px;'>Acesso Restrito</p>", unsafe_allow_html=True)
        
        # PIN Visual
        pins = "".join([f"<span style='font-size: 25px; color: {'#32D74B' if i < len(st.session_state.senha_digitada) else '#222'}; margin: 0 6px;'>●</span>" for i in range(4)])
        st.markdown(f"<div style='text-align: center; margin-bottom: 15px;'>{pins}</div>", unsafe_allow_html=True)

        with st.container():
            # Linhas 1-9
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                c1, c2, c3 = st.columns(3)
                if c1.button(str(row[0]), key=f"k{row[0]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[0]); st.rerun()
                if c2.button(str(row[1]), key=f"k{row[1]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[1]); st.rerun()
                if c3.button(str(row[2]), key=f"k{row[2]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[2]); st.rerun()

            # Linha Final
            c_del, c_zero, c_ok = st.columns(3)
            if c_del.button("⌫", key="del", use_container_width=True):
                st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
            if c_zero.button("0", key="k0", use_container_width=True):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += "0"; st.rerun()
            if c_ok.button("OK", type="primary", key="ok", use_container_width=True):
                if st.session_state.senha_digitada == "1234":
                    st.session_state.password = True; st.rerun()
                else:
                    st.toast("PIN Incorreto!"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. DASHBOARD ---
if check_password():
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # SALDO
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        st.markdown(f"""
            <div style="background: #111; padding: 15px; border-radius: 15px; border: 1px solid #32D74B; margin-bottom: 10px; text-align: center;">
                <p style="color: #888; margin: 0; font-size: 11px;">DISPONÍVEL</p>
                <h2 style="color: #32D74B; margin: 0; font-size: 28px;">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

    # GRÁFICO (REDUZIDO)
    if not df.empty:
        df_g = df[df["Valor"] < 0]
        if not df_g.empty:
            fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.85)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=130, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    # NOVO LANÇAMENTO (SIDEBAR)
    with st.sidebar:
        st.header("➕ Lançar")
        with st.form("f", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída", "Entrada"], horizontal=True)
            desc = st.text_input("Descrição")
            val = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Confirmar"):
                if desc and val > 0:
                    v = -val if tipo == "Saída" else val
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Descrição": desc, "Valor": v, "Categoria": "Geral", "Tipo": tipo}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.rerun()

    # LISTA DE MOVIMENTAÇÕES
    st.markdown("<p style='font-size: 11px; color: #555; font-weight: bold; margin-top: 5px;'>HISTÓRICO</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(15).iterrows():
        v = float(row['Valor'])
        cor_v = "#34C759" if v > 0 else "#FF453A"
        st.markdown(f"""
            <div class="finance-card">
                <div>
                    <div class="card-txt">{row['Descrição']}</div>
                    <div class="card-sub">{row['Data']}</div>
                </div>
                <div style="color: {cor_v}; font-weight: bold; font-size: 14px;">{formatar_moeda(v)}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_{i}"):
            df = df.drop(i); conn.update(data=df); st.rerun()
