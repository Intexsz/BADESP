import sqlite3
from datetime import datetime, timedelta
from app.database.db_usuario import buscar_usuario, pegar_no_nome

# iniciar banco de dados de denuncia
def criar_tabela():
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            tipo TEXT,
            gravidade TEXT NOT NULL,
            descricao TEXT NOT NULL,
            descricao_ia TEXT,
            comentario TEXT,
            data TEXT NOT NULL,
            datavisto TEXT,
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            cargo TEXT,
            nome TEXT NOT NULL,
            visto TEXT,
            especifico TEXT
        )
    ''')
    # OBS: gravidade e tipo estão trocados de lugar (quando for fazer o gravidade com IA arrumar isso)
    conn.commit()
    conn.close()

# aqui ira criar a denuncia
def criar_denuncia(titulo, gravidade, descricao, user_id, status, cargo, especifico):
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
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO denuncias (titulo, gravidade, descricao, data, user_id, status, nome, visto, comentario, cargo, especifico)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (titulo, gravidade, descricao, data, user_id, status, nome, 'Ninguém', '', cargo, especifico))
    conn.commit()
    conn.close()

# aqui vai pegar as denuncias e retornar
def mostrar_denuncias(user_id, cargo, tipo):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    nomezin = pegar_no_nome(user_id)

    if tipo != 'Tudo':
        if cargo == "Secretaria":
            cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, cargo, comentario, datavisto, especifico
            FROM denuncias
            WHERE status != "Expirada."
              AND (cargo = 'Secretaria' OR cargo = 'Ambos')
              AND status = ?
              AND especifico IN (?, "any")
            ORDER BY id DESC
        ''', (tipo,nomezin,))
        elif cargo == 'Aluno':
            cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, comentario, datavisto
            FROM denuncias
            WHERE user_id = ? AND status = ?
            ORDER BY id DESC
        ''', (user_id,tipo,))
        elif cargo == 'Professor':
            cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, cargo, comentario, datavisto
            FROM denuncias
            WHERE status != "Expirada."
              AND (cargo = 'Professor' OR cargo = 'Ambos')
              AND status = ?
              AND especifico IN (?, "any")
            ORDER BY id DESC
        ''', (tipo,nomezin,))
        denuncias = cursor.fetchall()
        conn.close()
        return denuncias

    elif tipo == 'Tudo':
        if cargo == "Secretaria":
            cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, cargo, comentario, datavisto
            FROM denuncias
            WHERE status != "Expirada."
              AND (cargo = 'Secretaria' OR cargo = 'Ambos')
              AND especifico IN (?, "any")
            ORDER BY id DESC
        ''', (nomezin,))
        elif cargo == 'Aluno':
            cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, comentario, datavisto
            FROM denuncias
            WHERE user_id = ?
            ORDER BY id DESC
        ''', (user_id,))
        elif cargo == 'Professor':
            cursor.execute('''
            SELECT id, titulo, gravidade, descricao, data, status, nome, visto, cargo, comentario, datavisto
            FROM denuncias
            WHERE status != "Expirada."
              AND (cargo = 'Professor' OR cargo = 'Ambos')
              AND especifico IN (?, "any")
            ORDER BY id DESC
        ''', (nomezin,))
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

        if status != "Visto." or not data_str:
            continue

        data_visto = datetime.strptime(data_str, "%d/%m/%Y %H:%M")

        # expira 7 segundos depois de ter sido vista
        if datetime.now() > data_visto + timedelta(days=7):
            cursor.execute(
                'UPDATE denuncias SET status = ? WHERE id = ? AND status = ?',
                ("Expirada.", id_denuncia, 'Visto.')
            )

    conn.commit()
    conn.close()

# checa se o usuario ja criou uma denuncia a menos de 30 minutos -feito com ajuda de IA
def checagem_denunciahehe(user_id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()

    # Pega a data/hora da última denúncia criada pelo usuário
    cursor.execute('SELECT data FROM denuncias WHERE user_id = ? ORDER BY data DESC LIMIT 1', (user_id,))
    resultado = cursor.fetchone()
    conn.close()

    if not resultado:
        return True  # nunca criou denúncia, pode criar

    ultima_data_str = resultado[0]
    ultima_data = datetime.strptime(ultima_data_str, "%d/%m/%Y %H:%M")

    # Checa se passaram 30 minutos desde a última denúncia para evitar spam
    return datetime.now() >= ultima_data + timedelta(seconds=3)
######----------######

# aqui é quando ele abre a denuncia, deixando ela em Visto.
def abrir_denunciabanquinho(id, cargo, nome, id_user):
    # se não for secretaria, vaza
    if cargo != "Secretaria" and cargo != "Professor":
        return
    # se o nome especificado por diferente, retorne
    especifico = buscar_especifico(id)
    nome_usuario = pegar_no_nome(id_user)

    if especifico != 'any' and especifico != nome_usuario:
        return
    data = datetime.now().strftime("%d/%m/%Y %H:%M") 
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    # seleciona o datavisto
    cursor.execute("""
        SELECT datavisto
        FROM denuncias
        WHERE id = ?
    """, (id,))
    row = cursor.fetchone()
    
    # atualiza o status para VISTO no id se o status for diferente de expirado
    cursor.execute(
        'UPDATE denuncias SET status = ? WHERE id = ? AND status = ?',
        ("Visto.", id, 'Em Análise.')
    )
    
    cursor.execute(
    'UPDATE denuncias SET visto = ? WHERE id = ? AND visto = ?',
    (nome, id, 'Ninguém')
    )

    # verifica se datavisto não for None e atualiza o datavisto quaso não exista
    if not row[0] or row[0] == '':
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
        SELECT id, titulo, gravidade, descricao, data, status, nome, visto, comentario, tipo, cargo, datavisto, especifico
        FROM denuncias
        WHERE id = ?
    """, (id,))

    row = cursor.fetchone()
    conn.close()

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
            'tipo': row[9],
            'cargo': row[10],
            'datavisto': row[11],
            'especifico': row[12]
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

def atualizar_statuse(id, cargo, novo, id_user):
    # se não for secretaria, vaza
    if cargo != "Secretaria" and cargo != "Professor":
        return
    # se não for o nome especifico, vaza
    especifico = buscar_especifico(id)
    nome_usuario = pegar_no_nome(id_user)
    
    if especifico != 'any' and especifico != nome_usuario:
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

def publicar_comentario(comentario, id, cargo, id_user):
    # se não for secretaria, vaza
    if cargo != "Secretaria" and cargo != "Professor":
        return
    # se não for nome especifico, vaza
    especifico = buscar_especifico(id)
    nome_usuario = pegar_no_nome(id_user)
    
    if especifico != 'any' and especifico != nome_usuario:
        return
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE denuncias SET comentario = ? WHERE id = ?',
        (comentario, id)
    )
    
    conn.commit()
    conn.close()

def buscar_especifico(id):
    conn = sqlite3.connect('denuncias.db')
    cursor = conn.cursor()
    cursor.execute('SELECT especifico FROM denuncias WHERE id = ?', (id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None