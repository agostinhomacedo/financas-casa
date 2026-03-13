import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO E CSS "INQUEBRÁVEL" ---
st.set_page_config(page_title="Finanças Pro", layout="centered", page_icon="💰")

# CSS AGRESSIVO: Força o layout de grade 3x3 ignorando o padrão do Streamlit
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* --- O SEGREDO PARA NÃO EMPILHAR --- */
    /* Selecionamos o container de colunas e forçamos o Grid */
    [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 8px !important;
        margin-bottom: -15px !important;
    }
    
    /* Remove a largura mínima que o Streamlit impõe e que causa o empilhamento */
    [data-testid="column"] {
        width: 100% !important;
        min-width: 0px !important;
        flex: 1 1 0% !important;
    }

    /* Estilo das Teclas: Modernas e Altura Fixa */
    .stButton > button {
        height: 55px !important;
        border-radius: 12px !important;
        background: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    /* Botão OK em destaque Azul Moderno */
    button[kind="primary"] {
        background: #007AFF !important;
        color: white !important;
        border: none !important;
    }

    /* Ajuste de largura para Celular */
    .block-container {
        max-width: 350px !important;
        padding: 1.5rem 1rem !important;
        margin: auto;
    }

    /* Cards de Histórico Estilo App de Banco */
    .finance-card {
        background: white;
        padding: 12px;
        border-radius: 16px;
        margin-bottom: 8px;
        border: 1px solid #F0F0F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. ACESSO COM TECLADO 3x3 FIXO ---
def check_password():
    if "password" not in st.session_state: st.session_state.password = False
    if "senha_digitada" not in st.session_state: st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h3 style='text-align: center; color: #333;'>Digite o PIN</h3>", unsafe_allow_html=True)
        
        # PIN Display
        dots = "".join([f"<span style='font-size: 35px; color: {'#007AFF' if i < len(st.session_state.senha_digitada) else '#DDD'}; margin: 0 8px;'>●</span>" for i in range(4)])
        st.markdown(f"<div style='text-align: center; margin-bottom: 25px;'>{dots}</div>", unsafe_allow_html=True)

        # Container do Teclado
        # Usamos uma estrutura simples de botões. O CSS cuidará do resto.
        with st.container():
            # Linhas 1-9
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                c1, c2, c3 = st.columns(3)
                if c1.button(str(row[0]), key=f"k{row[0]}"):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[0]); st.rerun()
                if c2.button(str(row[1]), key=f"k{row[1]}"):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[1]); st.rerun()
                if c3.button(str(row[2]), key=f"k{row[2]}"):
                    if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += str(row[2]); st.rerun()

            # Linha Final
            c_del, c_zero, c_ok = st.columns(3)
            if c_del.button("⌫", key="del"): 
                st.session_state.senha_digitada = st.session_state.senha_digitada[:-1]; st.rerun()
            if c_zero.button("0", key="k0"):
                if len(st.session_state.senha_digitada) < 4: st.session_state.senha_digitada += "0"; st.rerun()
            if c_ok.button("OK", type="primary", key="ok"):
                if st.session_state.senha_digitada == "1234": # <--- SENHA
                    st.session_state.password = True; st.rerun()
                else:
                    st.error("Incorreta"); st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. DASHBOARD MODERNO ---
if check_password():
    st.markdown("<h4 style='color: #007AFF;'>Resumo Financeiro</h4>", unsafe_allow_html=True)
    
    try:
        df = conn.read(ttl="0").dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        saldo = df["Valor"].sum()
        
        # Card de Saldo Moderno
        st.markdown(f"""
            <div style="background: #007AFF; padding: 20px; border-radius: 20px; color: white; margin-bottom: 20px; box-shadow: 0 10px 20px rgba(0,122,255,0.2);">
                <small style="opacity: 0.8;">Saldo em Conta</small>
                <h2 style="margin: 0; font-size: 28px;">{formatar_moeda(saldo)}</h2>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico Donut Moderno
        df_g = df[df["Valor"] < 0].copy()
        if not df_g.empty:
            fig = px.pie(df_g, values=df_g["Valor"].abs(), names='Categoria', hole=0.7)
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=180)
            st.plotly_chart(fig, use_container_width=True)

    # Botão Adicionar (Sidebar)
    with st.sidebar:
        st.header("➕ Lançamento")
        with st.form("add_form", clear_on_submit=True):
            tipo = st.selectbox("Operação", ["Saída", "Entrada"])
            desc = st.text_input("Descrição")
            val = st.number_input("Valor", min_value=0.0)
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Saúde", "Outros"])
            if st.form_submit_button("Salvar Registro", use_container_width=True):
                if desc and val > 0:
                    vf = -val if tipo == "Saída" else val
                    n = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Descrição": desc, "Valor": vf, "Categoria": cat, "Tipo": tipo}])
                    df = pd.concat([df, n], ignore_index=True)
                    conn.update(data=df)
                    st.toast("Salvo com sucesso!"); st.rerun()

    # Histórico estilo Timeline
    st.markdown("<p style='font-weight: 600; color: #666;'>Movimentações</p>", unsafe_allow_html=True)
    for i, row in df.iloc[::-1].head(15).iterrows():
        cor = "#FF3B30" if float(row['Valor']) < 0 else "#34C759"
        st.markdown(f"""
            <div class="finance-card">
                <div>
                    <div style="font-weight: 600; font-size: 14px; color: #333;">{row['Descrição']}</div>
                    <small style="color: #999;">{row['Data']} • {row['Categoria']}</small>
                </div>
                <div style="color: {cor}; font-weight: 700;">{formatar_moeda(float(row['Valor']))}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"del_{i}"):
            df = df.drop(i).dropna(how="all")
            conn.update(data=df)
            st.rerun()
