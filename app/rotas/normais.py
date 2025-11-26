from flask import Flask, request, render_template, session, redirect, url_for, Blueprint, make_response, jsonify
from authlib.integrations.flask_client import OAuth
from app.database.db_usuario import buscar_cargo, buscar_usuario, buscar_nome_secretaria, buscar_nome_professor
from app.database.db_denuncia import buscar_status_denuncia, mostrar_denuncias, apagar_denuncia, criar_denuncia, expirar, checagem_denunciahehe
from app.database.db_usuario import usuario_tem_pin, cadastrar_pin, check_pin
from flask_cors import CORS

app = Flask(__name__)
rotas_bp = Blueprint('rotas', __name__)
CORS(app)

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

@rotas_bp.route('/Login2', methods=['GET', 'POST'])
def cadastro2_pin():
    if not "user_id" in session:
        return redirect(url_for('rotalogin.cadastro'))
    if usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.inicio"))
    cargo = buscar_cargo(session["user_id"])

    if request.method == 'POST':
        id = session.get("user_id")
        pin = request.form['pin']
        escola = request.form['escola']
        if cargo == 'Aluno':   
            ano = request.form['ano']
            turma = request.form['turma']
        else:
            ano = None
            turma = None

        cadastrar_pin(id, pin, escola, ano, turma)

        return redirect(url_for('rotas.inicio'))

    return render_template("cadastroaluno.html", cargo=cargo)

@rotas_bp.route('/')
def homepage():
    if not "user_id" in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    
    return redirect(url_for('rotas.inicio'))

@rotas_bp.route('/Inicio', methods=['POST', 'GET'])
def inicio():
    if "user_id" not in session:
        return redirect(url_for("rotalogin.cadastro"))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    
    expirar()
    cargo = buscar_cargo(session["user_id"])
    usuario = buscar_usuario(session["user_id"])
    filtro = request.args.get('filtro', 'Tudo')

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))
    
    if filtro == 'Aprovado':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Aprovado.')
    elif filtro == 'Recusado':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Recusado.')
    elif filtro == 'Abertas':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Visto.')
    elif filtro == 'Arquivado':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Arquivado.')
    elif filtro == 'Esperando':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Em Análise.')
    elif filtro == 'Expirada':
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Expirada.')
    else:
        denuncias = mostrar_denuncias(session["user_id"], cargo, 'Tudo')

    if cargo == "Secretaria":
        return render_template("iniciosecretaria.html",usuario=usuario)
    elif cargo == 'Aluno':
        return render_template("inicio.html", denuncias=denuncias, usuario=usuario,filtro=filtro)
    elif cargo == 'Professor':
        return render_template("iniciosecretaria.html",usuario=usuario)

@rotas_bp.route('/Abertas')
def abertas():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    cargo = buscar_cargo(session["user_id"])
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    if cargo == 'Aluno':
        return redirect(url_for('rotas.inicio'))
    
    expirar()
    cargo = buscar_cargo(session["user_id"])
    usuario = buscar_usuario(session["user_id"])
    filtro = request.args.get('filtro', 'Tudo')

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))

    denuncias = mostrar_denuncias(session["user_id"], cargo, 'Historico')
    
    # ===== PAGINAÇÃO =====
    page = int(request.args.get("page", 1))
    per_page = 10
    start = (page - 1) * per_page 
    end = start + per_page
    
    denuncias_paginadas = denuncias[start:end]
    total_pages = (len(denuncias) + per_page - 1) // per_page

    return render_template('historico.html', denuncias=denuncias_paginadas, usuario=usuario,page=page,total_pages=total_pages,filtro=filtro,tipo='Abertas')

