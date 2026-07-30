from flask import Flask, render_template
from authlib.integrations.flask_client import OAuth
from app.rotas.aluno import rotas_bp
from app.rotas.secretaria import secretaria
from app.login.rota_login import rota_login 
from dotenv import load_dotenv
from extensions import limiter, csrf
from datetime import timedelta
import os
from flask_wtf.csrf import CSRFError

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = os.getenv("FLASK_DEBUG") == "0"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_NAME"] = "badesp_session"
app.config["SESSION_REFRESH_EACH_REQUEST"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

limiter.init_app(app)
csrf.init_app(app)
CLIENT_ID = os.getenv("CLIENT_ID")

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin"
    response.headers["Content-Security-Policy"] = (
    "default-src 'self';"

    "script-src 'self' "
    "https://accounts.google.com "
    "https://apis.google.com;"

    "style-src 'self' "
    "'unsafe-inline' "
    "https://fonts.googleapis.com "
    "https://accounts.google.com;"

    "font-src 'self' "
    "https://fonts.gstatic.com data:;"

    "img-src 'self' data: "
    "https://*.googleusercontent.com;"

    "frame-src 'self' "
    "https://accounts.google.com;"
)

    # response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response

# Google
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret=os.getenv("CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

# Registrar blueprints
app.register_blueprint(rotas_bp)
app.register_blueprint(rota_login)
app.register_blueprint(secretaria)

######---Paginas de Erro---######
@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return render_template(
        "error.html",
        type="400",
        content="""Sua sessão expirou ou a solicitação é inválida. Recarregue a página e tente novamente.""",
        TryAgain=True,
        title="Falha na validação de segurança."
    ), 400

@app.errorhandler(400)
def error_400(error):
    return render_template(
        "error.html",
        type="400",
        content="""A solicitação enviada é inválida ou está incompleta.""",
        TryAgain=False,
        title="Solicitação inválida."
    ), 400


@app.errorhandler(401)
def error_401(error):
    return render_template(
        "error.html",
        type="401",
        content="""Você precisa estar autenticado para acessar este recurso.""",
        TryAgain=False,
        title="Não autenticado."
    ), 401


@app.errorhandler(403)
def error_403(error):
    return render_template(
        "error.html",
        type="403",
        content="""Você não possui permissão para acessar esta página.""",
        TryAgain=False,
        title="Acesso negado."
    ), 403


@app.errorhandler(404)
def error_404(error):
    return render_template(
        "error.html",
        type="404",
        content="""A página que você está procurando não existe ou foi removida.""",
        TryAgain=False,
        title="Página inexistente ou removida."
    ), 404


@app.errorhandler(405)
def error_405(error):
    return render_template(
        "error.html",
        type="405",
        content="""O método utilizado nesta solicitação não é permitido para esta página.""",
        TryAgain=False,
        title="Método não permitido."
    ), 405


@app.errorhandler(408)
def error_408(error):
    return render_template(
        "error.html",
        type="408",
        content="""O tempo para concluir a solicitação expirou. Tente novamente.""",
        TryAgain=True,
        title="Tempo esgotado."
    ), 408


@app.errorhandler(413)
def error_413(error):
    return render_template(
        "error.html",
        type="413",
        content="""O arquivo ou os dados enviados excedem o tamanho máximo permitido.""",
        TryAgain=False,
        title="Conteúdo muito grande."
    ), 413


@app.errorhandler(429)
def error_429(error):
    return render_template(
        "error.html",
        type="429",
        content="""Muitas solicitações foram realizadas em um curto período. Aguarde alguns instantes e tente novamente.""",
        TryAgain=True,
        title="Muitas solicitações."
    ), 429


@app.errorhandler(500)
def error_500(error):
    return render_template(
        "error.html",
        type="500",
        content="""Ocorreu um erro inesperado durante o processamento da sua solicitação.
Tente novamente em alguns instantes.""",
        TryAgain=True,
        title="Erro interno do servidor."
    ), 500


@app.errorhandler(502)
def error_502(error):
    return render_template(
        "error.html",
        type="502",
        content="""O servidor recebeu uma resposta inválida de outro serviço. Tente novamente mais tarde.""",
        TryAgain=True,
        title="Gateway inválido."
    ), 502


@app.errorhandler(503)
def error_503(error):
    return render_template(
        "error.html",
        type="503",
        content="""O serviço está temporariamente indisponível. Tente novamente em alguns instantes.""",
        TryAgain=True,
        title="Serviço indisponível."
    ), 503


@app.errorhandler(504)
def error_504(error):
    return render_template(
        "error.html",
        type="504",
        content="""O servidor demorou mais do que o esperado para responder. Tente novamente.""",
        TryAgain=True,
        title="Tempo de resposta excedido."
    ), 504
######---------######

#---Iniciar aplicativo--#
if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
