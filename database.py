import sqlite3

db = sqlite3.connect('imagens.db', check_same_thread=False)
cursor = db.cursor()

def obter_id_pasta(nome_pasta, telefone):
    cursor.execute("SELECT id_drive FROM pastas WHERE nome = ? AND telefone = ?", (nome_pasta, telefone))
    row = cursor.fetchone()
    return row[0] if row else None

def listar_pastas_usuario(telefone):
    cursor.execute("SELECT nome FROM pastas WHERE telefone = ?", (telefone,))
    return [row[0] for row in cursor.fetchall()]