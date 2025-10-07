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
                pin INTEGER
            )
        """)
        conn.commit()

# salvar usuario aluno
def salvar_usuario(user_data):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
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

