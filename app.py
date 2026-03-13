import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Minha Casa", layout="centered")

st.markdown("""
    <style>
    /* Estilo Dark Moderno */
    html, body, [class*="css"] { 
        background-color: #000000 !important; 
        color: #FFFFFF !important; 
    }
    .block-container { max-width: 400px !important; padding: 1rem !important; }
    
    /* Cards de Gastos */
    .gasto-card {
        background: #111;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Esconder menus do Streamlit */
    header, footer, #MainMenu { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl="0").dropna(how="all")
    df["Valor"] = pd.to_numeric(df["Valor"])
    saldo = df["Valor"].sum()
except Exception:
    saldo, df = 0, pd.DataFrame(columns=["Data", "Descrição", "Valor"])

# --- CONTEÚDO ---
st.markdown("<h2 style='text-align: center;'>🏠 Finanças Casa</h2>", unsafe_allow_html=True)

# Card de Saldo
st.markdown(f"""
    <div style="background: #111; padding: 20px; border-radius: 20px; border: 1px solid #32D74B; text-align: center; margin-bottom: 20px;">
        <p style="color: #888; margin: 0; font-size: 14px;">SALDO DISPONÍVEL</p>
        <h1 style="color: #32D74B; margin: 0; font-size: 38px;">R$ {saldo:,.2f}</h1>
    </div>
""", unsafe_allow_html=True)

# Lançamento Rápido
with st.expander("➕ NOVO GASTO"):
    with st.form("add", clear_on_submit=True):
        desc = st.text_input("Descrição", placeholder="Ex: Mercado")
        valor = st.number_input("Valor", min_value=0.0, step=1.0)
        if st.form_submit_button("SALVAR AGORA", use_container_width=True):
            if desc and valor > 0:
                novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Descrição": desc, "Valor": -valor}])
                df = pd.concat([df, novo], ignore_index=True)
                conn.update(data=df)
                st.success("Salvo!")
                st.rerun()

# Histórico
st.markdown("<br><b>HISTÓRICO RECENTE</b>", unsafe_allow_html=True)
if not df.empty:
    for i, row in df.iloc[::-1].head(15).iterrows():
        st.markdown(f"""
            <div class="gasto-card">
                <div>
                    <div style="font-weight: 600; color: white;">{row['Descrição']}</div>
                    <div style="color: #888; font-size: 12px;">{row['Data']}</div>
                </div>
                <div style="color: #FF453A; font-weight: bold; font-size: 16px;">
                    R$ {abs(row['Valor']):,.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)
