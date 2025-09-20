from flask import Flask, request, render_template, session, redirect, url_for, Blueprint
from authlib.integrations.flask_client import OAuth
from app.bancodedados import buscar_usuario, buscar_status_denuncia
from app.bancodedados import criar_denuncia, mostrar_denuncias, apagar_denuncia, expirar

app = Flask(__name__)
rotas_bp = Blueprint('rotas', __name__)

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

###### PAGINA NORMAL ######
@rotas_bp.route('/Inicio')
def inicio():
    if "user_id" in session:
        expirar()
        usuario = buscar_usuario(session["user_id"])
        if usuario:
            denuncias = mostrar_denuncias(session["user_id"])
            return render_template("inicio.html", usuario={
                "id": usuario[0],
                "name": usuario[1],
                "email": usuario[2],
                "picture": usuario[3]
            }, denuncias=denuncias)
    return redirect(url_for('rotalogin.cadastro'))

@rotas_bp.route('/Ajuda')
def ajuda():
    return render_template('ajuda.html')

###### PAGINA DE DENUNCIA ######

@rotas_bp.route('/Denuncia', methods=['GET', 'POST'])
def denuncia():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        gravidade = request.form.get('gravidade')
        descricao = request.form.get('descricao')

        criar_denuncia(titulo, gravidade, descricao, session["user_id"], 'Em Análise.')

    return render_template('denuncia.html')

@rotas_bp.route('/Inicio/delete/<int:id>', methods=['POST'])
def excluir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    
    status = buscar_status_denuncia(id, session["user_id"])
    if status == 'Em Análise.' or status == 'Expirada.':
        apagar_denuncia(id, session["user_id"])
        return redirect(url_for('rotas.inicio'))
    else:
        return f"""
            <script>
                alert("Não é mais possível deletar denúncia.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """

    
    

