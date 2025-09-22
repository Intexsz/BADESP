from flask import Flask, request, render_template, session, redirect, url_for, Blueprint
from authlib.integrations.flask_client import OAuth
from app.bancodedadosusuario import buscar_cargo, buscar_usuario
from app.bancodedadosdenuncia import buscar_status_denuncia, mostrar_denuncias, apagar_denuncia, criar_denuncia, expirar

app = Flask(__name__)
rotas_bp = Blueprint('rotas', __name__)

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

###### PAGINAS NORMAIS ######
@rotas_bp.route('/')
def homepage():
    if "user_id" in session:
        return redirect(url_for('rotas.inicio'))
    return redirect(url_for('rotalogin.cadastro'))

@rotas_bp.route('/Inicio')
def inicio():
    if "user_id" not in session:
        return redirect(url_for("rotalogin.cadastro"))
    
    expirar()
    cargo = buscar_cargo(session["user_id"])
    denuncias = mostrar_denuncias(session["user_id"], cargo)
    usuario = buscar_usuario(session["user_id"])

    if cargo == "Secretaria":
        return render_template("secretaria.html", denuncias=denuncias, usuario=usuario)
    elif cargo == 'Aluno':
        return render_template("inicio.html", denuncias=denuncias, usuario=usuario)

@rotas_bp.route('/Ajuda')
def ajuda():
    return render_template('ajuda.html')
######----------######


###### PAGINA DE DENUNCIA ######
@rotas_bp.route('/Denuncia', methods=['GET', 'POST'])
def denuncia():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        gravidade = request.form.get('gravidade')
        descricao = request.form.get('descricao')
        usuario = buscar_usuario(session['user_id'])
        usuario_dict = {
        "id": usuario[0],
        "nome": usuario[1],
        "email": usuario[2],
        "foto": usuario[3],
        "cargo": usuario[4]}
        nome = usuario_dict["nome"]
        
        criar_denuncia(titulo, gravidade, descricao, session["user_id"], 'Em Análise.', nome)
        
    return render_template('denuncia.html')
######----------######


###### DELETAR DENUNCIA SE ESTIVER EM ANALISE OU EXPIRADA ######
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
######----------######