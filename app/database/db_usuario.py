import logging
from datetime import datetime, timedelta
from app.database.db_site import get_conn as get_db_connection

logging.basicConfig(
    filename="error_db.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def close(cursor=None, conn=None):
    try:
        if cursor:
            cursor.close()
    except Exception:
        pass

    try:
        if conn:
            conn.close()
    except Exception:
        pass


def save_user(user_data):
    conn = None
    cursor = None
    
    try:
        if not user_data.get("id") or not user_data.get("email"):
            logging.error("ID ou email ausente: %s", user_data)
            return False

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT 1 FROM usuarios WHERE id = %s LIMIT 1",
            (user_data["id"],)
        )

        if cursor.fetchone():
            return True

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
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao salvar usuário: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def buscar_usuario(user_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, email, foto, cargo, pin,
                   escola, ano, turma, turmano,
                   matricula_ativa, suspenso, tipo_suspensao,
                   motivo_suspensao, data_suspensao, fim_suspensao,
                   suspenso_por_id, suspenso_por_nome, suspenso_por_email,
                   email_fim_suspensao_enviado
            FROM usuarios
            WHERE id = %s
            LIMIT 1
        """, (user_id,))

        return cursor.fetchone()

    finally:
        close(cursor, conn)


def get_role(user_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT cargo
            FROM usuarios
            WHERE id = %s
            LIMIT 1
        """, (user_id,))

        r = cursor.fetchone()
        return r["cargo"] if r else None

    finally:
        close(cursor, conn)


def pegar_no_nome(id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT nome
            FROM usuarios
            WHERE id = %s
            LIMIT 1
        """, (id,))

        r = cursor.fetchone()
        return r["nome"] if r else None

    finally:
        close(cursor, conn)


def check_team(turma):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT nome
            FROM usuarios
            WHERE turmano = %s
            ORDER BY nome
            LIMIT 300
        """, (turma,))

        return cursor.fetchall()

    finally:
        close(cursor, conn)


def buscar_email(nome):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT email
            FROM usuarios
            WHERE nome = %s
            LIMIT 1
        """, (nome,))

        r = cursor.fetchone()
        return r["email"] if r else None

    finally:
        close(cursor, conn)


def buscar_nome_secretaria():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT nome
            FROM usuarios
            WHERE cargo = %s
            ORDER BY nome
        """, ("Secretaria",))

        return [x["nome"] for x in cursor.fetchall()]

    finally:
        close(cursor, conn)


def buscar_nome_professor():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT nome
            FROM usuarios
            WHERE cargo = %s
            ORDER BY nome
        """, ("Professor",))

        return [x["nome"] for x in cursor.fetchall()]

    finally:
        close(cursor, conn)


def buscar_nome_aluno(escola=None):
    conn = None
    cursor = None

    try:
        query = """
            SELECT turmano, nome
            FROM usuarios
            WHERE cargo = %s
        """
        params = ["Aluno"]

        if escola:
            query += " AND escola = %s"
            params.append(escola)

        query += " ORDER BY turmano, nome LIMIT 1000"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        alunos = {}

        for r in rows:
            turmano = r["turmano"]

            if turmano not in alunos:
                alunos[turmano] = []

            alunos[turmano].append(r["nome"])

        return alunos

    finally:
        close(cursor, conn)


def usuario_tem_pin(user_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT pin
            FROM usuarios
            WHERE id = %s
            LIMIT 1
        """, (user_id,))

        r = cursor.fetchone()
        return bool(r and r["pin"])

    finally:
        close(cursor, conn)


def calcular_fim_suspensao(tempo):
    agora = datetime.now()

    tempos = {
        "3_dias": timedelta(days=3),
        "5_dias": timedelta(days=5),
        "10_dias": timedelta(days=10),
        "1_mes": timedelta(days=30),
    }

    if tempo in tempos:
        return agora + tempos[tempo], "temporaria"

    if tempo == "permanente":
        return None, "permanente"

    return None, None


def buscar_aluno_por_id(id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, email, ano, turma, turmano, cargo,
                   suspenso, motivo_suspensao, data_suspensao,
                   fim_suspensao, tipo_suspensao,
                   suspenso_por_id, suspenso_por_nome, suspenso_por_email,
                   matricula_ativa
            FROM usuarios
            WHERE id = %s AND cargo = %s
            LIMIT 1
        """, (id, "Aluno"))

        return cursor.fetchone()

    finally:
        close(cursor, conn)


def buscar_status_suspensao(user_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, email, cargo, matricula_ativa,
                   suspenso, motivo_suspensao, data_suspensao,
                   fim_suspensao, tipo_suspensao,
                   suspenso_por_id, suspenso_por_nome, suspenso_por_email,
                   email_fim_suspensao_enviado
            FROM usuarios
            WHERE id = %s
            LIMIT 1
        """, (user_id,))

        return cursor.fetchone()

    finally:
        close(cursor, conn)


