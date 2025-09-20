import sqlite3
from datetime import datetime, timedelta
from app.bancodedadosusuario import buscar_usuario

# iniciar banco de dados de denuncia
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
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            nome TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# aqui ira criar a denuncia
def criar_denuncia(titulo, gravidade, descricao, user_id, status, nome):
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = sqlite3.connect('denuncias.db')
    usuario = buscar_usuario(user_id)
    usuario_dict = {
    "id": usuario[0],
    "nome": usuario[1],
    "email": usuario[2],
    "foto": usuario[3],
    "cargo": usuario[4]}
    nome = usuario_dict["nome"]
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO denuncias (titulo, gravidade, descricao, data, user_id, status, nome)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (titulo, gravidade, descricao, data, user_id, status, nome))
    conn.commit()
    conn.close()

# aqui vai pegar as denuncias e retornar
def mostrar_denuncias(user_id, cargo):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    
    if cargo == "Secretaria":
        cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome
            FROM denuncias
            WHERE status != "Expirada."
            ORDER BY id DESC
        ''')
    else:
        cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome
            FROM denuncias
            WHERE user_id = ?
            ORDER BY id DESC
        ''', (user_id,))
    
    denuncias = cursor.fetchall()
    conn.close()
    return denuncias

# aqui é apagar as denuncias
def apagar_denuncia(id, user_id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM denuncias WHERE id = ? AND user_id = ?', (id, user_id))
    conn.commit()
    conn.close()

# aqui vai buscar o status da denuncia
def buscar_status_denuncia(id, user_id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM denuncias WHERE id = ? AND user_id = ?', (id, user_id))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# aqui vai ser aonde o status vai expirar quaso a denuncia fique parada durante 7 dias
def expirar():
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, data, status FROM denuncias')
    denuncias = cursor.fetchall()
    for d in denuncias:
        id_denuncia, data_str, status = d
        if status != "Em Análise.":
            continue

        created_at = datetime.strptime(data_str, "%d/%m/%Y %H:%M")
        if datetime.now() > created_at + timedelta(days=7):
            cursor.execute(
                'UPDATE denuncias SET status = ? WHERE id = ?',
                ("Expirada.", id_denuncia)
            )
    conn.commit()
    conn.close()


def abrir_denunciabanquinho(id, cargo):
    # se não for secretaria, vaza
    if cargo != "Secretaria":
        return

    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    # tualize
    cursor.execute(
        'UPDATE denuncias SET status = ? WHERE id = ? AND status != ?',
        ("Visto.", id, "Expirada.")
    )
    
    conn.commit()
    conn.close()

