import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURAÇÃO DE INTERFACE ULTRA-MODERNA E RESPONSIVA ---
# O layout="centered" ajuda a manter a interface elegante em desktops e celulares
st.set_page_config(page_title="Minha Casa Finanças Pro", layout="centered", page_icon="💰")

# Injeção de CSS customizado para garantir a responsividade e o visual inovador
st.markdown("""
    <style>
    /* Importando fonte moderna (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f8f9fa; }

    /* Forçando as colunas laterais no Mobile: ISSO IMPEDE O EMPILHAMENTO INDESEJADO */
    [data-testid="column"] {
        width: calc(33.33% - 5px) !important;
        flex: 1 1 calc(33.33% - 5px) !important;
        min-width: calc(33.33% - 5px) !important;
    }
    
    /* Reduz o espaçamento vertical entre as linhas de botões do teclado */
    [data-testid="stHorizontalBlock"] {
        gap: 5px !important;
        margin-bottom: -15px !important; /* Aproxima as linhas verticalmente */
    }

    /* Estilização das Teclas Numéricas: Estilo Minimalista e Facilidade de Toque */
    .stButton > button {
        height: 60px !important; /* Altura ideal para o polegar no celular */
        width: 100% !important;
        border-radius: 15px !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #31333F !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03) !important;
    }
    
    /* Efeito de hover/toque para as teclas numéricas */
    .stButton > button:hover {
        background-color: #f0f0f0 !important;
        border-color: #ccc !important;
        transform: translateY(-2px);
    }

    /* Estilização Diferenciada para Botões Especiais (Limpar, OK) */
    button[kind="secondary"] { /* Estilo do Limpar */
        background-color: #ffcccc !important;
        color: #b30000 !important;
        border: 1px solid #ff9999 !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: #ffb3b3 !important;
    }

    button[kind="primary"] { /* Estilo do Entrar (OK) */
        background: linear-gradient(135deg, #1A73E8 0%, #0056D2 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
    }
    
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0056D2 0%, #0042A2 100%) !important;
        transform: translateY(-2px);
    }

    /* Ajuste de Margens e Padding para o Container Principal no Mobile */
    .block-container {
        max-width: 420px !important; /* Estreita o app no desktop para simular celular */
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        margin: auto;
    }

    /* Estilo Inovador para os Cards do Histórico e Gráficos */
    .css-1r6slb0, div[data-testid="stMetricValue"] {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(5px) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. SISTEMA DE ACESSO COM TECLADO NUMÉRICO MODELO CALCULADORA ---
def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    
    # Inicializa a variável para armazenar a senha digitada
    if "senha_digitada" not in st.session_state:
        st.session_state.senha_digitada = ""

    if not st.session_state.password:
        st.markdown("<h2 style='text-align: center; color: #1A73E8;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
        
        # Centraliza a visualização da senha
        st.markdown("<h3 style='text-align: center; color: gray;'>Digite a senha da casa:</h3>", unsafe_allow_html=True)
        
        # Exibe a senha usando asteriscos (*) enquanto digita para manter a privacidade
        display_senha = " * " * len(st.session_state.senha_digitada)
        st.markdown(f"<h1 style='text-align: center; font-size: 32px; letter-spacing: 5px; color: #31333F;'>{display_senha if display_senha else '____'}</h1>", unsafe_allow_html=True)
        
        # Desenha o Teclado Numérico 3x3 usando colunas
        for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            cols = st.columns(3)
            for i, num in enumerate(row):
                if cols[i].button(str(num), use_container_width=True, key=f"btn_{num}"):
                    # Permite digitar no máximo 4 dígitos para a senha
                    if len(st.session_state.senha_digitada) < 4:
                        st.session_state.senha_digitada += str(num)
                        st.rerun()

        # Linha inferior do teclado: Limpar, Zero e Entrar
        c1, c2, c3 = st.columns(3)
        if c1.button("Limpar", key="limpar", use_container_width=True):
            st.session_state.senha_digitada = ""
            st.rerun()
            
        if c2.button("0", key="btn_0", use_container_width=True):
            if len(st.session_state.senha_digitada) < 4:
                st.session_state.senha_digitada += "0"
                st.rerun()
            
        # O botão "Entrar" usa o estilo 'primary' (vibrante) configurado no CSS
        if c3.button("Entrar", type="primary", key="entrar", use_container_width=True):
            if st.session_state.senha_digitada == "1234": # <--- SUA SENHA AQUI
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                st.session_state.senha_digitada = ""
        
        return False
    return True

# --- 3. CONTEÚDO PRINCIPAL DO APP (SOMENTE SE LOGADO) ---
if check_password():
    st.markdown("<h1 style='color: #1A73E8;'>🏠 Finanças da Família Pro</h1>", unsafe_allow_html=True)

    # --- LER DADOS DO GOOGLE SHEETS ---
    try:
        df = conn.read(ttl="0") # ttl="0" garante que ele sempre pegue o dado mais atual
        df = df.dropna(how="all") # Limpa linhas totalmente vazias
    except Exception as e:
        # Se der erro, cria um dataframe vazio para o app não crashar
        df = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Categoria", "Tipo"])

    # --- BARRA LATERAL PARA ENTRADA DE DADOS (侧边栏) ---
    with st.sidebar:
        st.header("➕ Novo Lançamento")
        with st.form("form_novo", clear_on_submit=True):
            tipo = st.radio("Operação", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Descrição", placeholder="Ex: Mercado")
            valor_input = st.number_input("Valor", min_value=0.0, format="%.2f", step=1.0)
            cat = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Salário", "Transporte", "Saúde", "Educação", "Outros", "Investimento"])
            
            # Formato de data configurado para o padrão brasileiro
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            # O botão de salvar também é responsivo
            if st.form_submit_button("💾 Salvar Registro", use_container_width=True):
                if desc == "" or valor_input == 0:
                    st.warning("Preencha a descrição e o valor!")
                else:
                    valor_final = -valor_input if tipo == "Saída (Gasto)" else valor_input
                    
                    # Criar nova linha de dados
                    novo = pd.DataFrame([{
                        "Data": data.strftime("%d/%m/%Y"), # Salvando a data no formato dd/mm/yyyy
                        "Descrição": desc,
                        "Valor": valor_final,
                        "Categoria": cat,
                        "Tipo": tipo
                    }])
                    
                    # Adicionar ao DataFrame atual e atualizar o Google Sheets
                    df_atualizado = pd.concat([df, novo], ignore_index=True)
                    conn.update(data=df_atualizado)
                    st.success("Salvo!")
                    st.rerun() # Recarrega o app para atualizar os gráficos

    # --- PAINEL VISUAL RESPONSIVO ---
    if not df.empty:
        # Garantir que a coluna 'Valor' é numérica antes de calcular
        df["Valor"] = pd.to_numeric(df["Valor"])
        
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = df[df["Valor"] < 0]["Valor"].sum()
        saldo = ganhos + gastos

        # Métricas com formatação brasileira e estilo 'Glassmorphism' (vidro embaçado)
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", formatar_moeda(ganhos))
        c2.metric("Saídas", formatar_moeda(abs(gastos)))
        c3.metric("Saldo Atual", formatar_moeda(saldo))

        # --- Gráfico de Pizza Inovador (Pizza Donut) ---
        df_gastos = df[df["Valor"] < 0].copy()
        if not df_gastos.empty:
            st.subheader("🍕 Divisão de Gastos")
            df_gastos["Valor_Abs"] = df_gastos["Valor"].abs() # Gráfico de pizza precisa de valores positivos
            
            # Gráfico de rosca (hole=0.4) com cores personalizadas e responsivas
            fig = px.pie(df_gastos, values='Valor_Abs', names='Categoria', hole=0.6,
                         color_discrete_sequence=px.colors.qualitative.Bold)
            
            # Remove legendas e centraliza o gráfico para caber melhor no celular
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=True)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            # O gráfico também se ajusta automaticamente à largura da tela (use_container_width=True)
            st.plotly_chart(fig, use_container_width=True)

        # --- Histórico estilo Timeline ---
        st.divider()
        st.subheader("📄 Últimos Lançamentos")
        
        # Inverte o DF para mostrar os registros mais recentes primeiro (iloc[::-1])
        # Usamos st.container() para criar cartões responsivos em vez de tabelas
        for i, row in df.iloc[::-1].head(15).iterrows():
            with st.container():
                # Cria 3 colunas para Data, Descrição e Valor
                col_data, col_desc, col_val = st.columns([1, 2, 1])
                
                # Define a cor com base no valor: Vermelho para Gasto, Verde para Ganho
                # A formatação format_moeda já ajusta para R$ 1.234,56
                cor = "#e63946" if float(row['Valor']) < 0 else "#2a9d8f"
                
                col_data.write(f"**{row['Data']}**")
                col_desc.write(f"{row['Descrição']}<br><small style='color: gray'>{row['Categoria']}</small>", unsafe_allow_html=True)
                col_val.write(f"<span style='color: {cor}; font-weight: bold;'>{formatar_moeda(float(row['Valor']))}</span>", unsafe_allow_html=True)
                
                # Botão de exclusão (lixeira) minimalista
                if st.button("🗑️", key=f"del_{i}"):
                    df_exclusao = df.drop(i)
                    conn.update(data=df_exclusao)
                    st.rerun()
                st.write("---") # Linha divisória entre cartões
    else:
        st.info("Ainda não há registros. Use o menu lateral à esquerda para adicionar!")

# Rodapé simples e discreto
st.markdown("<p style='text-align: center; color: grey; font-size: 10px; margin-top: 50px;'>v1.0 • Família Finanças Pro • Desenvolvido com Streamlit + CSS Advanced Responsiveness</p>", unsafe_allow_html=True)