def suspender_user(aluno_id, motivo, tempo, suspensor):
    conn = None
    cursor = None

    try:
        fim_suspensao, tipo_suspensao = calcular_fim_suspensao(tempo)

        if tipo_suspensao is None:
            return False

        agora = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

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
            WHERE id = %s AND cargo = %s
        """, (
            1,
            motivo,
            agora,
            fim_suspensao,
            tipo_suspensao,
            suspensor["id"],
            suspensor["nome"],
            suspensor["email"],
            aluno_id,
            "Aluno"
        ))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao suspender usuário: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def remover_suspensao_user(aluno_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

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
            WHERE id = %s AND cargo = %s
        """, (aluno_id, "Aluno"))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao remover suspensão: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def finalizar_suspensao_expirada(aluno_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

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
        return cursor.rowcount > 0

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao finalizar suspensão expirada: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def alterar_matricula_ativa(aluno_id, ativo):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            UPDATE usuarios
            SET matricula_ativa = %s
            WHERE id = %s AND cargo = %s
        """, (1 if ativo else 0, aluno_id, "Aluno"))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao alterar matrícula ativa: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def listar_alunose(ano=None, serie=None, escola=None):
    conn = None
    cursor = None

    try:
        query = """
            SELECT id, nome, turma, email, ano, suspenso, matricula_ativa, escola
            FROM usuarios
            WHERE cargo = %s
        """

        params = ["Aluno"]

        if ano and ano != "Todos":
            query += " AND ano = %s"
            params.append(ano)

        if serie and serie != "Todos":
            query += " AND turma = %s"
            params.append(serie)

        if escola:
            query += " AND escola = %s"
            params.append(escola)

        query += " ORDER BY nome LIMIT 500"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(query, params)
        return cursor.fetchall()

    finally:
        close(cursor, conn)

def cadastrar_pin(id, pin, escola, ano, turma, turmano):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            UPDATE usuarios
            SET pin = %s,
                escola = %s,
                ano = %s,
                turma = %s,
                turmano = %s
            WHERE id = %s
        """, (pin, escola, ano, turma, turmano, id))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao cadastrar PIN: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def mudar_turma(id, ano, turma, turmano):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            UPDATE usuarios
            SET ano = %s,
                turma = %s,
                turmano = %s
            WHERE id = %s
        """, (ano, turma, turmano, id))

        conn.commit()
        return "Sucesso"

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao mudar turma: %s", e, exc_info=True)
        return str(e)

    finally:
        close(cursor, conn)


def can_chance_team(turmano):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 1
            FROM lista_turmas
            WHERE ano_serie = %s
            LIMIT 1
        """, (turmano,))

        r = cursor.fetchone()
        return "Sucesso" if r else "Erro"

    finally:
        close(cursor, conn)


def check_pin(user_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT pin
            FROM usuarios
            WHERE id = %s
            LIMIT 1
        """, (user_id,))

        r = cursor.fetchone()
        return r["pin"] if r else None

    finally:
        close(cursor, conn)


def novo_pin(pin, nome, turma):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            UPDATE usuarios
            SET pin = %s
            WHERE nome = %s AND turmano = %s
        """, (pin, nome, turma))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao alterar PIN do aluno: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def novo_pin_secretaria(pin, nome):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            UPDATE usuarios
            SET pin = %s
            WHERE nome = %s
        """, (pin, nome))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao alterar PIN da secretaria: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def alterar_escola_aluno(aluno_id, nova_escola):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            UPDATE usuarios
            SET escola = %s
            WHERE id = %s AND cargo = %s
        """, (nova_escola, aluno_id, "Aluno"))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Erro ao alterar escola do aluno: %s", e, exc_info=True)
        return False

    finally:
        close(cursor, conn)


def buscar_dados_basicos_usuario(user_id):
    """
    Use esta função quando precisar de vários dados do usuário de uma vez,
    em vez de chamar get_role(), pegar_no_nome(), check_pin() separadamente.
    """
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, email, cargo, pin,
                   escola, ano, turma, turmano,
                   matricula_ativa, suspenso, tipo_suspensao
            FROM usuarios
            WHERE id = %s
            LIMIT 1
        """, (user_id,))

        return cursor.fetchone()

    finally:
        close(cursor, conn)