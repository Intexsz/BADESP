from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    session,
    redirect,
    url_for,
)
from google.oauth2 import id_token
from google.auth.transport import requests
from app.database.db_usuario import save_user
import logging
import os

from extensions import limiter 


# Define estritamente o Blueprint (sem recriar o objeto Flask 'app')
rota_login = Blueprint("rotalogin", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")

# ==========================
# FUNÇÃO AUXILIAR DE LOGIN
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

        # Salva usuário no banco de dados
        save_user(user_data)

        # Limpa qualquer sessão anterior e gera uma nova e segura
        session.clear()
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
# ROTAS DO ALUNO
# ==========================

@rota_login.route("/Login/callback", methods=["POST", "GET"])
@limiter.limit("5 per minute")  # Protege o endpoint contra spam de requisições
def callback():
    return process_login("Aluno")


@rota_login.route("/Login", methods=["GET", "POST"])
def cadastro():
    if "user_id" in session:
        return redirect(url_for("rotas.inicio"))  # Altere para o nome correto do seu blueprint de início

    return render_template(
        "login.html",
        tipo="/Login/callback",
    )


# ==========================
# ROTAS DA SECRETARIA
# ==========================

@rota_login.route("/Login/Secretaria/callback", methods=["POST", "GET"])
@limiter.limit("5 per minute")
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
# ROTAS DO PROFESSOR
# ==========================

@rota_login.route("/Login/Professor/callback", methods=["POST", "GET"])
@limiter.limit("5 per minute")
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
