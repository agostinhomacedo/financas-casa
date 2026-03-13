import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E UI/UX AVANÇADA ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💳")

# CSS para forçar o layout de calculadora e estilo Glassmorphism
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Forçar colunas lado a lado no Mobile */
    [data-testid="column"] {
        width: calc(33.3333% - 1rem) !important;
        flex: 1 1 calc(33.3333% - 1rem) !important;
        min-width: calc(33.3333% - 1rem) !important;
    }

    /* Estilo das Teclas (Menores e Elegantes) */
    .stButton > button {
        height: 50px !important;
        width: 100% !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #1a1a1a !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 0px;
    }

    /* Botão OK de Destaque */
    button[kind="primary"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #434343 100%) !important;
        color: white !important;
        border: none !important;
    }

    /* Ajuste de Espaçamento Geral */
    .block-container {
        max-width: 380px !important;
        padding: 1rem !important;
    }
    
    .finance-card {
        background: white;
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. TECLADO MODELO CALCULADORA ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h3 style='text-align: center; margin-top: 2rem;'>🔒 Acesso</h3>", unsafe_allow_html=True)
        
        # Display de Senha
        display = " ● " * len(st.session_state.senha_digitada)
        placeholder = " ○ " * (4 - len(st.session_state.senha_digitada))
        st.markdown(f"<h1 style='text-align: center; letter-spacing: 5px;'>{display}{placeholder}</h1>", unsafe_allow_html=True)

        # Teclado (Forçando o grid 3x3)
        container_teclado = st.container()
        with container_teclado:
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                c1, c2, c3 = st.columns(3)
                if c1.button(str(row[0]), key=f"k{row[0]}"):
                    if len(st.session_state.senha_digitada) < 4: 
                        st.session_state.senha_digitada += str(row[0]); st.rerun()
                if c2.button(str(row[1]), key=f"k{row[1]}"):
                    if len(st.session_state.senha_digitada) < 4: 
                        st.session_state.senha_digitada += str(row[1]); st.rerun()
                if c3.button(str(row[2]), key=f"k{row[2]}"):
                    if len(st.session_state.senha_digitada) < 4: 
                        st.session_state.senha_digitada += str(row[2]); st.rerun()

            c1, c2, c3 = st.columns(3)
            if c1.button("⌫", key="del"): 
                st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
            if c2.button("0", key="k0"):
                if len(st.session_state.senha_digitada) < 4: 
                    st.session_state.senha_digitada += "0"; st.rerun()
            if c3.button("OK", type="primary", key="ok"):
                if st.session_state.senha_digitada == "1234": # <--- SUA SENHA
                    st.session_state.password = True; st.rerun()
                else:
                    st.error("Senha Incorreta"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. CONTEÚDO PRINCIPAL ---
if check_password():
    st.markdown("### Olá, Família 👋")
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # Saldo Estilo Premium
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        st.markdown(f"""
            <div style="background: #1a1a1a; padding: 25px; border-radius: 28px; color: white; margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.15);">
                <small style="opacity:0.6;">Saldo Disponível</small>
                <h1 style="margin:0; font-size: 32px;">{formatar_moeda(saldo)}</h1>
            </div>
        """, unsafe_allow_html=True)

        # Gráficos em Abas Modernas
        tab1, tab2 = st.tabs(["🎯 Gastos", "📈 Tendência"])
        with tab1:
            df_g = df[df["Valor"] < 0].copy()
            if not df_g.empty:
                fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.7,
                             color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=220)
                st.plotly_chart(fig, use_container_width=True)
        with tab2:
            fig_b = px.bar(df, x="Data", y="Valor", color="Tipo", barmode="group",
                           color_discrete_map={"Saída (Gasto)": "#ff4d4d", "Entrada (Ganho)": "#00cc66"})
            fig_b.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=200, showlegend=False)
            st.plotly_chart(fig_b, use_container_width=True)

    # Botão de Cadastro (Sidebar)
    with st.sidebar:
        st.markdown("### ➕ Lançamento")
        with st.form("add_new"):
            t = st.selectbox("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
            d = st.text_input("O que foi?")
            v = st.number_input("Quanto?", min_value=0.0)
            c = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Saúde", "Outros"])
            if st.form_submit_button("Registrar", use_container_width=True):
                if d and v > 0:
                    vf = -v if t == "Saída (Gasto)" else v
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": d, "Valor": vf, "Categoria": c, "Tipo": t}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.toast("Sucesso!"); st.rerun()

    # Timeline de Gastos
    st.markdown("<br><b>Movimentações</b>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(10).iterrows():
        v_num = float(row['Valor'])
        cor = "#e63946" if v_num < 0 else "#2a9d8f"
        st.markdown(f"""
            <div class="finance-card">
                <div>
                    <div style="font-weight:600; font-size:14px; color:#1a1a1a;">{row['Descrição']}</div>
                    <small style="color:#aaa;">{row['Categoria']} • {row['Data']}</small>
                </div>
                <div style="color:{cor}; font-weight:700;">{formatar_moeda(v_num)}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
