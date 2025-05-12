import os
import datetime
import logging
import requests
from werkzeug.utils import secure_filename
from database import db, cursor, obter_id_pasta, listar_pastas_usuario
from drive import criar_pasta_drive, apagar_pasta_drive, upload_drive, obter_link_pasta
from messaging import enviar_mensagem
from config import ALLOWED_NUMBERS  # importa lista de números permitidos

logger = logging.getLogger(__name__)


def processar_webhook(request):
    data = request.get_json()
    logger.info("📨 Webhook recebido: %s", data)

    # Apenas processa mensagens recebidas
    if data.get('typeWebhook') != 'incomingMessageReceived':
        return 'Ignorado', 200

    # Extrai telefone do remetente (sem '+' e '@c.us')
    telefone = data.get('senderData', {}).get('sender', '').replace('+', '').replace('@c.us', '')

    # Verifica se o telefone está autorizado
    if telefone not in ALLOWED_NUMBERS:
        logger.warning("Telefone não autorizado: %s", telefone)
        enviar_mensagem(telefone, "❌ Você não está autorizado a interagir com o bot.")
        return 'Número não autorizado', 200

    message_data = data.get('messageData', {})
    tipo = message_data.get('typeMessage')

    # 1️⃣ Recebe imagem
    if tipo == 'imageMessage':
        file_data = message_data.get('fileMessageData', {})
        media_url = file_data.get('downloadUrl')
        descricao = file_data.get('caption', 'Sem descrição')

        try:
            response = requests.get(media_url, timeout=10)
            response.raise_for_status()
            nome_arquivo = secure_filename(f"temp_{telefone}.jpg")

            # Verifica pendências
            cursor.execute(
                "SELECT id FROM temporarias WHERE telefone = ? AND status = 'pendente'",
                (telefone,)
            )
            if cursor.fetchone():
                enviar_mensagem(telefone, "❌ Você já tem uma imagem pendente de processamento.")
                return 'Imagem pendente', 200

            # Salva arquivo temporariamente
            with open(nome_arquivo, 'wb') as f:
                f.write(response.content)

            cursor.execute(
                "INSERT INTO temporarias (telefone, arquivo_local, descricao, status) VALUES (?, ?, ?, ?)",
                (telefone, nome_arquivo, descricao, 'pendente')
            )
            db.commit()

            enviar_mensagem(
                telefone,
                "📁 Deseja salvar em uma nova pasta ou uma existente? Responda: nova ou existente."
            )
            return 'Imagem salva temporariamente', 200

        except Exception as e:
            logger.error("Erro ao baixar imagem: %s", e)
            return 'Erro ao baixar imagem', 500

    # 2️⃣ Recebe texto
    if tipo == 'textMessage':
        mensagem = message_data.get('textMessageData', {}).get('textMessage', '').strip().lower()

        # Comandos de controle
        if mensagem in ['ajuda', 'comandos']:
            texto = (
                "📌 *Comandos disponíveis:*\n"
                "🧾 *listar pastas* — lista suas pastas.\n"
                "🗑️ *apagar pasta <nome>* — apaga a pasta.\n"
                "🔗 *<nome da pasta>* — link da pasta.\n"
                "📤 Envie uma *imagem* para iniciar.\n"
                "📂 Após imagem, responda: 'nova' ou 'existente'."
            )
            enviar_mensagem(telefone, texto)
            return 'Comando ajuda enviado', 200

        if mensagem == 'listar pastas':
            pastas = listar_pastas_usuario(telefone)
            if not pastas:
                enviar_mensagem(telefone, "📂 Você ainda não tem pastas criadas.")
            else:
                lista = '\n'.join(f"- {p}" for p in pastas)
                enviar_mensagem(telefone, f"*📁 Suas pastas:*\n{lista}")
            return 'Listando pastas', 200

        if mensagem.startswith('apagar pasta'):
            nome_pasta = mensagem.replace('apagar pasta', '').strip()
            id_pasta = obter_id_pasta(nome_pasta, telefone)
            if id_pasta and apagar_pasta_drive(id_pasta):
                cursor.execute(
                    "DELETE FROM pastas WHERE nome = ? AND telefone = ?",
                    (nome_pasta, telefone)
                )
                db.commit()
                enviar_mensagem(telefone, f"🗑️ Pasta '{nome_pasta}' apagada com sucesso.")
            else:
                enviar_mensagem(telefone, f"❌ Pasta '{nome_pasta}' não encontrada ou erro ao apagar.")
            return 'Apagar pasta', 200

        # Checa pendências de imagem
        cursor.execute(
            "SELECT id, arquivo_local, descricao FROM temporarias WHERE telefone = ? AND status = 'pendente'",
            (telefone,)
        )
        temp = cursor.fetchone()

        if temp:
            id_temp, caminho, descricao = temp

            if mensagem == 'nova':
                enviar_mensagem(telefone, "✏️ Informe o nome da nova pasta:")
                return 'Aguardando nome nova pasta', 200

            if mensagem == 'existente':
                pastas = listar_pastas_usuario(telefone)
                if not pastas:
                    enviar_mensagem(telefone, "📂 Nenhuma pasta criada. Envie 'nova'.")
                    return 'Sem pasta existente', 200
                lista = '\n'.join(f"- {p}" for p in pastas)
                enviar_mensagem(telefone, f"📁 Pastas:\n{lista}\nDigite o nome exato:")
                return 'Listando pastas', 200

            # Se digitar nome da pasta (existente ou nova)
            pasta_id = obter_id_pasta(mensagem, telefone)
            if pasta_id:
                link = upload_drive(caminho, descricao, pasta_id)
                enviar_mensagem(telefone, f"✅ Imagem salva em '{mensagem}': {link}")
            else:
                nova_id = criar_pasta_drive(mensagem)
                cursor.execute(
                    "INSERT INTO pastas (nome, id_drive, telefone) VALUES (?, ?, ?)",
                    (mensagem, nova_id, telefone)
                )
                db.commit()
                link = upload_drive(caminho, descricao, nova_id)
                enviar_mensagem(telefone, f"✅ Imagem salva na nova pasta '{mensagem}': {link}")

            os.remove(caminho)
            cursor.execute("UPDATE temporarias SET status = 'concluída' WHERE id = ?", (id_temp,))
            db.commit()
            return 'Upload feito', 200

        # Se for apenas nome de pasta (consulta de link)
        pasta_id = obter_id_pasta(mensagem, telefone)
        if pasta_id:
            link = obter_link_pasta(pasta_id)
            enviar_mensagem(telefone, f"📂 Link da pasta '{mensagem}': {link}")
            return 'Link enviado', 200

    return 'OK', 200
