from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
DB_FILE = "dados_financeiros.csv"

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    # Pega a mensagem enviada
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    try:
        # Tenta separar a descrição do valor (Ex: Pizza -50)
        partes = incoming_msg.split()
        if len(partes) >= 2:
            descricao = " ".join(partes[:-1])
            valor = float(partes[-1].replace(',', '.'))
            
            tipo = "Saída (Gasto)" if valor < 0 else "Entrada (Ganho)"
            # A categoria padrão via WhatsApp será "Outros" (você pode mudar no site depois)
            nova_linha = [datetime.now().strftime("%d/%m/%Y"), descricao, valor, "Outros", tipo]
            
            # Salva no CSV
            df = pd.read_csv(DB_FILE)
            df.loc[len(df)] = nova_linha
            df.to_csv(DB_FILE, index=False)
            
            msg.body(f"✅ Registrado com sucesso!\n📌 {descricao}: R$ {valor:.2f}")
        elif incoming_msg.lower() == 'resumo':
            df = pd.read_csv(DB_FILE)
            saldo = df['Valor'].sum()
            msg.body(f"📊 *Resumo Atual*\nSaldo total: R$ {saldo:.2f}")
        else:
            msg.body("Envie: 'Item Valor' (Ex: Cafe -5.00) ou 'Resumo'.")
            
    except Exception as e:
        msg.body("❌ Erro no formato. Use: Descrição Valor (Ex: Almoço -30)")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)
