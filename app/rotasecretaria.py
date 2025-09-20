from flask import Flask, session, redirect, url_for, Blueprint
from authlib.integrations.flask_client import OAuth
from app.bancodedadosusuario import buscar_cargo
from app.bancodedadosdenuncia import buscar_status_denuncia, abrir_denunciabanquinho

app = Flask(__name__)
rota_secretaria = Blueprint('rotasecretaria', __name__)

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


###### ABRIR DENUNCIA SE NÃO ESTIVER EXPIRADA ######
@rota_secretaria.route('/Inicio/abrir/<int:id>', methods=['POST'])
def abrir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    cargo = buscar_cargo(session["user_id"])

    if cargo == "Aluno":
        return redirect(url_for("rotas.inicio"))
    elif cargo == "Secretaria":
        
        status = buscar_status_denuncia(id, session["user_id"])
        if status != 'Expirada.':
            # FALTA COLOCAR CAIXA DE AVISO SE DESEJA ABRIR DENUNCIA #
            abrir_denunciabanquinho(id, cargo)
            return redirect(url_for('rotas.inicio'))
        else:
            return f"""
            <script>
                alert("A denuncia expirou.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
    else:
        return redirect(url_for('rotas.incio'))

###### ARQUIVAR ######
@rota_secretaria.route('/Inicio/Arquivar/<int:id>', methods=['POST'])
def arquivar_denuncia(id):
    if 'user_id' not in session:
        return redirect(url_for('rotalogin.cadastro'))
    cargo = buscar_cargo(session['user_id'])

    if cargo == 'Aluno':
        return redirect(url_for('rotas.inicio'))
    elif cargo == 'Secretaria':
        # arquivar denuncia
        print('ok')
    else:
        return redirect(url_for('rotas.inicio'))

###### APROVAR ######
@rota_secretaria.route('/Inicio/Aprovar/<int:id>', methods=['POST'])
def aprovar():
    if 'user_id' not in session:
        return redirect(url_for('rotalogin.cadastro'))
    cargo = buscar_cargo(session['user_id'])

    if cargo == 'Aluno':
        return redirect(url_for('rotas.inicio'))
    elif cargo == 'Secretaria':
        # aprovar
        print('ok')
    else:
        return redirect(url_for('rotas.inicio'))