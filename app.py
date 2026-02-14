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

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Finanças Pro AI", layout="wide", page_icon="🎯")

# --- FUNÇÕES DE SUPORTE ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def extrair_dados_inteligente(imagem):
    try:
        # 1. Preparação da Imagem (Transforma em "Scanner")
        img = np.array(imagem.convert('RGB'))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Aumenta o contraste e limpa o ruído
        # O filtro CLAHE ajuda a equilibrar a luz se a foto tiver sombras
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Binarização (Preto no Branco puro)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # 2. Leitura do Texto
        texto = pytesseract.image_to_string(gray, lang='por')
        
        # --- LOGICA DE BUSCA DE VALOR MELHORADA ---
        # Procuramos por qualquer número no formato 00,00 ou 00.00
        todos_numeros = re.findall(r'(\d+[\.,]\d{2})', texto)
        
        valor_final = 0.0
        if todos_numeros:
            # Converte todos para float
            lista_floats = []
            for v in todos_numeros:
                try:
                    # Limpa pontos de milhar e converte vírgula em ponto
                    limpo = v.replace('.', '').replace(',', '.')
                    lista_floats.append(float(limpo))
                except:
                    continue
            
            if lista_floats:
                # ESTRATÉGIA: Geralmente o TOTAL é o maior valor da nota fiscal.
                # Mas filtramos valores absurdos (ex: datas que pareçam valores)
                lista_filtrada = [n for n in lista_floats if n < 50000] # Limite de segurança
                if lista_filtrada:
                    valor_final = max(lista_filtrada)

        # 3. Busca de Descrição (Nome do estabelecimento)
        # Pegamos a primeira linha que contenha letras (evitando lixo do topo)
        linhas = [l.strip() for l in texto.split('\n') if len(l.strip()) > 5]
        desc_sugerida = ""
        for linha in linhas:
            if any(c.isalpha() for c in linha): # Se tem letras, é provável que seja o nome
                desc_sugerida = linha[:30]
                break

        return desc_sugerida, valor_final
    except Exception as e:
        print(f"Erro no OCR: {e}")
        return "", 0.0

def check_password():
    if "password" not in st.session_state:
        st.session_state.password = False
    if not st.session_state.password:
        st.title("🔐 Acesso Restrito")
        senha = st.text_input("Digite a senha da casa:", type="password")
        if st.button("Entrar"):
            if senha == "2804": # <--- SUA SENHA AQUI
                st.session_state.password = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

# --- EXECUÇÃO DO APP ---
if check_password():
    DB_FILE = "dados_financeiros.csv"
    COLunas = ["Data", "Descrição", "Valor", "Categoria", "Tipo"]

    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=COLunas)
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)
        if len(df.columns) != len(COLunas):
            df = pd.DataFrame(columns=COLunas)
            df.to_csv(DB_FILE, index=False)

    st.title("🎯 Lançamento com Inteligência Artificial")
    
    # Interface Lado a Lado (Conforme seu modelo)
    col_foto, col_dados = st.columns([1, 1.2])
    
    with col_foto:
        st.subheader("1. Foto do Comprovante")
        foto = st.camera_input("Foque no valor total da nota")
        
    with col_dados:
        st.subheader("2. Confirmação de Dados")
        
        # Lógica de processamento da IA
        desc_ia = ""
        valor_ia = 0.0
        
        if foto:
            with st.spinner('IA analisando nota...'):
                img_pil = Image.open(foto)
                desc_ia, valor_ia = extrair_dados_inteligente(img_pil)

        with st.form("form_ia", clear_on_submit=True):
            tipo = st.radio("Tipo de Fluxo", ["Saída (Gasto)", "Entrada (Ganho)"], horizontal=True)
            
            # Campos preenchidos automaticamente pela IA
            desc = st.text_input("Descrição (IA)", value=desc_ia)
            valor_confirmado = st.number_input("Valor Identificado (R$)", value=float(valor_ia), format="%.2f")
            
            cat = st.selectbox("Categoria", sorted(["Alimentação", "Cartão de Crédito", "Lazer", "Moradia", "Salário", "Saúde", "Transporte", "Outros"]))
            data = st.date_input("Data", datetime.now(), format="DD/MM/YYYY")
            
            if st.form_submit_button("✅ CONFIRMAR E SALVAR"):
                if desc == "" or valor_confirmado == 0:
                    st.warning("Por favor, verifique a descrição e o valor.")
                else:
                    valor_final = -valor_confirmado if tipo == "Saída (Gasto)" else valor_confirmado
                    novo = pd.DataFrame([[data.strftime("%d/%m/%Y"), desc, valor_final, cat, tipo]], columns=COLunas)
                    df = pd.concat([df, novo], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Registro salvo com sucesso!")
                    st.rerun()

    # --- DASHBOARD DE GRÁFICOS ---
    if not df.empty:
        st.divider()
        ganhos = df[df["Valor"] > 0]["Valor"].sum()
        gastos = abs(df[df["Valor"] < 0]["Valor"].sum())
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entradas", formatar_moeda(ganhos))
        c2.metric("Saídas", formatar_moeda(gastos))
        c3.metric("Saldo", formatar_moeda(ganhos - gastos))

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("📊 Comparativo")
            fig_comp = px.bar(x=["Entradas", "Saídas"], y=[ganhos, gastos], color=["Entradas", "Saídas"],
                             color_discrete_map={"Entradas": "#2ecc71", "Saídas": "#e74c3c"})
            st.plotly_chart(fig_comp, use_container_width=True)
        
        with col_g2:
            st.subheader("🍕 Gastos por Categoria")
            df_gastos = df[df["Valor"] < 0].copy()
            if not df_gastos.empty:
                df_gastos["Valor_Abs"] = df_gastos["Valor"].abs()
                fig_pizza = px.pie(df_gastos, values='Valor_Abs', names='Categoria', hole=0.4)
                st.plotly_chart(fig_pizza, use_container_width=True)

        # Histórico
        with st.expander("📄 Ver Histórico / Excluir"):
            for i, row in df.iloc[::-1].iterrows():
                col_d, col_ds, col_v, col_b = st.columns([1, 2, 1, 0.5])
                col_d.write(row['Data'])
                col_ds.write(row['Descrição'])
                col_v.write(formatar_moeda(row['Valor']))
                if col_b.button("🗑️", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
