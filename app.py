import gradio as gr
import pandas as pd
from datetime import datetime

# --- LÓGICA DE SENHA ---
PIN_CORRETO = "1234"

def gerenciar_teclado(digito, pin_atual):
    if digito == "⌫":
        return pin_atual[:-1]
    novo_pin = pin_atual + digito
    if len(novo_pin) <= 4:
        return novo_pin
    return pin_atual

def validar_acesso(pin):
    if pin == PIN_CORRETO:
        return gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(value=""), gr.update(visible=False)

# --- INTERFACE ---
with gr.Blocks(css=".container { max-width: 400px; margin: auto; } button { height: 70px !important; font-size: 20px !important; }") as app:
    
    # TELA DE LOGIN
    with gr.Column(visible=True) as login_screen:
        gr.Markdown("# 🔐 Acesso Familiar")
        pin_display = gr.Textbox(label="Senha", type="password", interactive=False, elem_id="pin_box")
        
        with gr.Row():
            b1 = gr.Button("1"); b2 = gr.Button("2"); b3 = gr.Button("3")
        with gr.Row():
            b4 = gr.Button("4"); b5 = gr.Button("5"); b6 = gr.Button("6")
        with gr.Row():
            b7 = gr.Button("7"); b8 = gr.Button("8"); b9 = gr.Button("9")
        with gr.Row():
            b_del = gr.Button("⌫"); b0 = gr.Button("0"); b_ok = gr.Button("OK", variant="primary")

    # TELA PRINCIPAL (DASHBOARD)
    with gr.Column(visible=False) as main_screen:
        gr.Markdown("# 🏠 Minha Casa Finanças")
        with gr.Row():
            gr.Number(label="Saldo Atual", value=1500.50, interactive=False)
        
        with gr.Row():
            desc = gr.Textbox(label="O que comprou?")
            valor = gr.Number(label="Valor")
            btn_salvar = gr.Button("Salvar", variant="primary")
        
        gr.Markdown("### Últimos Gastos")
        dados = gr.DataFrame(value=[["12/03", "Mercado", -150.00], ["11/03", "Lazer", -50.00]], headers=["Data", "Item", "R$"])

    # EVENTOS (O que acontece quando clica)
    botoes = [b1, b2, b3, b4, b5, b6, b7, b8, b9, b0, b_del]
    for b in botoes:
        b.click(gerenciar_teclado, inputs=[b, pin_display], outputs=pin_display)
    
    b_ok.click(validar_acesso, inputs=[pin_display], outputs=[login_screen, main_screen])

app.launch(share=True)
