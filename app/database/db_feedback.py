import pymysql
import logging
from datetime import datetime, timezone

def get_conn_denuncia():
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

def create_feedback(titulo, tipo, feedback, cargo):
    data_utc = datetime.now(timezone.utc)
    data = data_utc.strftime("%H:%M %d/%m/%Y")
    conn = get_conn_denuncia()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback
        (titulo, tipo, feedback, horario, cargo)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        titulo, tipo, feedback, data, cargo))

    conn.commit()
    cursor.close()
    conn.close()

def show_feedback(cargo):
    conn = get_conn_denuncia()
    cursor = conn.cursor()
    if cargo == 'Admin':
            cursor.execute('''
            SELECT *
            FROM feedback
            ORDER BY id DESC''')
            denuncias = cursor.fetchall()
            conn.close()
            return denuncias
    else:
         return []

def delete_feedback(id):
    conn = get_conn_denuncia()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback WHERE id=%s", (id))
    conn.commit()
    cursor.close()
    conn.close()