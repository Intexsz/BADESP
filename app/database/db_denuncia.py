import re
from datetime import datetime, timedelta, timezone
from app.database.db_usuario import buscar_usuario, pegar_no_nome
from openai import OpenAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.database.db_site import get_conn as get_conn_denuncia
import smtplib
import os

######-E-Mail-######
remetente = os.getenv("EMAIL_SENDER")
senha = os.getenv("EMAIL_PASSWORD")

def envio_email(destinario, tipo, debug):
    # Criando a mensagem    
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinario
    if tipo == 'Erro':
        msg['Subject'] = 'Erro na IA'
        corpo = f'Este email foi enviado pois houve um erro na IA \n\n{debug}.\n\n Acesse agora: https://www.badesp.online/'
    msg.attach(MIMEText(corpo, 'plain'))

    # Configurando o servidor SMTP do Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls() 
    server.login(remetente, senha)
    texto = msg.as_string()
    server.sendmail(remetente, destinario, texto)
    server.quit()
######----------######

client = OpenAI(api_key=os.getenv("GPT_API"))

def IA(frase):
    response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {
            "role": "system",
            "content": (
                "Reforme e resuma a frase para que fique mais formal e profissional, "
                "independentemente do contexto, e avalie qual o tipo de gravidade: "
                "Baixa, Média ou Alta. "
                "Responda exatamente neste formato:\n\n"
                "Frase reformulada: <frase>\n"
                "Tipo de gravidade: <gravidade>"
            )
        },
        {"role": "user", "content": frase}
    ])
    texto_resposta = response.output[0].content[0].text.strip()
    return texto_resposta

