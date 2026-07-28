from flask import Flask, render_template
from authlib.integrations.flask_client import OAuth
from app.rotas.aluno import rotas_bp
from app.rotas.secretaria import secretaria
from app.login.rota_login import rota_login 
from dotenv import load_dotenv
from extensions import limiter
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")

limiter.init_app(app)

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
    "script-src 'self' https://*.google.com https://apis.google.com https://*.jsdelivr.net https://cdn.jsdelivr.net https://*.gov.br;"
    "style-src 'self' 'unsafe-inline' https://*.googleapis.com https://googleapis.com https://*.jsdelivr.net https://cdn.jsdelivr.net https://*.gov.br;"
    "font-src 'self' data: https://*.gstatic.com https://gstatic.com;"
    "img-src 'self' data: https://*.googleusercontent.com https://*.jsdelivr.net https://*.gov.br;"
)

    # response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response

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

app.register_blueprint(rotas_bp)
app.register_blueprint(rota_login)
app.register_blueprint(secretaria)

@app.errorhandler(404)
def error_404(error):
    return render_template("error.html", type="404", content="""A página que você está procurando não existe ou foi removida.""", TryAgain=False, title="Pagina inexistente ou removida."), 404

@app.errorhandler(500)
def error_500(error):
    return render_template("error.html", type="500", content="""Ocorreu um erro inesperado durante o processamento da sua solicitação.
                Tente novamente em alguns instantes.""", TryAgain=True, title="Erro interno do servidor"), 500

# Nota: Colocar Flash no inicio da secretaria e no inicio do aluno
if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
