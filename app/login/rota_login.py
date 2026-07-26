from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    session,
    redirect,
    url_for,
    Blueprint,
)

from google.oauth2 import id_token
from google.auth.transport import requests
from authlib.integrations.flask_client import OAuth

from app.database.db_usuario import save_user

from datetime import timedelta
import logging
import os

app = Flask(__name__)
rota_login = Blueprint("rotalogin", __name__)

# ==========================
# CONFIGURAÇÃO
# ==========================

app.secret_key = os.getenv("CLIENT_SECRET")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=not app.debug,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={
        "scope": "openid email profile"
    },
)

# ==========================
# LOGIN
# ==========================

def process_login(cargo):
    try:

        token = (
            request.json.get("credential")
            if request.is_json
            else request.form.get("credential")
            or request.args.get("credential")
        )

        if not token:
            return jsonify({"error": "Token não fornecido."}), 400

        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            CLIENT_ID,
            clock_skew_in_seconds=300,
        )

        # Verifica issuer
        if idinfo.get("iss") not in (
            "accounts.google.com",
            "https://accounts.google.com",
        ):
            return jsonify({"error": "Issuer inválido."}), 400

        # Verifica audience
        if idinfo.get("aud") != CLIENT_ID:
            return jsonify({"error": "Cliente inválido."}), 400

        # Verifica email
        if not idinfo.get("email_verified"):
            return jsonify({"error": "Email não verificado."}), 403

        user_data = {
            "id": str(idinfo["sub"]),
            "email": idinfo["email"],
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
            "cargo": cargo,
        }

        # Salva usuário
        save_user(user_data)

        # Limpa qualquer sessão anterior
        session.clear()

        # Cria nova sessão
        session["user_id"] = user_data["id"]
        session["cargo"] = cargo
        session.permanent = True

        return jsonify(
            {
                "status": "ok",
                "user": user_data,
            }
        )

    except ValueError:
        return jsonify({"error": "Token inválido."}), 400

    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Erro interno."}), 500


# ==========================
# ALUNO
# ==========================

@rota_login.route("/Login/callback", methods=["POST", "GET"])
def callback():
    return process_login("Aluno")


@rota_login.route("/Login", methods=["GET", "POST"])
def cadastro():

    if "user_id" in session:
        return redirect(url_for("rotas.inicio"))

    return render_template(
        "login.html",
        tipo="/Login/callback",
    )


# ==========================
# SECRETARIA
# ==========================

@rota_login.route("/Login/Secretaria/callback", methods=["POST", "GET"])
def callback_secretaria():
    return process_login("Secretaria")


@rota_login.route("/Login/Secretaria", methods=["GET", "POST"])
def login_secretaria():

    if "user_id" in session:
        return redirect(url_for("rotas.inicio"))

    return render_template(
        "login.html",
        tipo="/Login/Secretaria/callback",
    )


# ==========================
# PROFESSOR
# ==========================

@rota_login.route("/Login/Professor/callback", methods=["POST", "GET"])
def callback_professor():
    return process_login("Professor")


@rota_login.route("/Login/Professor", methods=["GET", "POST"])
def login_professor():

    if "user_id" in session:
        return redirect(url_for("rotas.inicio"))

    return render_template(
        "login.html",
        tipo="/Login/Professor/callback",
    )


# ==========================
# LOGOUT
# ==========================

@rota_login.route("/Logout")
def logout():

    session.clear()

    return redirect(url_for("rotalogin.cadastro"))