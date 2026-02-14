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

# --- MOTOR DE IA (REVISADO) ---
def extrair_valor_ia(imagem_file):
    try:
        img = Image.open(imagem_file)
        img = np.array(img.convert('RGB'))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Melhora o contraste para leitura de notas fiscais
        gray = cv2.threshold(cv2.medianBlur(gray, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        texto = pytesseract.image_to_string(gray, lang='por')
        
        # Busca por padrões de preço (00,00 ou 00.00)
        valores = re.findall(r'(\d+[\.,]\d{2})', texto)
        if valores:
            # Converte e pega o maior (geralmente o TOTAL)
            lista_floats = [float(v.replace('.', '').replace(',', '.')) for v in valores]
            return max(lista_floats)
    except:
        pass
    return 0.0

# --- SEGURANÇA ---
if "password" not in st.session_state: st.session_state.password = False
if not st.session_state.password:
    st.title("🔐 Acesso")
    if st.text_input("Senha:", type="password") == "1234":
        st.session_state.password = True
        st.rerun()
    st.stop()

# --- APP PRINCIPAL ---
DB_FILE = "dados_financeiros.csv"
COLunas = ["Data", "Descrição", "Valor", "Categoria", "Tipo"]

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=COLunas).to_csv(DB_FILE, index=False)

df = pd.read_csv(DB_FILE)

# Inicializa o valor na memória do navegador
if "valor_temp" not in st.session_state:
    st.session_state.valor_temp = 0.0

st.title("🏠 Lançamento Automático")

col_foto, col_dados = st.columns([1, 1])

with col_foto:
    st.subheader("1. Tire a Foto")
    foto = st.camera_input("Foque no TOTAL da nota")
    
    if foto:
        with st.spinner('IA lendo valor...'):
            valor_detectado = extrair_valor_ia(foto)
            if valor_detectado > 0:
                st.session_state.valor_temp = valor_detectado
                st.success(f"Valor Identificado: R$ {valor_detectado:.2f}")
                # Força a atualização da interface para o formulário ler o novo valor
                st.rerun() 

with col_dados:
    st.subheader("2. Confirme e Salve")
    
    # O segredo: não usamos 'value' fixo, usamos o session_state
    with st.form("meu_form", clear_on_submit=True):
        tipo = st.radio("Fluxo", ["Saída (Gasto)", "Entrada (Ganho)"], horizontal=True)
        
        desc = st.text_input("Descrição", placeholder="Ex: Mercado")
        
        # Campo valor conectado diretamente à IA
        valor_final = st.number_input("Valor (R$)", 
                                     value=st.session_state.valor_temp, 
                                     format="%.2f")
        
        cat = st.selectbox("Categoria", sorted(["Alimentação", "Cartão de Crédito", "Lazer", "Moradia", "Salário", "Saúde", "Transporte", "Outros"]))
        data = st.date_input("Data", datetime.now())

        if st.form_submit_button("✅ SALVAR NO SISTEMA"):
            if valor_final > 0:
                v_calc = -valor_final if tipo == "Saída (Gasto)" else valor_final
                novo_df = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, v_calc, cat, tipo]], columns=COLunas)
                df = pd.concat([df, novo_df], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                
                # Reseta para o próximo
                st.session_state.valor_temp = 0.0
                st.success("Salvo!")
                st.rerun()
            else:
                st.error("Insira um valor válido.")

# Dashboard rápido
if not df.empty:
    st.divider()
    st.subheader("📊 Resumo")
    st.plotly_chart(px.pie(df[df["Valor"]<0], values=df[df["Valor"]<0]["Valor"].abs(), names='Categoria', hole=0.4))
