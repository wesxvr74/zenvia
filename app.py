from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
import os
import traceback
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Configurações de e-mail
EMAIL_ORIGEM = os.environ.get("EMAIL_ORIGEM")
EMAIL_SENHA = os.environ.get("EMAIL_SENHA")
EMAIL_DESTINO = "delpim@desk.ms"
SMTP_SERVIDOR = "smtp.hostinger.com"
SMTP_PORTA = 465

# Conexão MongoDB
MONGO_URI = os.environ.get("MONGODB_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.zenvia
collection = db.callbacks

# Mapeamento de ramal_id para fila
ramais_para_filas = {
    542643: "SUPORTE", 542644: "SUPORTE", 542645: "SUPORTE", 542646: "SUPORTE",
    542647: "SUPORTE", 579906: "SUPORTE", 542649: "SUPORTE",
    542650: "FINANCEIRO", 542655: "FINANCEIRO", 871082: "FINANCEIRO", 542639: "FINANCEIRO",
    542651: "COMERCIAL", 542652: "COMERCIAL", 542653: "COMERCIAL",
    753881: "COMERCIAL", 769308: "COMERCIAL", 1038705: "COMERCIAL",
    1040106: "COMERCIAL", 1040121: "COMERCIAL"
}

@app.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.json
        # Adiciona controle de processamento
        data["processado"] = False
        data["criado_em"] = datetime.utcnow()

        # Salvar no Mongo
        collection.insert_one(data)
        return jsonify({'message': 'Callback processado com sucesso'}), 200
    except Exception as e:
        print('Erro no callback:', e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route("/processar", methods=["GET"])
def processar_emails():
    # Buscar callbacks não processados
    registros = collection.find({"processado": False})

    enviados = 0
    for data in registros:
        fila = ramais_para_filas.get(data.get("ramal_id"), "INDEFINIDA")

        corpo = f"""
📞 Chamada TTS Recebida

ID: {data.get("id")}
Status: {data.get("status")}
Número de Origem: {data.get("numero_origem")}
Número de Destino: {data.get("numero_destino")}
Data de Início: {data.get("data_inicio")}
Duração: {data.get("duracao")} ({data.get("duracao_segundos")} segundos)
Duração Cobrada: {data.get("duracao_cobrada")} ({data.get("duracao_cobrada_segundos")} segundos)
Duração Falada: {data.get("duracao_falada")} ({data.get("duracao_falada_segundos")} segundos)
Preço: R$ {data.get("preco")}

🎙️ Gravação:
{data.get("url_gravacao")}

Fila: {fila}
Ramal ID: {data.get("ramal_id")}
Tags: {data.get("tags")}
Gravações Parciais: {data.get("gravacoes_parciais")}
"""

        try:
            msg = MIMEText(corpo)
            msg["Subject"] = "Notificação de Chamada Finalizada"
            msg["From"] = EMAIL_ORIGEM
            msg["To"] = EMAIL_DESTINO

            with smtplib.SMTP_SSL(SMTP_SERVIDOR, SMTP_PORTA) as servidor:
                servidor.login(EMAIL_ORIGEM, EMAIL_SENHA)
                servidor.send_message(msg)

            # Marca como processado
            collection.update_one({"_id": data["_id"]}, {"$set": {"processado": True}})
            enviados += 1

        except Exception as e:
            print("Erro ao enviar e-mail:", e)

    return {"status": f"{enviados} e-mail(s) enviado(s)."}, 200

@app.route("/", methods=["GET"])
def home():
    return "API de Callback da Zenvia ativa!", 200

if __name__ == "__main__":
    app.run(debug=True)
