import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE INTERFACE "NATIVA" ---
st.set_page_config(page_title="Minha Casa", layout="centered", page_icon="💰")

# CSS Avançado para forçar visual de App Mobile
st.markdown("""
    <style>
    /* Remove margens desnecessárias e fixa o fundo */
    .main { background-color: #f8f9fa; }
    .block-container { padding: 1rem !important; max-width: 450px !important; }
    
    /* Estilização do Teclado para ser compacto e centralizado */
    .stButton > button {
        height: 55px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    /* Botão de Entrar (OK) em destaque */
    button[kind="primary"] {
        background-color: #2e7d32 !important;
        color: white !important;
        border: none !important;
    }

    /* Cards para o histórico */
    .css-1r6slb0 { 
        background-color: white; 
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Esconder o menu lateral em telas muito pequenas se desejar, 
       mas aqui vamos focar no teclado */
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. TECLADO VIRTUAL COMPACTO ---
def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if "senha_digitada" not in st.session_state:
        st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<br><h2 style='text-align: center;'>🔒</h2>", unsafe_allow_html=True)
        
        # Display de senha minimalista
        display = " • " * len(st.session_state.senha_digitada)
        placeholder = " ○ " * (4 - len(st.session_state.senha_digitada))
        st.markdown(f"<h1 style='text-align: center; letter-spacing: 10px; color: #333;'>{display}{placeholder}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Insira a senha da casa</p>", unsafe_allow_html=True)

        # Teclado Numérico (Forçado a ser pequeno)
        # Usamos colunas com proporções para manter o teclado estreito no meio da tela
        _, col_key, _ = st.columns([0.1, 0.8, 0.1])
        
        with col_key:
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                c1, c2, c3 = st.columns(3)
                if c1.button(str(row[0]), key=f"k{row[0]}"):
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(row[0])
                        st.rerun()
                if c2.button(str(row[1]), key=f"k{row[1]}"):
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(row[1])
                        st.rerun()
                if c3.button(str(row[2]), key=f"k{row[2]}"):
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(row[2])
                        st.rerun()

            c1, c2, c3 = st.columns(3)
            if c1.button("⌫", key="del"):
                st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]
                st.rerun()
            if c2.button("0", key="k0"):
                if len(st.session_state.senha_digitada) < 4:
                    st.session_state.senha_digitada += "0"
                    st.rerun()
            if c3.button("OK", type="primary", key="ok"):
                if st.session_state.senha_digitada == "1234":
                    st.session_state.password = True
                    st.rerun()
                else:
                    st.error("Senha incorreta")
                    st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. CONTEÚDO PRINCIPAL ---
if check_password():
    st.markdown("<h3 style='margin-bottom:0;'>🏠 Minha Casa</h3>", unsafe_allow_html=True)
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # Métricas em Cards pequenos
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        # Layout de métricas horizontal mas compacto
        st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 20px; text-align: center; border: 1px solid #eee;">
                <p style="color: gray; margin-bottom: 5px;">Saldo Atual</p>
                <h2 style="margin: 0; color: {'#2e7d32' if saldo >= 0 else '#c62828'};">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

    # Botão flutuante simulado para Adicionar (Sidebar)
    st.sidebar.header("➕ Novo Gasto/Ganho")
    with st.sidebar.form("novo"):
        tipo = st.selectbox("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
        desc = st.text_input("O que é?")
        val = st.number_input("Quanto?", min_value=0.0)
        cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Saúde", "Outros"])
        data = st.date_input("Quando?", datetime.now())
        if st.form_submit_button("Salvar Registro", use_container_width=True):
            if desc and val > 0:
                v_final = -val if tipo == "Saída (Gasto)" else val
                novo = pd.DataFrame([{"Data": data.strftime("%d/%m/%Y"), "Descrição": desc, "Valor": v_final, "Categoria": cat, "Tipo": tipo}])
                df = pd.concat([df, novo], ignore_index=True)
                conn.update(data=df)
                st.rerun()

    # Histórico estilo "Extrato de Banco"
    st.markdown("<br><b>Extrato Recente</b>", unsafe_allow_html=True)
    if not df.empty:
        for i, row in df.iloc[::-1].iterrows():
            cor_valor = "#c62828" if float(row['Valor']) < 0 else "#2e7d32"
            simbolo = "" if float(row['Valor']) < 0 else "+"
            
            st.markdown(f"""
                <div style="background-color: white; padding: 12px; border-radius: 15px; margin-bottom: 8px; border-left: 5px solid {cor_valor}; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <small style="color: gray;">{row['Data']}</small><br>
                        <b>{row['Descrição']}</b><br>
                        <small>{row['Categoria']}</small>
                    </div>
                    <div style="text-align: right;">
                        <b style="color: {cor_valor};">{simbolo}{formatar_moeda(float(row['Valor']))}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            # Botão de deletar pequeno logo abaixo do card
            if st.button(f"Remover item {i}", key=f"del_{i}", help="Clique para apagar"):
                df = df.drop(i)
                conn.update(data=df)
                st.rerun()
    else:
        st.info("Nenhum gasto registrado.")
