import pymysql
import logging

def get_db_connection():
    return pymysql.connect(
  charset="utf8mb4",
  connect_timeout=10,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  host="sqldeliciahaha2-manelreidelas.e.aivencloud.com",
  password="AVNS_8QxSpDvas-NUiG6m5CY",
  read_timeout=10,
  port=21948,
  user="avnadmin",
  write_timeout=10,
)

logging.basicConfig(
    filename="error_db.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def save_user(user_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if not user_data.get("id") or not user_data.get("email"):
            logging.error("ID ou email ausente: %s", user_data)
            return

        cursor.execute("SELECT 1 FROM usuarios WHERE id = %s", (user_data["id"],))
        if cursor.fetchone():
            return

        cursor.execute("""
            INSERT INTO usuarios (id, nome, email, foto, cargo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_data.get("id"),
            user_data.get("name"),
            user_data.get("email"),
            user_data.get("picture"),
            user_data.get("cargo")
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        logging.error("Erro ao salvar usuário: %s", e, exc_info=True)
    finally:
        cursor.close()
        conn.close()

def buscar_usuario(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r

def get_role(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cargo FROM usuarios WHERE id = %s", (user_id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["cargo"] if r else None

def pegar_no_nome(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE id = %s", (id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["nome"] if r else None

def check_team(turma):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE turmano = %s", (turma,))
    r = cursor.fetchall()
    cursor.close()
    conn.close()
    return r


def buscar_email(nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM usuarios WHERE nome = %s", (nome,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["email"] if r else None

def buscar_nome_secretaria():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE cargo = 'Secretaria'")
    r = [x["nome"] for x in cursor.fetchall()]
    cursor.close()
    conn.close()
    return r

    
def buscar_nome_professor():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE cargo = 'Professor'")
    r = [x["nome"] for x in cursor.fetchall()]
    cursor.close()
    conn.close()
    return r

    
def buscar_nome_aluno():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT turmano, nome FROM usuarios")
    rows = cursor.fetchall()
    conn.close()

    alunos = {}
    for r in rows:
        if r["turmano"] not in alunos:
            alunos[r["turmano"]] = []
        alunos[r["turmano"]].append(r["nome"])
    return alunos


def usuario_tem_pin(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pin FROM usuarios WHERE id = %s", (user_id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return bool(r and r["pin"])


def cadastrar_pin(id, pin, escola, ano, turma, turmano):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET pin=%s, escola=%s, ano=%s, turma=%s, turmano=%s
        WHERE id=%s
    """, (pin, escola, ano, turma, turmano, id))
    conn.commit()
    cursor.close()
    conn.close()

def mudar_turma(id, ano, turma, turmano):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET ano=%s, turma=%s, turmano=%s
            WHERE id=%s
        """, (ano, turma, turmano, id))
        conn.commit()
        return "Sucesso"
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

def can_chance_team(turmano):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM lista_turmas WHERE ano_serie = %s", (turmano,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return "Sucesso" if r else "Erro"


def check_pin(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pin FROM usuarios WHERE id=%s", (user_id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["pin"] if r else None
    
def novo_pin(pin, nome, turma):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET pin=%s
        WHERE nome=%s AND turmano=%s
    """, (pin, nome, turma))
    conn.commit()
    cursor.close()
    conn.close()

def novo_pin_secretaria(pin, nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET pin=%s WHERE nome=%s", (pin, nome))
    conn.commit()
    cursor.close()
    conn.close()


def listar_alunose(ano=None, serie=None):
    query = "SELECT nome, turma, email, ano, id FROM usuarios WHERE cargo='Aluno'"
    params = []

    if ano and ano != "Todos":
        query += " AND ano=%s"
        params.append(ano)

    if serie and serie != "Todos":
        query += " AND turma=%s"
        params.append(serie)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    r = cursor.fetchall()
    cursor.close()
    conn.close()
    return r


