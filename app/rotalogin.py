from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Blueprint
from google.oauth2 import id_token
from google.auth.transport import requests
from authlib.integrations.flask_client import OAuth
from app.bancodedados import salvar_usuario

app = Flask(__name__)
rota_login = Blueprint('rotalogin', __name__)

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

###### LOGIN ######
@rota_login.route('/')
def homepage():
    if "user_id" in session:
        return redirect(url_for('rotalogin.inicio'))
    return redirect(url_for('rotalogin.cadastro'))

@rota_login.route('/Login/callback', methods=["POST", "GET"])
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

@rota_login.route('/Logout')
def logout():
    session.clear()
    return redirect(url_for("rotalogin.cadastro"))

@rota_login.route('/Login', methods=['GET', 'POST'])
def cadastro():
    if "user_id" in session:
        return redirect(url_for('rotalogin.inicio'))
    return render_template('login.html')
