from flask import Flask, request, render_template, session, redirect, url_for, Blueprint, flash
from authlib.integrations.flask_client import OAuth
from app.database.db_usuario import buscar_cargo, buscar_usuario, buscar_nome_secretaria, buscar_nome_professor
from app.database.db_denuncia import buscar_status_denuncia, mostrar_denuncias, apagar_denuncia, criar_denuncia, expirar, checagem_denunciahehe

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
    if not "user_id" in session:
        return redirect(url_for('rotalogin.cadastro'))
    return redirect(url_for('rotas.inicio'))

@rotas_bp.route('/Inicio', methods=['POST', 'GET'])
def inicio():
    if "user_id" not in session:
        return redirect(url_for("rotalogin.cadastro"))

    expirar()
    cargo = buscar_cargo(session["user_id"])
    usuario = buscar_usuario(session["user_id"])
    denuncias = mostrar_denuncias(session["user_id"], cargo, 'Em Análise')
    filtro = request.args.get('filtro', 'Tudo')

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))
    
    if filtro == 'Tudo':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Tudo')
    elif filtro == 'Aprovado':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Aprovado.')
    elif filtro == 'Recusado':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Recusado.')
    elif filtro == 'Arquivado':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Arquivado.')
    elif filtro == 'Aberto':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Em Análise.')
    elif filtro == 'Expirada':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Expirada.')
    
    # ===== PAGINAÇÃO =====
    page = int(request.args.get("page", 1))
    per_page = 4
    start = (page - 1) * per_page 
    end = start + per_page

    denuncias_paginadas = denuncias[start:end]
    total_pages = (len(denuncias) + per_page - 1) // per_page
        
    if cargo == "Secretaria":
        return render_template("secretaria.html", denuncias=denuncias_paginadas, usuario=usuario,page=page,total_pages=total_pages,filtro=filtro)
    elif cargo == 'Aluno':
        return render_template("inicio.html", denuncias=denuncias, usuario=usuario,filtro=filtro)
    elif cargo == 'Professor':
        return render_template("professor.html", denuncias=denuncias_paginadas, usuario=usuario,page=page,total_pages=total_pages,filtro=filtro)


@rotas_bp.route('/Ajuda')
def ajuda():
    return render_template('ajuda.html')
######----------######


###### PAGINA DE DENUNCIA ######
@rotas_bp.route('/Denuncia', methods=['GET', 'POST'])
def denuncia():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    nomeprof = buscar_nome_professor()
    nomesecretaria = buscar_nome_secretaria()

    if request.method == 'POST':
        if not checagem_denunciahehe(session['user_id']):
            return f"""
    <script>
        window.location.href = "{url_for('rotas.inicio')}";
        alert("Você precisa esperar 30 minutos antes de criar outra denúncia.");
    </script>
    """
        titulo = request.form.get('titulo')
        gravidade = request.form.get('gravidade')
        descricao = request.form.get('descricao')
        quem = request.form.get('quem')
        pessoa = request.form.get('pessoa')

        criar_denuncia(titulo, gravidade, descricao, session["user_id"], 'Em Análise.', quem, pessoa)
        
        return f"""
    <script>
        window.location.href = "{url_for('rotas.inicio')}";
        alert("Denuncia enviada com sucesso!");
    </script>
    """
        
    return render_template('denuncia.html', professor=nomeprof, secretaria=nomesecretaria)
######----------######


###### DELETAR DENUNCIA SE ESTIVER EM ANALISE OU EXPIRADA ######
@rotas_bp.route('/Inicio/delete/<int:id>', methods=['POST' , 'GET'])
def excluir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    
    status = buscar_status_denuncia(id)
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


###### REENVIA A DENUNCIA SE FOR EXPIRADA ######
@rotas_bp.route('/Inicio/reenviar/<int:id>', methods=['POST'])
def reenviar_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    
    titulo = request.form.get('titulo')
    gravidade = request.form.get('gravidade')
    descricao = request.form.get('descricao')
    quem = request.form.get('quem')
    pessoa = request.form.get('pessoa')

    status = buscar_status_denuncia(id)
    if status == 'Expirada.':
        criar_denuncia(titulo, gravidade, descricao, session["user_id"], 'Em Análise.', quem, pessoa)
        apagar_denuncia(id, session["user_id"])
        return redirect(url_for('rotas.inicio'))
    else:
        return f"""
            <script>
                alert("Não é possível reenviar denúncia.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
######----------######