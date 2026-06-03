from mysql.connector import pooling, Error

db_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    pool_reset_session=True,

    host="sqldeliciahaha2-manelreidelas.e.aivencloud.com",
    port=21948,
    user="avnadmin",
    password="AVNS_8QxSpDvas-NUiG6m5CY",
    database="defaultdb",

    charset="utf8mb4",
    connection_timeout=10,
)

def get_conn():
    try:
        return db_pool.get_connection()
    except Error as e:
        print("[DB] Erro ao pegar conexão:", e)
        raise

def create_team(nome_turma):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO lista_turmas (ano_serie) VALUES (%s)",
        (nome_turma,)
    )
    conn.commit()
    cursor.close()
    conn.close()

def mostrar_teams():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ano_serie FROM lista_turmas")
    turmas = [r["ano_serie"] for r in cursor.fetchall()]
    cursor.close()
    conn.close()

    ordem = ['4','5','6','7','8','9','1','2','3']
    turmas.sort(key=lambda x: (ordem.index(x.split('°')[0]), x.split('°')[1]))
    return turmas

def delete_team(turma):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM lista_turmas WHERE ano_serie=%s", (turma,))
    conn.commit()
    cursor.close()
    conn.close()

def check_teams(turma):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ano_serie FROM lista_turmas WHERE ano_serie=%s", (turma,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r

