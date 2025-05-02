from flask import Flask, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# Variáveis de ambiente para o e-mail
EMAIL_ORIGEM = os.getenv("EMAIL_ORIGEM")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()
    
    # Formata o corpo do e-mail
    corpo = f"""
    📞 Nova Chamada Finalizada

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
    
    # Assunto do e-mail
    assunto = "Notificação de Chamada Finalizada"
    
    # Criação do e-mail
    msg = MIMEText(corpo)
    msg["Subject"] = assunto
    msg["From"] = EMAIL_ORIGEM
    msg["To"] = EMAIL_DESTINO
    
    # Envio do e-mail
    try:
        with smtplib.SMTP_SSL("smtp.hostinger.com", 465) as server:
            server.login(EMAIL_ORIGEM, EMAIL_SENHA)
            server.sendmail(EMAIL_ORIGEM, EMAIL_DESTINO, msg.as_string())
        return "E-mail enviado com sucesso!", 200
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return "Erro ao enviar e-mail", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
