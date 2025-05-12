import requests
import logging

ID_INSTANCE = '7105229253'
API_TOKEN = 'c80460a47c8e4cf1ae808d69f4afa34b8299e13e83414d74b8'

logger = logging.getLogger(__name__)

def enviar_mensagem(telefone, mensagem):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": f"{telefone}@c.us",
        "message": mensagem
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error("❌ Erro ao enviar mensagem: %s", e)