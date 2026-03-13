import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E CSS AVANÇADO ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💰")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* --- AJUSTE DO TECLADO (3x3 ULTRA COMPACTO) --- */
    .teclado-container [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 4px !important; /* Espaço mínimo entre teclas */
        margin-bottom: -18px !important; /* "Cola" as linhas verticalmente */
    }
    
    .teclado-container [data-testid="column"] {
        width: 100% !important;
        min-width: 0px !important;
        flex: 1 1 0% !important;
    }

    .stButton > button {
        height: 50px !important;
        border-radius: 10px !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        background: white !important;
        border: 1px solid #eee !important;
    }

    /* Botão OK */
    button[kind="primary"] {
        background: #007AFF !important;
        color: white !important;
    }

    /* --- RESPONSIVIDADE DO CONTEÚDO --- */
    /* Quando logado, permitimos que o app use mais largura para não cortar o título */
    .main-app-container {
        max-width: 100% !important;
    }
    
    /* Quando na tela de login, estreitamos para o teclado ficar bonito */
    .login-container {
        max-width: 320px !important;
        margin: auto;
    }

    /* Estilo dos Cards de extrato */
    .finance-card {
        background: white;
        padding: 12px;
        border-radius: 15px;
        margin-bottom: 8px;
        border: 1px solid #f0f0f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. TELA DE ACESSO (PIN) ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Acesso Restrito</h3>", unsafe_allow_html=True)
        
        # PIN display
        dots = "".join([f"<span style='font-size: 30px; color: {'#007AFF' if i < len(st.session_state.senha_digitada) else '#DDD'}; margin: 0 5px;'>●</span>" for i in range(4)])
        st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'>{dots}</div>", unsafe_allow_html=True)

        st.markdown('<div class="teclado-container">', unsafe_allow_html=True)
        # Teclado 3x3
        for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            c1, c2, c3 = st.columns(3)
            if c1.button(str(row[0]), key=f"k{row[0]}"):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[0]); st.rerun()
            if c2.button(str(row[1]), key=f"k{row[1]}"):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[1]); st.rerun()
            if c3.button(str(row[2]), key=f"k{row[2]}"):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[2]); st.rerun()

        c_del, c_zero, c_ok = st.columns(3)
        if c_del.button("⌫", key="del"): st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
        if c_zero.button("0", key="k0"):
            if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += "0"; st.rerun()
        if c_ok.button("OK", type="primary", key="ok"):
            if st.session_state.senha_digitada == "1234":
                st.session_state.password = True; st.rerun()
            else:
                st.error("Senha Incorreta"); st.session_state.senha_digitada = ""
        st.markdown('</div></div>', unsafe_allow_html=True)
        return False
    return True

# --- 3. CONTEÚDO PRINCIPAL ---
if check_password():
    st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
    st.title("🏠 Minha Casa Finanças")
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        # Card de Saldo
        st.markdown(f"""
            <div style="background: #007AFF; padding: 20px; border-radius: 20px; color: white; margin-bottom: 25px;">
                <small style="opacity: 0.8;">Saldo Total</small>
                <h2 style="margin: 0;">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico Donut
        df_g = df[df["Valor"] < 0].copy()
        if not df_g.empty:
            st.subheader("🍕 Gastos por Categoria")
            fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.6)
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

    # Sidebar para novos registros
    with st.sidebar:
        st.header("➕ Lançar")
        with st.form("add"):
            t = st.selectbox("Tipo", ["Saída", "Entrada"])
            d = st.text_input("Descrição")
            v = st.number_input("Valor", min_value=0.0)
            c = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Outros"])
            if st.form_submit_button("Salvar Registro", use_container_width=True):
                if d and v > 0:
                    vf = -v if t == "Saída" else v
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": d, "Valor": vf, "Categoria": c, "Tipo": t}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.rerun()

    # Histórico
    st.markdown("<br><b>Atividade Recente</b>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(10).iterrows():
        cor = "#FF3B30" if float(row['Valor']) < 0 else "#34C759"
        st.markdown(f"""
            <div class="finance-card">
                <div>
                    <div style="font-weight: 600; font-size: 14px;">{row['Descrição']}</div>
                    <small style="color: #999;">{row['Data']} • {row['Categoria']}</small>
                </div>
                <div style="color: {cor}; font-weight: 700;">{formatar_moeda(float(row['Valor']))}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
