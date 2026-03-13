import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE UI ESTILO "APP NATIVO" ---
st.set_page_config(page_title="Finanças Casa", layout="centered", page_icon="💸")

st.markdown("""
    <style>
    /* Importando fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000000; }

    /* Forçando o container a parecer um celular */
    .block-container {
        max-width: 400px !important;
        padding: 1.5rem 1rem !important;
        background-color: #000000;
    }

    /* --- TECLADO ULTRA COMPACTO E MODERNO --- */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        margin-bottom: -20px !important; /* Elimina vácuo entre teclas */
    }
    
    [data-testid="column"] { width: 33% !important; flex: 1 1 33% !important; }

    /* Estilo das Teclas: Estilo Dark Minimalista */
    .stButton > button {
        height: 52px !important;
        border-radius: 14px !important;
        background: #1C1C1E !important;
        border: 1px solid #2C2C2E !important;
        color: #FFFFFF !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        transition: 0.2s;
    }
    
    .stButton > button:active {
        background: #3A3A3C !important;
        transform: scale(0.95);
    }

    /* Botão OK em destaque */
    button[kind="primary"] {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: none !important;
    }

    /* Cards de Transação (Estilo Apple Health) */
    .transaction-card {
        background: #1C1C1E;
        padding: 16px;
        border-radius: 18px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #2C2C2E;
    }

    /* Ocultar elementos desnecessários do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. LOGIN COM TECLADO VIRTUAL COMPACTO ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h1 style='text-align: center; color: white; font-weight: 800; font-size: 42px; margin-top: 20px;'></h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8E8E93;'>Insira o código de acesso</p>", unsafe_allow_html=True)
        
        # Display de PIN (Bolinhas)
        pin_html = "".join([f"<div style='width: 15px; height: 15px; border-radius: 50%; background-color: {'#FFFFFF' if i < len(st.session_state.senha_digitada) else '#2C2C2E'}; margin: 0 10px;'></div>" for i in range(4)])
        st.markdown(f"<div style='display: flex; justify-content: center; margin: 30px 0;'>{pin_html}</div>", unsafe_allow_html=True)

        with st.container():
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                c1, c2, c3 = st.columns(3)
                if c1.button(str(row[0]), key=f"k{row[0]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[0]); st.rerun()
                if c2.button(str(row[1]), key=f"k{row[1]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[1]); st.rerun()
                if c3.button(str(row[2]), key=f"k{row[2]}", use_container_width=True):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[2]); st.rerun()

            c1, c2, c3 = st.columns(3)
            if c1.button("⌫", key="del", use_container_width=True):
                st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
            if c2.button("0", key="k0", use_container_width=True):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += "0"; st.rerun()
            if c3.button("OK", type="primary", key="ok", use_container_width=True):
                if st.session_state.senha_digitada == "1234":
                    st.session_state.password = True; st.rerun()
                else:
                    st.toast("Senha incorreta ❌"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. DASHBOARD MODERNO ---
if check_password():
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # Cabeçalho
    st.markdown("<h2 style='color: white; margin-bottom: 0;'>Finanças</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8E8E93;'>Resumo da conta familiar</p>", unsafe_allow_html=True)

    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        # Card de Saldo Estilo Cartão
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2C2C2E 0%, #000000 100%); padding: 25px; border-radius: 24px; border: 1px solid #3A3A3C; margin-bottom: 25px;">
                <small style="color: #8E8E93;">Saldo Disponível</small>
                <h1 style="color: white; margin: 0; font-size: 36px;">{formatar_moeda(saldo)}</h1>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico Donut Minimalista
        df_g = df[df["Valor"] < 0].copy()
        if not df_g.empty:
            fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.75,
                         color_discrete_sequence=["#FFFFFF", "#3A3A3C", "#8E8E93", "#48484A"])
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=180, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    # Botão de Adição (Sidebar ou Floating)
    with st.sidebar:
        st.markdown("### ➕ Novo Lançamento")
        with st.form("add", clear_on_submit=True):
            tipo = st.selectbox("Tipo", ["Saída", "Entrada"])
            desc = st.text_input("O que foi?")
            val = st.number_input("Quanto?", min_value=0.0)
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Saúde", "Outros"])
            if st.form_submit_button("Confirmar Lançamento", use_container_width=True):
                if desc and val > 0:
                    vf = -val if tipo == "Saída" else val
                    novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": desc, "Valor": vf, "Categoria": cat, "Tipo": tipo}])
                    df = pd.concat([df, novo], ignore_index=True)
                    conn.update(data=df)
                    st.toast("Sucesso! ✅"); st.rerun()

    # Timeline de Gastos Estilo iOS
    st.markdown("<p style='color: white; font-weight: 600; margin-top: 20px;'>Atividades Recentes</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(15).iterrows():
        valor = float(row['Valor'])
        cor_valor = "#FFFFFF" if valor > 0 else "#FF453A"
        prefixo = "+" if valor > 0 else ""
        
        st.markdown(f"""
            <div class="transaction-card">
                <div>
                    <div style="color: white; font-weight: 600; font-size: 15px;">{row['Descrição']}</div>
                    <div style="color: #8E8E93; font-size: 12px;">{row['Categoria']} • {row['Data']}</div>
                </div>
                <div style="color: {cor_valor}; font-weight: 600; font-size: 16px;">
                    {prefixo}{formatar_moeda(valor)}
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
