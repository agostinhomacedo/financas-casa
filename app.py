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
st.set_page_config(page_title="Minha Casa Finanças AI", layout="wide", page_icon="📸")

# Função para extrair valor da imagem (IA Simples)
def extrair_valor_da_imagem(imagem):
    try:
        # 1. Converter para array e escala de cinza
        img = np.array(imagem.convert('RGB'))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # 2. Aumentar o contraste e reduzir ruído (ajuda muito em fotos de celular)
        gray = cv2.bilateralFilter(gray, 9, 75, 75) # Remove ruído mantendo bordas
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # 3. Executar o OCR
        texto = pytesseract.image_to_string(gray, lang='por')
        st.expander("Texto detectado (Debug)").write(texto) # Para você ver o que ele está lendo
        
        # 4. Lógica para achar o Valor Total
        # Procuramos por palavras-chave que geralmente precedem o valor final
        linhas = texto.lower().split('\n')
        for linha in reversed(linhas): # Começamos do fim da nota, onde costuma estar o total
            if any(chave in linha for chave in ['total', 'pago', 'valor', 'r$', 'recebido']):
                # Busca números no formato 0,00 ou 0.00 nesta linha
                numeros = re.findall(r'(\d+[\.,]\d{2})', linha)
                if numeros:
                    valor_limpo = numeros[-1].replace('.', '').replace(',', '.')
                    return float(valor_limpo)
        
        # Se não achou por palavra-chave, tenta pegar o maior valor numérico da nota
        todos_valores = re.findall(r'(\d+[\.,]\d{2})', texto)
        if todos_valores:
            lista_floats = [float(v.replace('.', '').replace(',', '.')) for v in todos_valores]
            return max(lista_floats) # O maior valor costuma ser o total
            
    except Exception as e:
        st.error(f"Erro no processamento: {e}")
    return 0.0

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- (Mantenha a função check_password aqui igual à anterior) ---
def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if not st.session_state.password:
        st.title("🔐 Acesso Restrito")
        senha = st.text_input("Senha:", type="password")
        if st.button("Entrar"):
            if senha == "2804":
                st.session_state.password = True
                st.rerun()
        return False
    return True

if check_password():
    st.title("🏠 Finanças com IA")

    DB_FILE = "dados_financeiros.csv"
    COLunas = ["Data", "Descrição", "Valor", "Categoria", "Tipo"]

    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=COLunas)
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)

    # --- ENTRADA INTELIGENTE ---
    with st.sidebar:
        st.header("📸 Registro por Foto")
        foto = st.camera_input("Tirar foto do recibo")
        
        valor_detectado = 0.0
        if foto:
            img_pil = Image.open(foto)
            with st.spinner('Lendo imagem...'):
                valor_detectado = extrair_valor_da_imagem(img_pil)
                st.info(f"Valor detectado: R$ {valor_detectado:.2f}")

        st.divider()
        with st.form("form_ia", clear_on_submit=True):
            tipo = st.radio("Tipo", ["Saída (Gasto)", "Entrada (Ganho)"])
            desc = st.text_input("Descrição", placeholder="Ex: Mercado Extra")
            
            # O valor já vem preenchido pelo que a IA leu
            valor_final_input = st.number_input("Confirme o Valor", value=float(valor_detectado), format="%.2f")
            
            cat = st.selectbox("Categoria", sorted(["Alimentação", "Cartão de Crédito", "Lazer", "Moradia", "Salário", "Saúde", "Transporte", "Outros"]))
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            if st.form_submit_button("💾 Salvar Registro"):
                val = -valor_final_input if tipo == "Saída (Gasto)" else valor_final_input
                novo = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, val, cat, tipo]], columns=COLunas)
                df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("Salvo!")
                st.rerun()

    # --- (O restante do código de gráficos permanece o mesmo) ---
    # ... (Copie a parte das métricas e gráficos do código anterior aqui)
