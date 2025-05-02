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

    assunto = "Nova Ligação Finalizada na Zenvia"
    corpo = f"""
📞 Chamada TTS Recebida

ID: {data["id"]}
Status: {data["status"]}
Número de Origem: {data["numero_origem"]}
Número de Destino: {data["numero_destino"]}
Data de Início: {data["data_inicio"]}
Duração: {data["duracao"]} ({data["duracao_segundos"]} segundos)
Duração Cobrada: {data["duracao_cobrada"]} ({data["duracao_cobrada_segundos"]} segundos)
Duração Falada: {data["duracao_falada"]} ({data["duracao_falada_segundos"]} segundos)
Preço: R$ {data["preco"]}

🎙️ Gravação:
{data["url_gravacao"]}

Ramal ID: {data["ramal_id"]}
Tags: {data["tags"]}
Gravações Parciais: {data["gravacoes_parciais"]}
"""

try:
    msg = MIMEText(corpo)
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