@rotas_bp.route('/Resolvidas')
def Resolvidas():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    cargo = buscar_cargo(session["user_id"])
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    if cargo == 'Aluno':
        return redirect(url_for('rotas.inicio'))
    
    expirar()
    cargo = buscar_cargo(session["user_id"])
    usuario = buscar_usuario(session["user_id"])
    filtro = request.args.get('filtro', 'Tudo')

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))

    denuncias = mostrar_denuncias(session["user_id"], cargo, 'Resolvidas')
    
    # ===== PAGINAÇÃO =====
    page = int(request.args.get("page", 1))
    per_page = 10
    start = (page - 1) * per_page 
    end = start + per_page

    denuncias_paginadas = denuncias[start:end]
    total_pages = (len(denuncias) + per_page - 1) // per_page

    return render_template('historico.html', denuncias=denuncias_paginadas, usuario=usuario,page=page,total_pages=total_pages,filtro=filtro,tipo='Resolvidas')

@rotas_bp.route('/Denuncias')
def denuncias():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    cargo = buscar_cargo(session["user_id"])
    if cargo == 'Aluno':
        return redirect(url_for('rotas.inicio'))
    
    expirar()
    usuario = buscar_usuario(session["user_id"])
    denuncias = mostrar_denuncias(session["user_id"], cargo, 'Em Análise.')
    
    page = int(request.args.get("page", 1))
    per_page = 6
    start = (page - 1) * per_page 
    end = start + per_page

    denuncias_paginadas = denuncias[start:end]
    total_pages = (len(denuncias) + per_page - 1) // per_page
    
    return render_template("secretaria.html", denuncias=denuncias_paginadas, usuario=usuario,page=page,total_pages=total_pages,filtro='Esperando')

@rotas_bp.route('/Ajuda')
def ajuda():
    if "user_id" not in session:
        return render_template('ajuda.html',usuario=False)
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    return render_template('ajuda.html',usuario=buscar_usuario(session["user_id"]), cargo=buscar_cargo(session["user_id"]))
######----------######


###### PAGINA DE DENUNCIA ######
@rotas_bp.route('/Denuncia', methods=['GET', 'POST'])
def denuncia():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    cargo = buscar_cargo(session["user_id"])
    if cargo != 'Aluno':
        return redirect(url_for('rotas.inicio'))
    
    nomeprof = buscar_nome_professor()
    nomesecretaria = buscar_nome_secretaria()
    usuario = buscar_usuario(session["user_id"])

    if request.method == 'POST':
        if not checagem_denunciahehe(session['user_id']):
            return f"""
    <script>
        window.location.href = "{url_for('rotas.inicio')}";
        alert("Você precisa esperar 30 minutos antes de criar outra denúncia.");
    </script>
    """
        
        titulo = request.form.get('titulo')
        tipo = request.form.get('tipo')
        descricao = request.form.get('descricao')
        quem = request.form.get('quem')
        pessoa = request.form.get('pessoa')

        criar_denuncia(titulo, tipo, descricao, session["user_id"], 'Em Análise.', quem, pessoa)
        
        return f"""
    <script>
        window.location.href = "{url_for('rotas.inicio')}";
        alert("Denuncia enviada com sucesso!");
    </script>
    """

    # GET
    resp = make_response(render_template('denuncia.html', professor=nomeprof, secretaria=nomesecretaria,usuario=usuario))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp
######----------######


###### DELETAR DENUNCIA SE ESTIVER EM ANALISE OU EXPIRADA ######
@rotas_bp.route('/Inicio/delete/<int:id>', methods=['POST' , 'GET'])
def excluir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

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
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    
    titulo = request.form.get('titulo')
    tipo = request.form.get('tipo')
    descricao = request.form.get('descricao')
    quem = request.form.get('quem')
    pessoa = request.form.get('pessoa')

    status = buscar_status_denuncia(id)
    if status == 'Expirada.':
        criar_denuncia(titulo, tipo, descricao, session["user_id"], 'Em Análise.', quem, pessoa)
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

@rotas_bp.route('/verificar_pin', methods=['POST'])
def verificar_pin():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    
    data = request.get_json()
    pin_inserido = data.get('pin')
    usuario_id = session.get('user_id')

    resultado = check_pin(usuario_id)
    
    if str(resultado) == str(pin_inserido):
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'erro', 'mensagem': 'PIN incorreto'})
