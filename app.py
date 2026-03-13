import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO VISUAL (ALTO CONTRASTE) ---
st.set_page_config(page_title="Minha Casa", layout="centered")

st.markdown("""
    <style>
    /* Fundo preto e texto branco puro para enxergar no celular */
    html, body, [class*="css"] { 
        background-color: #000000 !important; 
        color: #FFFFFF !important; 
    }
    
    .block-container { 
        max-width: 400px !important; 
        padding: 1rem !important; 
    }

    /* Cards de Gastos: Fundo cinza escuro com borda verde */
    .gasto-card {
        background: #1A1A1A;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #32D74B;
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    
    /* Cores dos textos nos cards */
    .gasto-card b { color: #FFFFFF !important; font-size: 16px; }
    .gasto-card span { color: #AAAAAA !important; font-size: 12px; }
    
    /* Esconde elementos desnecessários do Streamlit */
    header, footer, #MainMenu { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lê os dados da planilha
    df = conn.read(ttl="0").dropna(how="all")
    # Garante que a coluna Valor é numérica
    df["Valor"] = pd.to_numeric(df["Valor"])
    saldo = df["Valor"].sum()
except:
    saldo = 0
    df = pd.DataFrame(columns=["Data", "Descrição", "Valor"])

# --- 3. EXIBIÇÃO DO DASHBOARD ---
st.markdown("<h2 style='color: white; text-align: center;'>🏠 Minha Casa</h2>", unsafe_allow_html=True)

# Card de Saldo em destaque Verde Neon
st.markdown(f"""
    <div style="background: #1A1A1A; padding: 25px; border-radius: 20px; border: 2px solid #32D74B; text-align: center; margin-bottom: 20px;">
        <p style="color: #AAAAAA; margin: 0; font-size: 14px;">SALDO TOTAL</p>
        <h1 style="color: #32D74B; margin: 0; font-size: 42px;">R$ {saldo:,.2f}</h1>
    </div>
""", unsafe_allow_html=True)

# --- 4. ÁREA DE LANÇAMENTO (SIMPLIFICADA) ---
with st.expander("➕ ADICIONAR NOVO GASTO"):
    with st.form("novo_gasto", clear_on_submit=True):
        desc = st.text_input("O que comprou?")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
        
        if st.form_submit_button("SALVAR NO GOOGLE SHEETS", use_container_width=True):
            if desc and valor > 0:
                novo_dado = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m"),
                    "Descrição": desc,
                    "Valor": -valor # Salva como negativo por ser gasto
                }])
                df_atualizado = pd.concat([df, novo_dado], ignore_index=True)
                conn.update(data=df_atualizado)
                st.success("Salvo!")
                st.rerun()

# --- 5. HISTÓRICO DE LANÇAMENTOS ---
st.markdown("<br><b style='color: white; letter-spacing: 1px;'>ÚLTIMOS LANÇAMENTOS</b>", unsafe_allow_html=True)

if not df.empty:
    # Mostra os últimos 15 itens (do mais novo para o mais velho)
    for i, row in df.iloc[::-1].head(15).iterrows():
        st.markdown(f"""
            <div class="gasto-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <b>{row['Descrição']}</b><br>
                        <span>{row['Data']}</span>
                    </div>
                    <b style="color: #FF453A !important; font-size: 18px;">
                        R$ {abs(row['Valor']):,.2f}
                    </b>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Nenhum lançamento encontrado.")
