"""
Módulo responsável por interações com o Google Drive.
"""

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = 'credenciais_google.json'
FOLDER_ID_PRINCIPAL = '1fku1KbTUNKTnTBOIpk4b3_FHUfXe78YV'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive"]
)
service = build('drive', 'v3', credentials=credentials, cache_discovery=False)

def criar_pasta_drive(nome):
    """Cria uma nova pasta no Drive dentro da pasta principal."""
    pasta = service.files().create(  # pylint: disable=no-member
        body={
            'name': nome,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [FOLDER_ID_PRINCIPAL]
        },
        fields='id'
    ).execute()  # pylint: disable=no-member
    return pasta['id']

def obter_link_pasta(pasta_id):
    """Gera link público para a pasta do Google Drive."""
    return f"https://drive.google.com/drive/folders/{pasta_id}"

def apagar_pasta_drive(pasta_id):
    """Tenta apagar a pasta do Drive com base no ID."""
    try:
        service.files().delete(fileId=pasta_id).execute()  # pylint: disable=no-member
        return True
    except HttpError as e:
        print(f"Erro ao apagar pasta: {e}")
        return False

def upload_drive(file_path, descricao, pasta_id):
    """Faz upload de imagem no Drive e retorna link público."""
    nome_arquivo = f"{descricao}_{pasta_id}_{os.path.basename(file_path)}"
    metadata = {'name': nome_arquivo, 'parents': [pasta_id]}
    media = MediaFileUpload(file_path, mimetype='image/jpeg')

    arquivo = service.files().create(  # pylint: disable=no-member
        body=metadata,
        media_body=media,
        fields='id'
    ).execute()  # pylint: disable=no-member

    link = f"https://drive.google.com/file/d/{arquivo['id']}/view"
    return link
