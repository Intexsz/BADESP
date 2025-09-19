import sqlite3

def init_db():
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                nome TEXT,
                email TEXT,
                foto TEXT
            )
        """)
        conn.commit()

def salvar_usuario(user_data):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_data["id"],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (id, nome, email, foto) VALUES (?, ?, ?, ?)",
                           (user_data["id"], user_data["name"], user_data["email"], user_data["picture"]))
            conn.commit()

def buscar_usuario(user_id):
    with sqlite3.connect("usuarios.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        return cursor.fetchone()