from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from google.oauth2 import id_token
from google.auth.transport import requests
from authlib.integrations.flask_client import OAuth
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "AGOCSPX-as9HxMU0xYAbQQlwiNZMpB73irZ7"

# CLIENT ID do Google (mantenha seguro em produção)
CLIENT_ID = "334998652961-c43b5pt422pnfqk98t56pu4d6aphi5fe.apps.googleusercontent.com"

# Arquivo de usuários locais (CPF + senha)
user_file = 'usuarios.txt'

# =========================== #
#       UTILITÁRIOS          #
# =========================== #

def validar_cpf(cpf):
    cpf = cpf.replace(".", "").replace("-", "")
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig1 = (soma1 * 10 % 11) % 10

    soma2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig2 = (soma2 * 10 % 11) % 10

    return dig1 == int(cpf[9]) and dig2 == int(cpf[10])

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

init_db()

# =========================== #
#       GOOGLE OAUTH         #
# =========================== #

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret='AGOCSPX-as9HxMU0xYAbQQlwiNZMpB73irZ7',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/')
def homepage():
    user = session.get('user')
    if user:
        return f"Olá, {user['name']} (<a href='/logout'>Sair</a>)"
    return '<a href="/login/google">Entrar com Google</a> | <a href="/Cadastro">Cadastro</a>'

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['user'] = user_info
    session["user_id"] = user_info["id"]
    salvar_usuario(user_info)
    return redirect('/Inicio')
@app.route('/login/callback', methods=["POST", "GET"])
def callback():
    token = None

    if request.is_json:
        token = request.json.get("credential")
    elif "credential" in request.form:
        token = request.form.get("credential")
    elif "credential" in request.args:
        token = request.args.get("credential")

    if not token:
        return jsonify({"error": "Token não fornecido"}), 400

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        user_data = {
            "id": idinfo["sub"],
            "email": idinfo["email"],
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture")
        }
        salvar_usuario(user_data)
        session["user_id"] = user_data["id"]
        return jsonify({"status": "ok", "user": user_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("homepage"))

# =========================== #
#     LOGIN LOCAL (TXT)      #
# =========================== #

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensagem = ""
    if request.method == "POST":
        usuario_digitado = request.form["nome"]
        senha_digitada = request.form["senha"]

        usuarios = {}
        with open(user_file, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if linha.strip():
                    nome, senha = linha.strip().split(":")
                    usuarios[nome] = senha

        if usuario_digitado in usuarios and usuarios[usuario_digitado] == senha_digitada:
            mensagem = f"Login concluído! Bem-vindo, {usuario_digitado}!"
            return render_template('concluido.html', mensagem=mensagem)
        else:
            mensagem = "Usuário ou senha incorretos!"

    return render_template("login.html", mensagem=mensagem)

# =========================== #
#         CADASTRO           #
# =========================== #

@app.route('/Cadastro', methods=['GET', 'POST'])
def cadastro():
    mensagem = ''
    if request.method == 'POST':
        cpf = request.form['cpf']
        senha = request.form['senha']
        confirmar = request.form['confirmar']

        usuarios = {}
        with open(user_file, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if linha.strip():
                    nome, senha_arquivo = linha.strip().split(":")
                    usuarios[nome] = senha_arquivo

        if cpf in usuarios:
            mensagem = 'Usuário já cadastrado.'
        elif senha != confirmar:
            mensagem = 'As senhas devem ser iguais.'
        elif not validar_cpf(cpf):
            mensagem = 'CPF inválido.'
        else:
            with open(user_file, "a", encoding="utf-8") as arquivo:
                arquivo.write(f'{cpf}:{senha}\n')
            mensagem = 'Cadastro concluído!'
            return redirect(url_for('inicio'))

    return render_template('cadastro.html', mensagem=mensagem)

# =========================== #
#       PÁGINAS EXTRAS       #
# =========================== #

@app.route('/Inicio')
def inicio():
    if "user_id" in session:
        usuario = buscar_usuario(session["user_id"])
        if usuario:
            return render_template("concluido.html", usuario={
                "id": usuario[0],
                "name": usuario[1],
                "email": usuario[2],
                "picture": usuario[3]
            })
    return redirect(url_for('cadastro'))

@app.route('/Ajuda')
def ajuda():
    return render_template('Ajuda.html')

@app.route('/Denuncia')
def denuncia():
    return render_template('denuncia.html')

@app.route('/hack')
def hack():
    with open(user_file, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
        usuarios = [linha.strip() for linha in linhas]
        return render_template('hacks.html', usuarios=usuarios)

# =========================== #
#         EXECUÇÃO           #
# =========================== #

if __name__ == '__main__':
    app.run(debug=True)
