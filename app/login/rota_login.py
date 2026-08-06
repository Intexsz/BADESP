from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    session,
    redirect,
    url_for,
    flash,
)
from google.oauth2 import id_token
from google.auth.transport import requests
from app.database.db_usuario import save_user, get_role
import logging
import os
from app.misc.extensions import limiter, csrf

rota_login = Blueprint("rotalogin", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")


# ==========================
# FUNÇÃO PARA DEFINIR O CARGO VIA E-MAIL
# ==========================
def determinar_cargo_por_email(email):
  email = email.lower()

  if email.endswith("@aluno.sp.gov.br") or email.endswith("@aluno.educacao.sp.gov.br") or email.endswith("@al.educacao.sp.gov.br") :
    return "Aluno"
  elif email.endswith("@prof.educacao.sp.gov.br") or email.endswith("@prof.sp.gov.br"):
    return "Professor"
  elif email.endswith("@educacao.sp.gov.br"):
    return "Secretaria"
  else:
    return "Aluno"

def process_login():
  try:
    token = (
        request.json.get("credential")
        if request.is_json
        else request.form.get("credential") or request.args.get("credential")
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

    email = idinfo["email"]
    cargo = determinar_cargo_por_email(email)

    user_data = {
        "id": str(idinfo["sub"]),
        "email": email,
        "name": idinfo.get("name"),
        "picture": idinfo.get("picture"),
        "cargo": cargo,
    }

    # Salva usuário no banco de dados
    save_user(user_data)

    # Limpa qualquer sessão anterior e gera uma nova e segura
    session.clear()
    session["cargo"] = cargo

    if get_role(user_data["id"]) == "Aluno":
      # sem 2 etapas
      session["user_id"] = user_data["id"]
    else:
      # com 2 etapas
      session["pre_user_id"] = user_data["id"]

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

@csrf.exempt
@rota_login.route("/Login/callback", methods=["POST", "GET"])
@limiter.limit("5 per minute")
def callback():
  return process_login()


@rota_login.route("/Login", methods=["GET", "POST"])
def cadastro():
  if "user_id" in session:
    flash("Você já possui Login.", "info")
    return redirect(url_for("rotas.inicio"))

  return render_template(
      "login.html",
      tipo="/Login/callback",
  )

@rota_login.route("/Logout")
def logout():
  session.clear()
  return redirect(url_for("rotalogin.cadastro"))