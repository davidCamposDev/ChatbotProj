import logging
from flask import Flask, request
from handlers import processar_webhook

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    return processar_webhook(request)

if __name__ == '__main__':
    logger.info("[FLASK] Servidor iniciado na porta 5000...")
    app.run(port=5000)