# aqui ira criar a denuncia
def create_report(titulo, tipo, descricao, user_id, status, cargo, especifico, envolvidos):
    data_utc = datetime.now(timezone.utc)
    data = data_utc.strftime("%H:%M %d/%m/%Y")
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)

    usuario = buscar_usuario(user_id)

    try:
        texto_resposta = IA(descricao)
        match = re.search(
        r"Frase reformulada[:\-–]?\s*[\"']?(.*?)[\"']?\s*(?:\.|\n|$).*?Tipo de gravidade[:\-–]?\s*[\"']?(Baixa|M[eé]dia|Alta)[\"']?",
        texto_resposta,
        re.IGNORECASE | re.DOTALL)
    
        if match:
            descricao_ia = match.group(1).strip()
            gravidade = match.group(2).capitalize()
        else:
            descricao_ia = f"❌Erro na IA.❌ \n\n {texto_resposta}"
            gravidade = 'Desconhecido'

    except Exception as error:
        descricao_ia = f"❌Erro na IA.❌"
        gravidade = 'Desconhecido'
        # envio_email('00001103203009sp@al.educacao.sp.gov.br', 'Erro', error)
        # envio_email('zamproniomatheus4', 'Erro', error)

    cursor.execute("""
        INSERT INTO denuncias
        (titulo, tipo, descricao, data, user_id, status, nome, visto, comentario, cargo,
         especifico, descricao_ia, gravidade, turma, ano, envolvidos, escola)
        VALUES (%s,%s,%s,%s,%s,%s,%s,'Ninguém','',%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        titulo, tipo, descricao, data, user_id, status,
        usuario["nome"], cargo, especifico,
        descricao_ia, gravidade, usuario["turma"], usuario["ano"], envolvidos, usuario["escola"]
    ))

    conn.commit()
    cursor.close()
    conn.close()


# aqui vai pegar as denuncias e retornar
def show_reports(user_id, cargo, tipo):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    nomezin = pegar_no_nome(user_id)
    usuario = buscar_usuario(user_id)
    escola_usuario = usuario.get("escola") if usuario else None
    
    if cargo == 'Admin':
            cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            ORDER BY id DESC''')
            denuncias = cursor.fetchall()
            conn.close()
            return denuncias
    if tipo != 'Tudo':
        if tipo == 'Resolvidas':
            if cargo == "Secretaria":
                cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, especifico, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE status NOT IN ('Em Análise.', 'Expirado.', 'Visto.')
              AND (cargo = 'Secretaria' OR cargo = 'Ambos')
              AND especifico IN (%s, 'any')
              AND escola = %s
            ORDER BY id DESC
        ''', (nomezin, escola_usuario))
            elif cargo == 'Aluno':
                return
            elif cargo == 'Professor':
                cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, especifico, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE status NOT IN ('Em Análise.', 'Expirado.', 'Visto.')
              AND (cargo = 'Professor' OR cargo = 'Ambos')
              AND especifico IN (%s, 'any')
              AND escola = %s
            ORDER BY id DESC
        ''', (nomezin, escola_usuario))
            denuncias = cursor.fetchall()
            conn.close()
            return denuncias
        
        if tipo == 'Historico':
            if cargo == 'Secretaria':
                cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, especifico, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE status = 'Visto.'
              AND (cargo = 'Secretaria' OR cargo = 'Ambos')
              AND especifico IN (%s, 'any')
              AND escola = %s
            ORDER BY id DESC
        ''', (nomezin, escola_usuario))
            elif cargo == 'Aluno':
                return
            elif cargo == 'Professor':
                cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, especifico, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE status = 'Visto.'
              AND (cargo = 'Professor' OR cargo = 'Ambos')
              AND especifico IN (%s, 'any')
              AND escola = %s
            ORDER BY id DESC
        ''', (nomezin, escola_usuario))
            denuncias = cursor.fetchall()
            conn.close()
            return denuncias
        
        if cargo == 'Secretaria':
            cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, especifico, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE status != 'Expirada.'
              AND (cargo = 'Secretaria' OR cargo = 'Ambos')
              AND status = %s
              AND especifico IN (%s, 'any')
              AND escola = %s
            ORDER BY id DESC
        ''', (tipo, nomezin, escola_usuario))
        elif cargo == 'Aluno':
            cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, comentario, datavisto, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE user_id = %s AND status = %s AND escola = %s
            ORDER BY id DESC
        ''', (user_id, tipo, escola_usuario))
        elif cargo == 'Professor':
            cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, especifico, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE status != 'Expirada.'
              AND (cargo = 'Professor' OR cargo = 'Ambos')
              AND status = %s
              AND especifico IN (%s, 'any')
              AND escola = %s
            ORDER BY id DESC
        ''', (tipo, nomezin, escola_usuario))
        denuncias = cursor.fetchall()
        conn.close()
        return denuncias

    elif tipo == 'Tudo':
        if cargo == 'Secretaria':
            cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE status != 'Expirada.'
              AND (cargo = 'Secretaria' OR cargo = 'Ambos')
              AND especifico IN (%s, 'any')
              AND escola = %s
            ORDER BY id DESC
        ''', (nomezin, escola_usuario))
        elif cargo == 'Aluno':
            cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, comentario, datavisto, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE user_id = %s AND escola = %s
            ORDER BY id DESC
        ''', (user_id, escola_usuario))
        elif cargo == 'Professor':
            cursor.execute('''
            SELECT id, titulo, tipo, descricao, data, status, nome, visto, cargo, comentario, datavisto, descricao_ia, gravidade, turma, ano, escola
            FROM denuncias
            WHERE status != 'Expirada.'
              AND (cargo = 'Professor' OR cargo = 'Ambos')
              AND especifico IN (%s, 'any')
              AND escola = %s
            ORDER BY id DESC
        ''', (nomezin, escola_usuario))
        denuncias = cursor.fetchall()
        conn.close()
        return denuncias

# aqui é apagar as denuncias
def delete_reports(id, user_id):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM denuncias WHERE id=%s AND user_id=%s", (id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

# aqui vai buscar o status da denuncia
def get_report_status(id):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM denuncias WHERE id=%s", (id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["status"] if r else None


# aqui vai ser aonde o status vai expire quaso a denuncia fique parada durante 7 dias
def expire():
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, datavisto, status FROM denuncias")
        denuncias = cursor.fetchall()

        agora = datetime.now()

        for d in denuncias:
            status = d["status"]
            datavisto = d["datavisto"]

            if not datavisto:
                continue

            try:
                data = datetime.strptime(datavisto, "%H:%M %d/%m/%Y")
            except ValueError:
                print(f"Data inválida na denúncia {d['id']}: {datavisto}")
                continue

            if status == "Visto.":
                if agora > data + timedelta(days=7):
                    cursor.execute(
                        "UPDATE denuncias SET status = %s WHERE id = %s",
                        ("Expirada.", d["id"])
                    )

            elif status in ("Aprovado.", "Recusado."):
                if agora > data + timedelta(days=14):
                    cursor.execute(
                        "DELETE FROM denuncias WHERE id = %s",
                        (d["id"],)
                    )

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Erro ao expirar denúncias:", e)

    finally:
        cursor.close()
        conn.close()


# checa se o usuario ja criou uma denuncia a menos de 30 minutos -feito com ajuda de IA
def check_reports(user_id):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT data FROM denuncias WHERE user_id=%s ORDER BY id DESC LIMIT 1", (user_id,))
    r = cursor.fetchone()
    conn.close()

    if not r:
        return True

    ultima = datetime.strptime(r["data"], "%H:%M %d/%m/%Y")
    return datetime.now() > ultima + timedelta(minutes=5)

######----------######

# aqui é quando ele abre a denuncia, deixando ela em Visto.
def open_report_db(id, cargo, nome, id_user, escola_usuario=None):
    if cargo not in ("Secretaria", "Professor"):
        return

    # Verificar se a denúncia pertence à escola do usuário
    if escola_usuario and not verificar_escola_denuncia(id, escola_usuario):
        return

    especifico = get_specific(id)
    nome_user = pegar_no_nome(id_user)

    if especifico != "any" and especifico != nome_user:
        return

    data = datetime.now().strftime("%H:%M %d/%m/%Y")

    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT datavisto FROM denuncias WHERE id=%s", (id,))
    row = cursor.fetchone()

    cursor.execute(
        "UPDATE denuncias SET status='Visto.' WHERE id=%s AND status='Em Análise.'", (id,)
    )

    cursor.execute(
        "UPDATE denuncias SET visto=%s WHERE id=%s AND visto='Ninguém'", (nome, id)
    )

    if not row["datavisto"]:
        cursor.execute(
            "UPDATE denuncias SET datavisto=%s WHERE id=%s", (data, id)
        )

    conn.commit()
    cursor.close()
    conn.close()


def get_report(id, escola_usuario=None):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id, titulo, tipo, descricao, data, status, nome, visto, comentario, tipo, cargo, datavisto, especifico, descricao_ia, gravidade, turma, ano, escola
        FROM denuncias
        WHERE id = %s
    """
    params = [id]
    
    if escola_usuario:
        query += " AND escola = %s"
        params.append(escola_usuario)
    
    cursor.execute(query, params)
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return row
    else:
        return 'no'

    
def get_open(id):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT visto FROM denuncias WHERE id=%s", (id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["visto"] if r else None


def check_coment(id):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT comentario FROM denuncias WHERE id=%s", (id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["comentario"] if r else None


def update_status(id, cargo, novo, id_user, escola_usuario=None):
    if cargo not in ("Secretaria", "Professor"):
        return

    # Verificar se a denúncia pertence à escola do usuário
    if escola_usuario and not verificar_escola_denuncia(id, escola_usuario):
        return

    especifico = get_specific(id)
    nome_user = pegar_no_nome(id_user)

    if especifico != "any" and especifico != nome_user:
        return

    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        UPDATE denuncias
        SET status=%s
        WHERE id=%s AND status!='Expirada.'
    """, (novo, id))

    conn.commit()
    cursor.close()
    conn.close()


def post_comment(comentario, id, cargo, id_user, escola_usuario=None):
    if cargo not in ("Secretaria", "Professor"):
        return

    # Verificar se a denúncia pertence à escola do usuário
    if escola_usuario and not verificar_escola_denuncia(id, escola_usuario):
        return

    especifico = get_specific(id)
    nome_user = pegar_no_nome(id_user)

    if especifico != "any" and especifico != nome_user:
        return

    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "UPDATE denuncias SET comentario=%s WHERE id=%s", (comentario, id)
    )

    conn.commit()
    cursor.close()
    conn.close()


def get_specific(id):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT especifico FROM denuncias WHERE id=%s", (id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["especifico"] if r else None


def verificar_escola_denuncia(id_denuncia, escola_usuario):
    """Verifica se a denúncia pertence à escola do usuário"""
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT escola FROM denuncias WHERE id=%s", (id_denuncia,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not r:
        return False
    return r["escola"] == escola_usuario


def list_reports(nome):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total FROM denuncias WHERE nome=%s", (nome,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["total"]


def list_approved(nome):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM denuncias
        WHERE nome=%s AND status='Aprovado.'
    """, (nome,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r["total"]


def checar_envolvidos(id_denuncia):
    conn = get_conn_denuncia()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT envolvidos FROM denuncias WHERE id=%s", (id_denuncia,))
    r = cursor.fetchone()

    cursor.close()
    conn.close()

    if not r or not r["envolvidos"]:
        return []

    return [x.strip() for x in r["envolvidos"].split(",")]

        
