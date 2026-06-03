from flask import Flask
from authlib.integrations.flask_client import OAuth
from app.rotas.aluno import rotas_bp
from app.rotas.secretaria import secretaria
from app.login.rota_login import rota_login

app = Flask(__name__)
app.secret_key = "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"

CLIENT_ID = "177205671715-238eoh4gfa3qusnfuuaa9jmctiot8vno.apps.googleusercontent.com"

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret='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',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

app.register_blueprint(rotas_bp)
app.register_blueprint(rota_login)
app.register_blueprint(secretaria)

if __name__ == '__main__':
    app.run(debug=True)
