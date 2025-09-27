import sqlite3
from datetime import datetime, timedelta
from app.database.db_usuario import buscar_usuario

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
            comentario TEXT,
            comentario_ia TEXT,
            data TEXT NOT NULL,
            datavisto TEXT,
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            nome TEXT NOT NULL,
            visto TEXT,
            cargo TEXT,
            pin TEXT
        )
    ''')
    conn.commit()
    conn.close()

# aqui ira criar a denuncia
def criar_denuncia(titulo, gravidade, descricao, user_id, status):
    data = datetime.now().strftime("%d/%m/%Y %H:%M") # data de quando foi criada
    conn = sqlite3.connect('denuncias.db')
    usuario = buscar_usuario(user_id)
    usuario_dict = {
    "id": usuario[0],
    "nome": usuario[1],
    "email": usuario[2],
    "foto": usuario[3],
    "cargo": usuario[4]}
    nome = usuario_dict["nome"]
    cargo = usuario_dict['cargo']
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO denuncias (titulo, gravidade, descricao, data, user_id, status, nome, visto, comentario, comentario_ia, cargo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (titulo, gravidade, descricao, data, user_id, status, nome, 'Ninguém', '', '', cargo))
    conn.commit()
    conn.close()

# aqui vai pegar as denuncias e retornar
def mostrar_denuncias(user_id, cargo):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    
    if cargo == "Secretaria":
        cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, cargo, comentario
            FROM denuncias
            WHERE status != "Expirada."
            ORDER BY id DESC
        ''')
    elif cargo == 'Aluno':
        cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, comentario
            FROM denuncias
            WHERE user_id = ?
            ORDER BY id DESC
        ''', (user_id,))
    elif cargo == 'Professor':
        cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, comentario
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
def buscar_status_denuncia(id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM denuncias WHERE id = ?', (id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# aqui vai ser aonde o status vai expirar quaso a denuncia fique parada durante 7 dias
def expirar():
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, datavisto, status FROM denuncias')
    denuncias = cursor.fetchall()

    for d in denuncias:
        id_denuncia, data_str, status = d
        if status != "Visto.":
            continue

        created_at = datetime.strptime(data_str, "%d/%m/%Y %H:%M")
        if datetime.now() > created_at + timedelta(days=7):
            cursor.execute(
                'UPDATE denuncias SET status = ? WHERE id = ? AND status = ?',
                ("Expirada.", id_denuncia, 'Visto.')
            )
    conn.commit()
    conn.close()

# aqui é quando ele abre a denuncia, deixando ela em Visto.
def abrir_denunciabanquinho(id, cargo, nome):
    # se não for secretaria, vaza
    if cargo != "Secretaria":
        return
    
    data = datetime.now().strftime("%d/%m/%Y %H:%M") 
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    # atualiza o status para VISTO no id se o status for diferente de expirado
    cursor.execute(
        'UPDATE denuncias SET status = ? WHERE id = ? AND status = ?',
        ("Visto.", id, 'Em Análise.')
    )
    
    cursor.execute(
    'UPDATE denuncias SET visto = ? WHERE id = ? AND visto = ?',
    (nome, id, 'Ninguém')
    )

    cursor.execute(
    'UPDATE denuncias SET datavisto = ? WHERE id = ?',
    (data, id)
    )

    conn.commit()
    conn.close()

def pegar_na_denuncia_haha(id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, titulo, gravidade, descricao, data, status, nome, visto, comentario, comentario_ia, cargo
        FROM denuncias
        WHERE id = ?
    """, (id,))

    row = cursor.fetchone()
    conn.close()
    
    # Adicione este print para depurar
    print(f"Dados buscados do banco para denúncia ID {id}: {row}")

    if row:
        return {
            "id": row[0],
            "titulo": row[1],
            "gravidade": row[2],
            "descricao": row[3],
            "data": row[4],
            "status": row[5],
            "nome": row[6],
            'visto': row[7],
            'comentario': row[8],
            'comentario_ia': row[9],
            'cargo': row[10]
        }
    else:
        return 'no'

    
def buscar_visto(id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('SELECT visto FROM denuncias WHERE id = ?', (id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def buscar_comentario(id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('SELECT comentario FROM denuncias WHERE id = ?', (id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def atualizar_statuse(id, cargo, novo):
    # se não for secretaria, vaza
    if cargo != "Secretaria":
        return

    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    # atualiza o status para novo no id se o status for diferente de expirado
    cursor.execute(
        'UPDATE denuncias SET status = ? WHERE id = ? AND status != ?',
        (novo, id, "Expirada.")
    )
    
    conn.commit()
    conn.close()

def publicar_comentario(comentario, id, cargo):
    # se não for secretaria, vaza
    if cargo != "Secretaria":
        return

    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE denuncias SET comentario = ? WHERE id = ?',
        (comentario, id)
    )
    print(f'{comentario}')
    
    conn.commit()
    conn.close()