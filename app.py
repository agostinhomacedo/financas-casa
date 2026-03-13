import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E DESIGN SYSTEM ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💳")

# Injeção de CSS para Design Moderno e Responsivo
st.markdown("""
    <style>
    /* Importando fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Fundo Gradiente Suave */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Container Principal Estilo Mobile */
    .block-container {
        max-width: 400px !important;
        padding: 1.5rem 1rem !important;
    }

    /* Teclado Virtual Compacto */
    .stButton > button {
        height: 50px !important;
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        transition: all 0.2s ease;
        font-weight: 600 !important;
        color: #1a1a1a !important;
    }
    
    .stButton > button:hover {
        background: #ffffff !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Botão Primário (Entrar/Salvar) */
    button[kind="primary"] {
        background: #1a1a1a !important;
        color: white !important;
        border: none !important;
    }

    /* Cards de Histórico (Glassmorphism) */
    .finance-card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 15px;
        margin-bottom: 12px;
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

# --- 2. ACESSO COM TECLADO COMPACTO ---
def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if "senha_digitada" not in st.session_state:
        st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🔐</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Digite sua senha</p>", unsafe_allow_html=True)
        
        # Display de bolinhas elegante
        display = " ● " * len(st.session_state.senha_digitada)
        placeholder = " ○ " * (4 - len(st.session_state.senha_digitada))
        st.markdown(f"<h1 style='text-align: center; letter-spacing: 8px; color: #1a1a1a;'>{display}{placeholder}</h1>", unsafe_allow_html=True)

        # Teclado reduzido para smartphone
        _, col_key, _ = st.columns([0.05, 0.9, 0.05])
        with col_key:
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

            c1, c2, c3 = st.columns(3)
            if c1.button("⌫", key="del", use_container_width=True):
                st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
            if c2.button("0", key="k0", use_container_width=True):
                if len(st.session_state.senha_digitada) < 4:
                    st.session_state.senha_digitada += "0"; st.rerun()
            if c3.button("OK", type="primary", key="ok", use_container_width=True):
                if st.session_state.senha_digitada == "1234":
                    st.session_state.password = True; st.rerun()
                else:
                    st.error("Senha incorreta"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. DASHBOARD ATUALIZADO ---
if check_password():
    st.markdown("<h4 style='margin-bottom: 20px;'>Olá, Família 👋</h4>", unsafe_allow_html=True)
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # Resumo com Design de Cartão de Crédito
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        cor_saldo = "#1a1a1a" if saldo >= 0 else "#e63946"
        
        st.markdown(f"""
            <div style="background: #1a1a1a; padding: 25px; border-radius: 24px; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
                <small style="opacity: 0.7;">Saldo Total em conta</small>
                <h1 style="margin: 0; font-size: 32px;">{formatar_moeda(saldo)}</h1>
                <br>
                <div style="display: flex; justify-content: space-between; font-size: 12px; opacity: 0.8;">
                    <span>**** **** **** 2026</span>
                    <span>FAMÍLIA UNIDA</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Botão de Ação Rápida no Sidebar
    with st.sidebar:
        st.markdown("### ⚡ Ação Rápida")
        with st.form("quick_add", clear_on_submit=True):
            tipo = st.selectbox("Operação", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Título", placeholder="Ex: Aluguel")
            val = st.number_input("Valor", min_value=0.0)
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Saúde", "Outros"])
            if st.form_submit_button("Confirmar Transação", use_container_width=True):
                if desc and val > 0:
                    v_final = -val if tipo == "Saída (Gasto)" else val
                    novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": desc, "Valor": v_final, "Categoria": cat, "Tipo": tipo}])
                    df = pd.concat([df, novo], ignore_index=True)
                    conn.update(data=df)
                    st.toast("Transação salva!", icon="✅")
                    st.rerun()

    # Histórico estilo "Timeline"
    st.markdown("<p style='margin-top: 25px; font-weight: 600; color: #333;'>Movimentações</p>", unsafe_allow_html=True)
    if not df.empty:
        for i, row in df.iloc[::-1].iterrows():
            valor = float(row['Valor'])
            cor = "#e63946" if valor < 0 else "#2a9d8f"
            prefixo = "" if valor < 0 else "+"
            
            st.markdown(f"""
                <div class="finance-card">
                    <div>
                        <small style="color: #888; font-size: 11px;">{row['Data']}</small>
                        <div style="font-weight: 600; color: #1a1a1a;">{row['Descrição']}</div>
                        <small style="color: #aaa;">{row['Categoria']}</small>
                    </div>
                    <div style="text-align: right; font-weight: 600; color: {cor};">
                        {prefixo}{formatar_moeda(valor)}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botão de exclusão minimalista
            if st.button(f"Remover #{i}", key=f"del_{i}", use_container_width=False):
                df = df.drop(i)
                conn.update(data=df)
                st.rerun()
    else:
        st.markdown("<p style='text-align: center; color: #999;'>Nenhuma atividade recente.</p>", unsafe_allow_html=True)
