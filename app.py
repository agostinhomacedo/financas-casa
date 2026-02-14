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

def extrair_dados_alta_precisao(imagem_file):
    try:
        # 1. Carregar e forçar alta resolução
        img = Image.open(imagem_file)
        img = np.array(img.convert('RGB'))
        
        # 2. PRÉ-PROCESSAMENTO "SCANNER" (O segredo da precisão)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Aumentar a escala da imagem (ajuda a ler letras pequenas de cupons)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Filtro para remover sombras e brilhos do papel térmico
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # 3. OCR com configuração de "Bloco de Texto"
        # --psm 6 assume que a nota é um bloco único, --oem 3 é o motor mais forte
        custom_config = r'--oem 3 --psm 6'
        texto = pytesseract.image_to_string(gray, lang='por', config=custom_config)
        
        # DEBUG: Caso queira ver o que a IA está lendo, descomente a linha abaixo
        # st.expander("Ver o que a IA leu").code(texto)

        # 4. BUSCA INTELIGENTE DE VALORES
        # Procuramos por números com vírgula ou ponto (padrão BR)
        padrao_valor = r'(\d+[\.,]\d{2})'
        todos_valores = re.findall(padrao_valor, texto)
        
        if not todos_valores:
            return "Não identificado", 0.0

        # Converte para float e limpa
        lista_floats = []
        for v in todos_valores:
            limpo = v.replace('.', '').replace(',', '.')
            try:
                lista_floats.append(float(limpo))
            except: continue

        # O Valor Total costuma ser o MAIOR valor próximo a palavras-chave
        # Mas se não houver palavras-chave, pegamos o maior valor absoluto abaixo de 10.000
        valor_final = max([n for n in lista_floats if n < 10000]) if lista_floats else 0.0
        
        # Tenta pegar a primeira linha para o nome
        linhas = [l.strip() for l in texto.split('\n') if len(l.strip()) > 3]
        desc_final = linhas[0][:25] if linhas else "Despesa"

        return desc_final, valor_final
    except:
        return "Erro na leitura", 0.0

# --- INTERFACE ---
# (Certifique-se de manter a função check_password no seu arquivo!)

if "password" in st.session_state and st.session_state.password:
    DB_FILE = "dados_financeiros.csv"
    COLunas = ["Data", "Descrição", "Valor", "Categoria", "Tipo"]

    # Iniciar estado se não existir
    if "valor_ia" not in st.session_state: st.session_state.valor_ia = 0.0
    if "desc_ia" not in st.session_state: st.session_state.desc_ia = ""

    st.title("🎯 Lançamento Rápido com IA")
    
    col_foto, col_dados = st.columns([1, 1])

    with col_foto:
        st.subheader("📷 Tirar Foto")
        # camera_input por padrão usa a resolução máxima do dispositivo
        foto = st.camera_input("Foque no TOTAL da nota")
        
        if foto:
            with st.spinner('Processando imagem em HD...'):
                d, v = extrair_dados_alta_precisao(foto)
                st.session_state.valor_ia = float(v)
                st.session_state.desc_ia = d

    with col_dados:
        st.subheader("📝 Confirmar Dados")
        with st.form("confirm_ia", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"], horizontal=True)
            
            # OS CAMPOS SÃO PREENCHIDOS AQUI
            desc = st.text_input("Descrição", value=st.session_state.desc_ia)
            valor = st.number_input("Valor Identificado (R$)", value=st.session_state.valor_ia, format="%.2f")
            
            cat = st.selectbox("Categoria", sorted(["Alimentação", "Cartão de Crédito", "Lazer", "Moradia", "Salário", "Saúde", "Transporte", "Outros"]))
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")

            if st.form_submit_button("✅ SALVAR REGISTRO"):
                if valor > 0:
                    v_final = -valor if tipo == "Saída (Gasto)" else valor
                    # Lógica de salvar no CSV igual à anterior
                    df = pd.read_csv(DB_FILE)
                    novo = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, v_final, cat, tipo]], columns=COLunas)
                    df = pd.concat([df, novo], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    
                    # Resetar estados
                    st.session_state.valor_ia = 0.0
                    st.session_state.desc_ia = ""
                    st.success("Salvo!")
                    st.rerun()
                else:
                    st.error("Valor não identificado. Por favor, digite manualmente ou tente outra foto.")
