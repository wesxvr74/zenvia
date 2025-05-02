import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

EMAIL_ORIGEM = os.getenv("EMAIL_ORIGEM")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()

    # Mapeamento de ramal_id para fila
    ramais_para_filas = {
        542643: "SUPORTE", 542644: "SUPORTE", 542645: "SUPORTE", 542646: "SUPORTE",
        542647: "SUPORTE", 579906: "SUPORTE", 542649: "SUPORTE",
        542650: "FINANCEIRO", 542655: "FINANCEIRO", 871082: "FINANCEIRO", 542639: "FINANCEIRO",
        542651: "COMERCIAL", 542652: "COMERCIAL", 542653: "COMERCIAL",
        753881: "COMERCIAL", 769308: "COMERCIAL", 1038705: "COMERCIAL",
        1040106: "COMERCIAL", 1040121: "COMERCIAL"
    }

    ramal_id = data["ramal_id"]
    fila = ramais_para_filas.get(ramal_id, "INDEFINIDA")

    try:
        assunto = "Notificação de Chamada Finalizada"
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

Fila: {fila}
Ramal ID: {ramal_id}
Tags: {data["tags"]}
Gravações Parciais: {data["gravacoes_parciais"]}
"""

        msg = MIMEText(corpo)
        msg["Subject"] = assunto
        msg["From"] = EMAIL_ORIGEM
        msg["To"] = EMAIL_DESTINO

        with smtplib.SMTP_SSL("smtp.hostinger.com", 465) as smtp:
            smtp.login(EMAIL_ORIGEM, EMAIL_SENHA)
            smtp.send_message(msg)

        return jsonify({"status": "email enviado"}), 200

    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "API de Callback da Zenvia está rodando!", 200

if __name__ == "__main__":
    app.run(debug=True, port=8080)
