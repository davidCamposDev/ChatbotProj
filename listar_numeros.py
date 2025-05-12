import requests

ID_INSTANCE = '7105229253'
API_TOKEN = 'c80460a47c8e4cf1ae808d69f4afa34b8299e13e83414d74b8'

url = f'https://api.green-api.com/waInstance{ID_INSTANCE}/getSettings/{API_TOKEN}'

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Extrair lista de correspondents (números permitidos)
    correspondents = data.get("correspondents", []) 

    if correspondents:
        print("📱 Números autorizados atualmente:")
        for numero in correspondents:
            print(f"✔️ {numero}")
    else:
        print("⚠️ Nenhum número está autorizado atualmente.")
except Exception as e:
    print(f"❌ Erro ao consultar a Green-API: {e}")
