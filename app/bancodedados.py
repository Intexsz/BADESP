import sqlite3
from datetime import datetime

def criar_tabela():
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            gravidade TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data TEXT NOT NULL,
            user_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_db():
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                nome TEXT,
                email TEXT,
                foto TEXT
            )
        """)
        conn.commit()

def salvar_usuario(user_data):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_data["id"],))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO usuarios (id, nome, email, foto) VALUES (?, ?, ?, ?)",
                (user_data["id"], user_data["name"], user_data["email"], user_data["picture"])
            )
            conn.commit()

def buscar_usuario(user_id):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        return cursor.fetchone()

def criar_denuncia(titulo, gravidade, descricao, user_id):
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO denuncias (titulo, gravidade, descricao, data, user_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (titulo, gravidade, descricao, data, user_id))
    conn.commit()
    conn.close()

def mostrar_denuncias(user_id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, titulo, gravidade, descricao, data
        FROM denuncias
        WHERE user_id = ?
        ORDER BY id DESC
    ''', (user_id,))
    denuncias = cursor.fetchall()
    conn.close()
    return denuncias

def apagar_denuncia(id, user_id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM denuncias WHERE id = ? AND user_id = ?', (id, user_id))
    conn.commit()
    conn.close()
