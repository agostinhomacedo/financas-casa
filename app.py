import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E DESIGN SYSTEM ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="📊")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .block-container { max-width: 400px !important; padding: 1rem !important; }
    
    /* Botões do Teclado */
    .stButton > button {
        height: 48px !important;
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        font-weight: 600 !important;
    }
    button[kind="primary"] { background: #1a1a1a !important; color: white !important; }

    /* Cards */
    .finance-card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. ACESSO ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h2 style='text-align: center;'>🔐</h2>", unsafe_allow_html=True)
        display = " ● " * len(st.session_state.senha_digitada)
        placeholder = " ○ " * (4 - len(st.session_state.senha_digitada))
        st.markdown(f"<h1 style='text-align: center; letter-spacing: 8px;'>{display}{placeholder}</h1>", unsafe_allow_html=True)

        _, col_key, _ = st.columns([0.05, 0.9, 0.05])
        with col_key:
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
                if st.session_state.senha_digitada == "1234": st.session_state.password = True; st.rerun()
                else: st.error("Incorreta"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. CONTEÚDO COM GRÁFICOS ---
if check_password():
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # Cartão de Saldo Principal
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        st.markdown(f"""
            <div style="background: #1a1a1a; padding: 20px; border-radius: 20px; color: white; margin-bottom: 20px;">
                <small style="opacity:0.7;">Saldo da Casa</small>
                <h2 style="margin:0;">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

        # --- SEÇÃO DE GRÁFICOS (INSETS) ---
        df_gastos = df[df["Valor"] < 0].copy()
        if not df_gastos.empty:
            tab1, tab2 = st.tabs(["🍕 Categorias", "📊 Fluxo"])
            
            with tab1:
                fig_pie = px.pie(
                    df_gastos, values=df_gastos["Valor"].abs(), names='Categoria',
                    hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with tab2:
                # Gráfico de barras simples por dia/mês
                fig_bar = px.bar(
                    df, x="Data", y="Valor", color="Tipo",
                    color_discrete_map={"Saída (Gasto)": "#e63946", "Entrada (Ganho)": "#2a9d8f"}
                )
                fig_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False, height=200)
                st.plotly_chart(fig_bar, use_container_width=True)

    # Botão de Adicionar (Sidebar)
    with st.sidebar:
        st.header("⚡ Novo")
        with st.form("add"):
            tipo = st.selectbox("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Descrição")
            val = st.number_input("Valor", min_value=0.0)
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Saúde", "Outros"])
            if st.form_submit_button("Confirmar", use_container_width=True):
                if desc and val > 0:
                    v_final = -val if tipo == "Saída (Gasto)" else val
                    novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": desc, "Valor": v_final, "Categoria": cat, "Tipo": tipo}])
                    df = pd.concat([df, novo], ignore_index=True)
                    conn.update(data=df)
                    st.toast("Salvo!"); st.rerun()

    # Histórico
    st.markdown("<p style='font-weight:600; margin-top:15px;'>Movimentações</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].iterrows():
        cor = "#e63946" if float(row['Valor']) < 0 else "#2a9d8f"
        st.markdown(f"""
            <div class="finance-card">
                <div>
                    <small style="color:#888; font-size:10px;">{row['Data']}</small>
                    <div style="font-weight:600; font-size:14px;">{row['Descrição']}</div>
                </div>
                <div style="color:{cor}; font-weight:600;">{formatar_moeda(float(row['Valor']))}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"d_{i}"):
            df = df.drop(i)
            conn.update(data=df)
            st.rerun()
