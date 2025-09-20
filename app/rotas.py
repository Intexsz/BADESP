from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Blueprint
from google.oauth2 import id_token
from google.auth.transport import requests
from authlib.integrations.flask_client import OAuth
from app.bancodedados import salvar_usuario, buscar_usuario
from app.bancodedados import criar_denuncia, mostrar_denuncias, apagar_denuncia

app = Flask(__name__)
rotas_bp = Blueprint('rotas', __name__)

CLIENT_ID = "334998652961-c43b5pt422pnfqk98t56pu4d6aphi5fe.apps.googleusercontent.com"

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

'''###### LOGIN ######
@rotas_bp.route('/')
def homepage():
    if "user_id" in session:
        return redirect(url_for('rotas.inicio'))
    return redirect(url_for('rotas.cadastro'))

@rotas_bp.route('/Login/callback', methods=["POST", "GET"])
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

@rotas_bp.route('/Logout')
def logout():
    session.clear()
    return redirect(url_for("rotas.cadastro"))

@rotas_bp.route('/Login', methods=['GET', 'POST'])
def cadastro():
    if "user_id" in session:
        return redirect(url_for('rotas.inicio'))
    return render_template('login.html')
'''

###### PAGINA NORMAL ######
@rotas_bp.route('/Inicio')
def inicio():
    if "user_id" in session:
        usuario = buscar_usuario(session["user_id"])
        if usuario:
            denuncias = mostrar_denuncias(session["user_id"])
            return render_template("inicio.html", usuario={
                "id": usuario[0],
                "name": usuario[1],
                "email": usuario[2],
                "picture": usuario[3]
            }, denuncias=denuncias)
    return redirect(url_for('rotalogin.cadastro'))

@rotas_bp.route('/Ajuda')
def ajuda():
    return render_template('ajuda.html')

###### PAGINA DE DENUNCIA ######

@rotas_bp.route('/Denuncia', methods=['GET', 'POST'])
def denuncia():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        gravidade = request.form.get('gravidade')
        descricao = request.form.get('descricao')

        criar_denuncia(titulo, gravidade, descricao, session["user_id"])

    return render_template('denuncia.html')

@rotas_bp.route('/Inicio/delete/<int:id>', methods=['POST'])
def excluir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    apagar_denuncia(id, session["user_id"])
    return redirect(url_for('rotas.inicio'))
