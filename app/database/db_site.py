import pymysql

def get_conn():
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

def create_team(nome_turma):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lista_turmas (ano_serie) VALUES (%s)",
        (nome_turma,)
    )
    conn.commit()
    cursor.close()
    conn.close()

def mostrar_teams():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT ano_serie FROM lista_turmas")
    turmas = [r["ano_serie"] for r in cursor.fetchall()]
    cursor.close()
    conn.close()

    ordem = ['4','5','6','7','8','9','1','2','3']
    turmas.sort(key=lambda x: (ordem.index(x.split('°')[0]), x.split('°')[1]))
    return turmas

def delete_team(turma):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lista_turmas WHERE ano_serie=%s", (turma,))
    conn.commit()
    cursor.close()
    conn.close()

def check_teams(turma):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT ano_serie FROM lista_turmas WHERE ano_serie=%s", (turma,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r

