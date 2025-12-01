import sqlite3

# iniciar banco de dados de login
def init_db():
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                nome TEXT,
                email TEXT,
                foto TEXT,
                cargo TEXT,
                pin INTEGER,
                escola TEXT, 
                ano INTEGER,
                turma TEXT,
                turmano TEXT
            )
        """)
        conn.commit()

# salvar usuario aluno
def salvar_usuario(user_data):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        print(user_data["email"])
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_data["id"],))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO usuarios (id, nome, email, foto, cargo) VALUES (?, ?, ?, ?, ?)",
                (user_data["id"], user_data["name"], user_data["email"], user_data["picture"], user_data["cargo"])
            )
            conn.commit()

# aqui vai buscar usuario
def buscar_usuario(user_id):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        return cursor.fetchone()

# buscar os cargos e verificar qual é o cargo do usuario atual, se é aluno ou professor ou secretaria
def buscar_cargo(user_id):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cargo FROM usuarios WHERE id = ?", (user_id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None

def pegar_no_nome(id):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    
def buscar_nome_secretaria():
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE cargo = 'Secretaria'")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    
def buscar_nome_professor():
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE cargo = 'Professor'")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    
def buscar_nome_aluno():
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT turmano, nome FROM usuarios")
        rows = cursor.fetchall()

    alunos_por_turma = {}
    for turmano, nome in rows:
        if not turmano or not nome:
            continue
        if turmano not in alunos_por_turma:
            alunos_por_turma[turmano] = []
        alunos_por_turma[turmano].append(nome)
    return alunos_por_turma

def usuario_tem_pin(user_id):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pin FROM usuarios WHERE id = ?", (user_id,))
        resultado = cursor.fetchone()
        # Retorna True se o usuário tiver um pin, False se não tiver
        return bool(resultado and resultado[0] is not None)

def cadastrar_pin(id, pin, escola, ano, turma, turmano):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET pin = ?, escola = ?, ano = ?, turma = ?, turmano = ?
            WHERE id = ?
        """, (pin, escola, ano, turma, turmano, id))
        conn.commit()


def check_pin(user_id):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pin FROM usuarios WHERE id = ?", (user_id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    
def novo_pin(pin, nome, turma):
    with sqlite3.connect("usuarios.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET pin = ?
                WHERE nome = ?
                AND turma = ?
            """, (pin,nome,turma))
            conn.commit()

def novo_pin_secretaria(pin, nome):
    with sqlite3.connect("usuarios.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET pin = ?
                WHERE nome = ?
            """, (pin,nome))
            conn.commit()

def listar_alunose(ano=None, serie=None):
    query = "SELECT nome, turma, email, ano FROM usuarios WHERE cargo = 'Aluno'"
    params = []

    # Aplica filtros dinamicamente
    if ano and ano != "Todos":
        query += " AND ano = ?"
        params.append(ano)

    if serie and serie != "Todos":
        query += " AND turma = ?"
        params.append(serie)

    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

