from flask import Flask, request
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

EMAIL_ORIGEM = os.environ.get("EMAIL_ORIGEM", "seu_email@hostinger.com")
EMAIL_DESTINO = os.environ.get("EMAIL_DESTINO", "delpim@desk.ms")
EMAIL_SENHA = os.environ.get("EMAIL_SENHA", "sua_senha_aqui")
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 465

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()

    if not data:
        return "Dados ausentes", 400

    assunto = "Novo Callback da Zenvia"
    corpo = f"Dados recebidos:\n\n{data}"

    try:
        msg = MIMEText(corpo)
        msg["Subject"] = assunto
        msg["From"] = EMAIL_ORIGEM
        msg["To"] = EMAIL_DESTINO

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ORIGEM, EMAIL_SENHA)
            server.send_message(msg)

        return "E-mail enviado com sucesso", 200

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return "Erro ao enviar e-mail", 500

@app.route("/", methods=["GET"])
def home():
    return "Webhook Zenvia ativo!", 200
