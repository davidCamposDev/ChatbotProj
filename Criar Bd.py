import sqlite3
import subprocess
import os

DB_PATH = 'imagens.db'

def criar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Criar tabela imagens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS imagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        link TEXT,
        descricao TEXT,
        data TEXT
    )
    ''')

    # Criar tabela pastas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pastas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        id_drive TEXT,
        telefone TEXT
    )
    ''')

    # Criar tabela temporarias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS temporarias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telefone TEXT,
        arquivo_local TEXT,
        descricao TEXT,
        status TEXT DEFAULT 'pendente'  -- Adicionando coluna 'status'
    )
    ''')

    # Verificar se a coluna 'status' já existe (caso precise adicionar em banco existente)
    cursor.execute("PRAGMA table_info(temporarias);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'status' not in columns:
        cursor.execute('''
        ALTER TABLE temporarias ADD COLUMN status TEXT DEFAULT 'pendente'
        ''')

    conn.commit()
    conn.close()
    print("✅ Banco de dados verificado/criado com sucesso!")

def iniciar_app():
    print("🚀 Iniciando a aplicação Flask...")
    subprocess.run(["python", "app.py"])

if __name__ == "__main__":
    criar_banco()
    iniciar_app()
