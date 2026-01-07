import sqlite3
import logging

# iniciar banco de dados de login
def init_db():
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
# Configura logging para produção
logging.basicConfig(filename='error_db.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def save_user(user_data):
    try:
        with sqlite3.connect("usuarios.db") as conn:
            cursor = conn.cursor()

            # Confere se os campos obrigatórios existem
            if not user_data.get("id") or not user_data.get("email"):
                logging.error("ID ou email ausente em user_data: %s", user_data)
                return

            # Verifica se o usuário já existe
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_data["id"],))
            if cursor.fetchone():
                logging.info("Usuário já existe: %s", user_data["email"])
                return

            # Insere novo usuário
            cursor.execute(
                "INSERT INTO usuarios (id, nome, email, foto, cargo) VALUES (?, ?, ?, ?, ?)",
                (
                    user_data.get("id"),
                    user_data.get("name"),
                    user_data.get("email"),
                    user_data.get("picture"),
                    user_data.get("cargo")
                )
            )
            conn.commit()
            logging.info("Usuário salvo com sucesso: %s", user_data["email"])

    except sqlite3.IntegrityError as e:
        # ID duplicado ou outra violação de integridade
        logging.warning("Tentativa de inserir usuário já existente: %s - %s", user_data, e)

    except sqlite3.OperationalError as e:
        # Problema com o banco (ex: locked)
        logging.error("Erro operacional no SQLite: %s - %s", user_data, e, exc_info=True)

    except Exception as e:
        # Qualquer outro erro
        logging.error("Erro desconhecido ao salvar usuário: %s - %s", user_data, e, exc_info=True)
# aqui vai buscar usuario
def buscar_usuario(user_id):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        return cursor.fetchone()

# buscar os cargos e verificar qual é o cargo do usuario atual, se é aluno ou professor ou secretaria
def get_role(user_id):
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

def check_team(turma):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE turmano = ?", (turma,))
        resultado = cursor.fetchall()
        return resultado if resultado else None

def buscar_email(nome):
    with sqlite3.connect('usuarios.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM usuarios WHERE nome = ?', (nome,))
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

def mudar_turma(id, ano, turma, turmano):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET ano = ?, turma = ?, turmano = ?
            WHERE id = ?
        """, (ano, turma, turmano, id))
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
    query = "SELECT nome, turma, email, ano, id FROM usuarios WHERE cargo = 'Aluno'"
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

