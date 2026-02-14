import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import re

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Finanças Pro AI", layout="wide", page_icon="🎯")

# --- MOTOR DE IA DE ALTA PERFORMANCE ---
def processar_imagem_avancado(img_pil):
    # Converte para OpenCV
    img = np.array(img_pil.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Criamos 3 versões da imagem para garantir a leitura
    versao1 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    versao2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    versao3 = cv2.medianBlur(img, 3)

    texto_final = ""
    for v in [versao1, versao2, versao3]:
        # Tenta ler cada versão da imagem
        texto_final += pytesseract.image_to_string(v, lang='por', config='--psm 6') + " "

    # Busca avançada por valores (0.000,00 ou 000.00)
    # Filtramos para pegar valores que tenham sentido financeiro
    numeros = re.findall(r'(\d+[\.,]\d{2})', texto_final)
    
    if numeros:
        # Converte tudo para float e remove erros de leitura (ex: datas)
        lista_valores = []
        for n in numeros:
            val = float(n.replace('.', '').replace(',', '.'))
            if 0.50 < val < 50000.00: # Filtro: ignora centavos irrelevantes e valores absurdos
                lista_valores.append(val)
        
        if lista_valores:
            # O Total é quase sempre o maior valor da nota
            return max(lista_valores)
    return 0.0

# --- SEGURANÇA E LOGIN ---
if "password" not in st.session_state: st.session_state.password = False
if not st.session_state.password:
    st.title("🔐 Acesso Restrito")
    if st.text_input("Senha:", type="password") == "1234":
        st.session_state.password = True
        st.rerun()
    st.stop()

# --- BANCO DE DADOS ---
DB_FILE = "dados_financeiros.csv"
COLUNAS = ["Data", "Descrição", "Valor", "Categoria", "Tipo"]
if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=COLUNAS).to_csv(DB_FILE, index=False)
df = pd.read_csv(DB_FILE)

# --- INTERFACE ---
if "valor_ia" not in st.session_state: st.session_state.valor_ia = 0.0

st.title("🏠 Sistema Financeiro Inteligente")

col_foto, col_dados = st.columns([1, 1])

with col_foto:
    st.subheader("📷 Escanear Comprovante")
    foto = st.camera_input("Foque no valor total da nota")
    
    if foto:
        with st.spinner('IA analisando...'):
            valor_extraido = processar_imagem_avancado(Image.open(foto))
            if valor_extraido > 0:
                st.session_state.valor_ia = valor_extraido
                st.success(f"Detectado: R$ {valor_extraido:.2f}")
                st.rerun() # ESSENCIAL para atualizar o campo abaixo
            else:
                st.error("Valor não identificado. Tente aproximar mais ou melhorar a luz.")

with col_dados:
    st.subheader("📝 Confirmação")
    with st.form("form_final", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"], horizontal=True)
        desc = st.text_input("Descrição", placeholder="Ex: Supermercado")
        
        # O campo VALOR agora é forçado pela IA
        valor_final = st.number_input("Valor Identificado (R$)", 
                                     value=st.session_state.valor_ia, 
                                     step=0.01, format="%.2f")
        
        cat = st.selectbox("Categoria", sorted(["Alimentação", "Cartão de Crédito", "Lazer", "Moradia", "Salário", "Saúde", "Transporte", "Outros"]))
        data = st.date_input("Data", datetime.now())

        if st.form_submit_button("✅ SALVAR REGISTRO"):
            if valor_final > 0:
                v_real = -valor_final if tipo == "Saída (Gasto)" else valor_final
                novo = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, v_real, cat, tipo]], columns=COLUNAS)
                df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.session_state.valor_ia = 0.0 # Reseta
                st.success("Salvo com sucesso!")
                st.rerun()
