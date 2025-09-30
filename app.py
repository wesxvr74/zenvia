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

@app.route("/meuip", methods=["GET"])
def meu_ip():
    import requests
    ip = requests.get("https://api.ipify.org").text
    return f"Meu IP externo é: {ip}", 200
    

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
def processar_callbacks():
    registros = collection.find({"processado": False})
    enviados = 0

    for data in registros:
        fila = ramais_para_filas.get(data.get("ramal_id"), "INDEFINIDA")

        payload = {
            "id": data.get("id"),
            "status": data.get("status"),
            "numero_origem": data.get("numero_origem"),
            "numero_destino": data.get("numero_destino"),
            "data_inicio": data.get("data_inicio"),
            "duracao": data.get("duracao"),
            "duracao_segundos": data.get("duracao_segundos"),
            "duracao_cobrada": data.get("duracao_cobrada"),
            "duracao_cobrada_segundos": data.get("duracao_cobrada_segundos"),
            "duracao_falada": data.get("duracao_falada"),
            "duracao_falada_segundos": data.get("duracao_falada_segundos"),
            "preco": data.get("preco"),
            "url_gravacao": data.get("url_gravacao"),
            "fila": fila,
            "ramal_id": data.get("ramal_id"),
            "tags": data.get("tags"),
            "gravacoes_parciais": data.get("gravacoes_parciais")
        }

        try:
            response = requests.post(
                f"{AWS_ENDPOINT}?token={AWS_TOKEN}",
                json=payload,
                timeout=10
            )
            response.raise_for_status()  # Gera exceção se status != 2xx

            # Marca como processado
            collection.update_one({"_id": data["_id"]}, {"$set": {"processado": True}})
            enviados += 1

        except Exception as e:
            print("Erro ao enviar para Lambda:", e)

    return {"status": f"{enviados} callback(s) enviado(s) para Lambda."}, 200
