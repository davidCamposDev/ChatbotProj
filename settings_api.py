import requests
from messaging import ID_INSTANCE, API_TOKEN

def listar_numeros_autorizados():
    url = f'https://api.green-api.com/waInstance{ID_INSTANCE}/getSettings/{API_TOKEN}'
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("correspondents", [])
