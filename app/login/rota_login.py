from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Blueprint
from google.oauth2 import id_token
from google.auth.transport import requests
from authlib.integrations.flask_client import OAuth
from app.database.db_usuario import save_user

app = Flask(__name__)
rota_login = Blueprint('rotalogin', __name__)
app.secret_key = "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"

CLIENT_ID = "177205671715-238eoh4gfa3qusnfuuaa9jmctiot8vno.apps.googleusercontent.com"

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret="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",
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

###### LOGIN ######
def processar_login(cargo):
    try:
        token = request.json.get("credential") if request.is_json else \
                request.form.get("credential") or request.args.get("credential")

        if not token:
            return jsonify({"error": "Erro: Token não fornecido."}), 400

        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            CLIENT_ID,
            clock_skew_in_seconds=300
        )
        user_data = {
            "id": str(idinfo["sub"]),
            "email": idinfo["email"],
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
            "cargo": cargo
        }
        save_user(user_data)
        
        session["user_id"] = user_data["id"]
        session.permanent = True

        save_user(user_data)
        session["user_id"] = user_data["id"]
        return jsonify({"status": "ok", "user": user_data})

    except ValueError as ve:
        return jsonify({"error": f"Token inválido: {str(ve)}"}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
######----------######

###### ALUNO ######
@rota_login.route('/Login/callback', methods=["POST", "GET"])
def callback():
    return processar_login("Aluno")

@rota_login.route('/Login', methods=['GET', 'POST'])
def cadastro():
    if "user_id" in session:
        return redirect(url_for('rotas.inicio'))
    return render_template('login.html',tipo='/Login/callback')
######----------######

###### SECRETARIA ######
@rota_login.route('/Login/Secretaria/callback', methods=["POST", "GET"])
def callback_secretaria():
    return processar_login("Secretaria")

@rota_login.route('/Login/Secretaria', methods=['GET', 'POST'])
def login_secretaria():
    if "user_id" in session:
        return redirect(url_for('rotas.inicio'))
    return render_template('login.html',tipo='/Login/Secretaria/callback')
######-----------######

###### PROFESSOR ######
@rota_login.route('/Login/Professor/callback', methods=["POST", "GET"])
def callback_professor():
    return processar_login("Professor")

@rota_login.route('/Login/adminsupersecretroutelogin/callback', methods=["POST", "GET"])
def callback_admin():
    return processar_login("Admin")

@rota_login.route('/Login/adminsupersecretroutelogin', methods=['GET', 'POST'])
def login_admin():
    if "user_id" in session:
        return redirect(url_for('rotas.inicio'))
    return render_template('login.html',tipo='/Login/adminsupersecretroutelogin/callback')

@rota_login.route('/Login/Professor', methods=['GET', 'POST'])
def login_professor():
    if "user_id" in session:
        return redirect(url_for('rotas.inicio'))
    return render_template('login.html',tipo='/Login/Professor/callback')
######----------######

###### DESLOGAR ######
@rota_login.route('/Logout')
def logout():
    session.clear()
    return redirect(url_for("rotalogin.cadastro"))
######----------######