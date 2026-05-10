import pymysql
import logging
from datetime import datetime, timedelta

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

    
def buscar_nome_aluno(escola=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT turmano, nome FROM usuarios WHERE cargo = 'Aluno'"
    params = []
    
    if escola:
        query += " AND escola = %s"
        params.append(escola)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
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

def calcular_fim_suspensao(tempo):
    agora = datetime.now()

    if tempo == "3_dias":
        return agora + timedelta(days=3), "temporaria"

    if tempo == "5_dias":
        return agora + timedelta(days=5), "temporaria"

    if tempo == "10_dias":
        return agora + timedelta(days=10), "temporaria"

    if tempo == "1_mes":
        return agora + timedelta(days=30), "temporaria"

    if tempo == "permanente":
        return None, "permanente"

    return None, None

def buscar_aluno_por_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, ano, turma, turmano, cargo,
               suspenso, motivo_suspensao, data_suspensao,
               fim_suspensao, tipo_suspensao
        FROM usuarios
        WHERE id = %s AND cargo = 'Aluno'
    """, (id,))

    aluno = cursor.fetchone()

    cursor.close()
    conn.close()

    return aluno


def calcular_fim_suspensao(tempo):
    agora = datetime.now()

    if tempo == "3_dias":
        return agora + timedelta(days=3), "temporaria"

    if tempo == "5_dias":
        return agora + timedelta(days=5), "temporaria"

    if tempo == "10_dias":
        return agora + timedelta(days=10), "temporaria"

    if tempo == "1_mes":
        return agora + timedelta(days=30), "temporaria"

    if tempo == "permanente":
        return None, "permanente"

    return None, None


def buscar_aluno_por_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, ano, turma, turmano, cargo,
               suspenso, motivo_suspensao, data_suspensao,
               fim_suspensao, tipo_suspensao,
               suspenso_por_id, suspenso_por_nome, suspenso_por_email,
               matricula_ativa
        FROM usuarios
        WHERE id = %s AND cargo = 'Aluno'
    """, (id,))

    aluno = cursor.fetchone()

    cursor.close()
    conn.close()

    return aluno


def buscar_status_suspensao(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, cargo, matricula_ativa,
               suspenso, motivo_suspensao, data_suspensao,
               fim_suspensao, tipo_suspensao,
               suspenso_por_id, suspenso_por_nome, suspenso_por_email,
               email_fim_suspensao_enviado
        FROM usuarios
        WHERE id = %s
    """, (user_id,))

    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    return usuario


def suspender_user(aluno_id, motivo, tempo, suspensor):
    conn = get_db_connection()
    cursor = conn.cursor()

    agora = datetime.now()
    fim_suspensao, tipo_suspensao = calcular_fim_suspensao(tempo)

    if tipo_suspensao is None:
        cursor.close()
        conn.close()
        return False

    cursor.execute("""
        UPDATE usuarios
        SET suspenso = %s,
            motivo_suspensao = %s,
            data_suspensao = %s,
            fim_suspensao = %s,
            tipo_suspensao = %s,
            suspenso_por_id = %s,
            suspenso_por_nome = %s,
            suspenso_por_email = %s,
            email_fim_suspensao_enviado = 0
        WHERE id = %s AND cargo = 'Aluno'
    """, (
        1,
        motivo,
        agora,
        fim_suspensao,
        tipo_suspensao,
        suspensor["id"],
        suspensor["nome"],
        suspensor["email"],
        aluno_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return True


def remover_suspensao_user(aluno_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET suspenso = 0,
            motivo_suspensao = NULL,
            data_suspensao = NULL,
            fim_suspensao = NULL,
            tipo_suspensao = NULL,
            suspenso_por_id = NULL,
            suspenso_por_nome = NULL,
            suspenso_por_email = NULL,
            email_fim_suspensao_enviado = 0
        WHERE id = %s AND cargo = 'Aluno'
    """, (aluno_id,))

    conn.commit()
    cursor.close()
    conn.close()


def finalizar_suspensao_expirada(aluno_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET suspenso = 0,
            motivo_suspensao = NULL,
            data_suspensao = NULL,
            fim_suspensao = NULL,
            tipo_suspensao = NULL,
            suspenso_por_id = NULL,
            suspenso_por_nome = NULL,
            suspenso_por_email = NULL,
            email_fim_suspensao_enviado = 1
        WHERE id = %s
    """, (aluno_id,))

    conn.commit()
    cursor.close()
    conn.close()


def alterar_matricula_ativa(aluno_id, ativo):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET matricula_ativa = %s
        WHERE id = %s AND cargo = 'Aluno'
    """, (1 if ativo else 0, aluno_id))

    conn.commit()
    cursor.close()
    conn.close()


def listar_alunose(ano=None, serie=None, escola=None):
    query = """
        SELECT nome, turma, email, ano, id, suspenso, matricula_ativa, escola
        FROM usuarios
        WHERE cargo = 'Aluno'
    """

    params = []

    if ano and ano != "Todos":
        query += " AND ano = %s"
        params.append(ano)

    if serie and serie != "Todos":
        query += " AND turma = %s"
        params.append(serie)

    if escola:
        query += " AND escola = %s"
        params.append(escola)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    r = cursor.fetchall()
    cursor.close()
    conn.close()

    return r

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


def alterar_escola_aluno(aluno_id, nova_escola):
    """Altera a escola de um aluno. Deve ser validado em rota que apenas secretaria pode fazer."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET escola=%s
            WHERE id=%s AND cargo='Aluno'
        """, (nova_escola, aluno_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return False

