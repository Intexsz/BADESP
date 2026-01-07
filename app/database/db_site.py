import sqlite3

def init_db():
    with sqlite3.connect("turmas.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lista_turmas (
                ano_serie TEXT
            )
        """)
        conn.commit()

def create_team(nome_turma):
    with sqlite3.connect("turmas.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO lista_turmas (ano_serie)
            VALUES (?)
        """, (nome_turma,)) 
        
        conn.commit()

def mostrar_teams():
    with sqlite3.connect("turmas.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ano_serie FROM lista_turmas")
        # Pega a lista bruta: ['1°A', '6°A', '2°B', '9°C'...]
        turmas = [turma[0] for turma in cursor.fetchall()]

    ordem = ['4','5', '6', '7', '8', '9', '1', '2', '3']

    turmas.sort(key=lambda x: (
        ordem.index(x.split('°')[0]),
        x.split('°')[1]          
    ))
    
    return turmas

def delete_team(turma):
    with sqlite3.connect("turmas.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM lista_turmas
            WHERE ano_serie = ?
        """, (turma,))
        
        conn.commit()

def check_teams(turma):
    with sqlite3.connect("turmas.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ano_serie FROM lista_turmas
            WHERE ano_serie = ?
        """, (turma,))
        
        conn.commit()
        return cursor.fetchone()

if __name__ == "__main__":
    init_db()