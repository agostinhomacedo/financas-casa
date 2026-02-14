
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

# --- MOTOR DE IA ---
def extrair_dados_alta_precisao(imagem_file):
    try:
        img = Image.open(imagem_file)
        img = np.array(img.convert('RGB'))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Filtro de nitidez
        gray = cv2.threshold(cv2.medianBlur(gray, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        texto = pytesseract.image_to_string(gray, lang='por')
        
        valores = re.findall(r'(\d+[\.,]\d{2})', texto)
        v_final = 0.0
        if valores:
            v_final = max([float(v.replace('.', '').replace(',', '.')) for v in valores if float(v.replace('.', '').replace(',', '.')) < 10000])
        
        linhas = [l.strip() for l in texto.split('\n') if len(l.strip()) > 3]
        d_final = linhas[0][:25] if linhas else "Despesa"
        return d_final, v_final
    except:
        return "", 0.0

# --- SEGURANÇA ---
def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if not st.session_state.password:
        st.title("🔐 Acesso Restrito")
        senha = st.text_input("Senha da Casa:", type="password")
        if st.button("Entrar"):
            if senha == "1234":
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        return False
    return True

# --- APP PRINCIPAL ---
if check_password():
    DB_FILE = "dados_financeiros.csv"
    COLunas = ["Data", "Descrição", "Valor", "Categoria", "Tipo"]

    # Garante que o arquivo exista e esteja correto
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=COLunas)
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)
        if len(df.columns) != len(COLunas):
            os.remove(DB_FILE) # Apaga se estiver incompatível
            st.rerun()

    # Estados iniciais
    if "v_ia" not in st.session_state: st.session_state.v_ia = 0.0
    if "d_ia" not in st.session_state: st.session_state.d_ia = ""

    st.title("🏠 Finanças Inteligentes")
    
    c_foto, c_form = st.columns([1, 1])

    with c_foto:
        foto = st.camera_input("Tire foto do cupom")
        if foto:
            d, v = extrair_dados_alta_precisao(foto)
            st.session_state.d_ia = d
            st.session_state.v_ia = v

    with c_form:
        with st.form("confirmar", clear_on_submit=True):
            tipo = st.radio("Fluxo", ["Saída (Gasto)", "Entrada (Ganho)"], horizontal=True)
            desc = st.text_input("Descrição", value=st.session_state.d_ia)
            valor = st.number_input("Valor (R$)", value=float(st.session_state.v_ia), format="%.2f")
            cat = st.selectbox("Categoria", sorted(["Alimentação", "Cartão de Crédito", "Lazer", "Moradia", "Salário", "Saúde", "Transporte", "Outros"]))
            data = st.date_input("Data", datetime.now())

            if st.form_submit_button("SALVAR"):
                v_final = -valor if tipo == "Saída (Gasto)" else valor
                novo = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, v_final, cat, tipo]], columns=COLunas)
                df = pd.concat([df, novo], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.session_state.v_ia = 0.0
                st.session_state.d_ia = ""
                st.success("Salvo!")
                st.rerun()

    # Dashboard simples abaixo
    if not df.empty:
        st.divider()
        saldo = df["Valor"].sum()
        st.metric("Saldo Geral", f"R$ {saldo:.2f}")
        fig = px.pie(df[df["Valor"]<0], values=df[df["Valor"]<0]["Valor"].abs(), names='Categoria', title="Gastos por Categoria")
        st.plotly_chart(fig)
