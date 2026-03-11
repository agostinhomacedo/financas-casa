import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Minha Casa Finanças", 
    layout="centered", 
    page_icon="💰"
)

# CSS para ajustar o tamanho dos botões e layout mobile
st.markdown("""
    <style>
    /* Ajusta o preenchimento superior em dispositivos móveis */
    .main > div { padding-top: 1rem; }
    
    /* Estilização dos botões do teclado para não ficarem gigantes */
    div.stButton > button {
        height: 60px !important;
        font-size: 20px !important;
        border-radius: 12px;
        margin-bottom: -5px;
    }
    
    /* Ajuste para o container de métricas não ocupar muito espaço vertical */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. SISTEMA DE ACESSO (TECLADO VIRTUAL) ---
def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if "senha_digitada" not in st.session_state:
        st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h3 style='text-align: center;'>🔐 Acesso Restrito</h3>", unsafe_allow_html=True)
        
        # Display da senha (bolinhas)
        display = " ● " * len(st.session_state.senha_digitada)
        st.markdown(f"<h1 style='text-align: center; color: #31333F;'>{display if display else '____'}</h1>", unsafe_allow_html=True)

        # Container centralizado para o teclado não esticar no celular
        _, col_centro, _ = st.columns([1, 4, 1])
        
        with col_centro:
            # Teclado 1-9
            for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
                cols = st.columns(3)
                for i, num in enumerate(row):
                    if cols[i].button(str(num), key=f"btn_{num}", use_container_width=True):
                        if len(st.session_state.senha_digitada) < 4:
                            st.session_state.senha_digitada += str(num)
                            st.rerun()

            # Linha 0 e Controles
            c1, c2, c3 = st.columns(3)
            if c1.button("❌", key="clear", use_container_width=True):
                st.session_state.senha_digitada = ""
                st.rerun()
            if c2.button("0", key="btn_0", use_container_width=True):
                if len(st.session_state.senha_digitada) < 4:
                    st.session_state.senha_digitada += "0"
                    st.rerun()
            if c3.button("OK", type="primary", key="enter", use_container_width=True):
                if st.session_state.senha_digitada == "2804": # <--- SUA SENHA AQUI
                    st.session_state.password = True
                    st.rerun()
                else:
                    st.error("Senha Incorreta")
                    st.session_state.senha_digitada = ""
        return False
    return True

# --- 3. EXECUÇÃO DO APLICATIVO ---
if check_password():
    st.title("🏠 Finanças da Família")

    # Carregar dados da Planilha
    try:
        df = conn.read(ttl="0")
        df = df.dropna(how="all")
    except:
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # Sidebar para novos registros
    with st.sidebar:
        st.header("➕ Novo Registro")
        with st.form("add_form", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Descrição", placeholder="Ex: Mercado")
            valor_in = st.number_input("Valor", min_value=0.0, format="%.2f")
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Saúde", "Educação", "Outros"])
            data_in = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            if st.form_submit_button("💾 Salvar no Google Sheets", use_container_width=True):
                if desc and valor_in > 0:
                    valor_final = -valor_in if tipo == "Saída (Gasto)" else valor_in
                    novo_dado = pd.DataFrame([{
                        "Data": data_in.strftime("%d/%m/%Y"),
                        "Descrição": desc,
                        "Valor": valor_final,
                        "Categoria": cat,
                        "Tipo": tipo
                    }])
                    df_novo = pd.concat([df, novo_dado], ignore_index=True)
                    conn.update(data=df_novo)
                    st.success("Salvo com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha Descrição e Valor!")

    # Painel de Resumo
    if not df.empty:
        df["Valor"] = pd.to_numeric(df["Valor"])
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = df[df["Valor"] < 0]["Valor"].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Ganhos", formatar_moeda(ganhos))
        m2.metric("Gastos", formatar_moeda(abs(gastos)))
        m3.metric("Saldo", formatar_moeda(ganhos + gastos))

        # Gráfico de Gastos
        df_gastos = df[df["Valor"] < 0].copy()
        if not df_gastos.empty:
            st.subheader("🍕 Divisão de Gastos")
            fig = px.pie(df_gastos, values=df_gastos["Valor"].abs(), names='Categoria', hole=0.4)
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

        # Histórico Responsivo
        st.divider()
        st.subheader("📄 Histórico Recente")
        
        for i, row in df.iloc[::-1].iterrows():
            with st.container():
                c_data, c_info, c_btn = st.columns([2, 4, 1])
                cor = "red" if float(row['Valor']) < 0 else "green"
                
                c_data.write(f"**{row['Data']}**")
                c_info.write(f":{cor}[{formatar_moeda(float(row['Valor']))}]")
                
                if c_btn.button("🗑️", key=f"del_{i}"):
                    df_upd = df.drop(i)
                    conn.update(data=df_upd)
                    st.rerun()
                
                st.caption(f"{row['Descrição']} | {row['Categoria']}")
                st.markdown("---")
    else:
        st.info("Nenhum registro encontrado na planilha.")

# Rodapé simples
st.markdown("<p style='text-align: center; color: grey;'>Sistema Financeiro Familiar v2.0</p>", unsafe_allow_html=True)
