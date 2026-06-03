import logging
from datetime import datetime, timezone
from app.database.db_site import get_conn as get_conn_denuncia

logging.basicConfig(
    filename="error_db.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_feedback(titulo, tipo, feedback, cargo):
    data_utc = datetime.now(timezone.utc)
    data = data_utc.strftime("%H:%M %d/%m/%Y")
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)

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
    cursor = conn.cursor(dictionary=True)
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
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM feedback WHERE id=%s", (id))
    conn.commit()
    cursor.close()
    conn.close()