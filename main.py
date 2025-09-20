# main.py
from flask import Flask
from authlib.integrations.flask_client import OAuth
from app.bancodedados import init_db
from app.rotas import rotas_bp  # Importa a instância do Blueprint
from app.rotalogin import rota_login
from app.bancodedados import criar_tabela
app = Flask(__name__)
app.secret_key = "AGOCSPX-as9HxMU0xYAbQQlwiNZMpB73irZ7"

# CLIENT ID do Google
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

# Registra a instância do Blueprint
app.register_blueprint(rotas_bp)
app.register_blueprint(rota_login)

if __name__ == '__main__':
    init_db()
    criar_tabela()
    app.run(debug=True)
