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

# --- MOTOR DE INTELIGÊNCIA ---
def extrair_dados_inteligente(imagem):
    try:
        # Converter imagem para OpenCV
        img = np.array(imagem.convert('RGB'))
        
        # Pré-processamento avançado para notas fiscais
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Aumentar nitidez e contraste
        gray = cv2.threshold(cv2.medianBlur(gray, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Configuração do Tesseract para focar em números e palavras financeiras
        custom_config = r'--oem 3 --psm 6'
        texto = pytesseract.image_to_string(gray, lang='por', config=custom_config)
        
        # 1. Identificar Valor Total
        # Padrões: TOTAL, VALOR A PAGAR, VALOR RECEBIDO, R$, SUBTOTAL
        padrao_valor = r'(?:TOTAL|VALOR|PAGAR|R\$)\s*:?\s*(\d+[\.,]\d{2})'
        todos_valores = re.findall(padrao_valor, texto, re.IGNORECASE)
        
        # Se não achar por palavra-chave, busca qualquer número com decimal no final da nota
        if not todos_valores:
            todos_valores = re.findall(r'(\d+[\.,]\d{2})', texto)
            
        valor_final = 0.0
        if todos_valores:
            # Pegamos o maior valor da nota (geralmente é o Total)
            lista_limpa = [float(v.replace('.', '').replace(',', '.')) for v in todos_valores]
            valor_final = max(lista_floats) if lista_floats else 0.0

        # 2. Tentar identificar Descrição (Nome do Estabelecimento)
        # Geralmente é a primeira ou segunda linha de texto com letras grandes
        linhas = [l.strip() for l in texto.split('\n') if len(l.strip()) > 3]
        desc_sugerida = linhas[0][:30] if linhas else "Nova Despesa"

        return desc_sugerida, valor_final
        
    except Exception as e:
        return None, 0.0

# --- INTERFACE (Conforme o modelo solicitado) ---
if check_password(): # Função de senha que já tínhamos
    st.title("🎯 Lançamento Inteligente")
    
    # Colunas para organizar como no seu modelo
    col_foto, col_dados = st.columns([1, 1.2])
    
    with col_foto:
        st.subheader("1. Capture o Comprovante")
        foto = st.camera_input("Tire a foto focando no Total")
        
    with col_dados:
        st.subheader("2. Confirme os Dados")
        
        # Estado do formulário
        desc_inicial = ""
        valor_inicial = 0.0
        
        if foto:
            with st.spinner('IA analisando o cupom...'):
                img_pil = Image.open(foto)
                desc_ia, valor_ia = extrair_dados_inteligente(img_pil)
                desc_inicial = desc_ia
                valor_inicial = valor_ia

        with st.form("confirmacao_ia", clear_on_submit=True):
            tipo = st.radio("Fluxo", ["Saída (Gasto)", "Entrada (Ganho)"], horizontal=True)
            
            # Campos com valores pré-preenchidos pela IA
            desc = st.text_input("Descrição Identificada", value=desc_inicial)
            valor_confirmado = st.number_input("Valor Identificado (R$)", value=float(valor_inicial), format="%.2f")
            
            cat = st.selectbox("Categoria", sorted(["Alimentação", "Cartão de Crédito", "Lazer", "Moradia", "Salário", "Saúde", "Transporte", "Outros"]))
            data = st.date_input("Data da Despesa", datetime.now())
            
            if st.form_submit_button("✅ CONFIRMAR E GUARDAR"):
                # Salvar no CSV (Mesma lógica anterior)
                # ... [Código de salvar igual ao anterior] ...
                st.balloons()
                st.rerun()

    # --- ABAIXO: GRÁFICOS E HISTÓRICO ---
    # [Código de gráficos e histórico igual ao anterior]
