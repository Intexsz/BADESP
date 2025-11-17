from flask import Flask
from authlib.integrations.flask_client import OAuth
from app.database.db_usuario import init_db
from app.database.db_denuncia import criar_tabela
from app.rotas.normais import rotas_bp
from app.rotas.rota_secretaria import rota_secretaria
from app.login.rota_login import rota_login

app = Flask(__name__)
app.secret_key = "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"

CLIENT_ID = "334998652961-rpf4gt64873gg0uoa64cmlqkcmj33q4b.apps.googleusercontent.com"

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

# Registra os blueprints
app.register_blueprint(rotas_bp)
app.register_blueprint(rota_login)
app.register_blueprint(rota_secretaria)

if __name__ == '__main__':
    init_db()
    criar_tabela()
    app.run(debug=True)
