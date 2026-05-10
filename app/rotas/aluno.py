from flask import Flask, request, render_template, session, redirect, url_for, Blueprint, make_response, jsonify
from authlib.integrations.flask_client import OAuth
from app.database.db_usuario import get_role, buscar_usuario, buscar_nome_secretaria, buscar_nome_professor
from app.database.db_denuncia import get_report_status, show_reports, delete_reports, create_report, expire, check_reports
from app.database.db_usuario import usuario_tem_pin, cadastrar_pin, check_pin, buscar_email, pegar_no_nome, buscar_nome_aluno, buscar_status_suspensao,finalizar_suspensao_expirada
from app.database.db_feedback import create_feedback,show_feedback, delete_feedback
from app.database.db_site import mostrar_teams
from app.email.email_service import enviar_email_fim_suspensao
from flask_cors import CORS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime

######-E-Mail-######
remetente = 'denunciasdehaytalo@gmail.com'
senha = 'fpui zjlf ammk kpym'

app = Flask(__name__)
rotas_bp = Blueprint('rotas', __name__)
CORS(app)

CLIENT_ID = "177205671715-238eoh4gfa3qusnfuuaa9jmctiot8vno.apps.googleusercontent.com"

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

######-TESTE-######
def envio_email(destinario, aluno, tipo, debug):
    # Criando a mensagem    
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinario
    if tipo == 'Marcar':
        msg['Subject'] = 'Marcação em Denuncia'
        corpo = f'Este email foi enviado a você pois o {aluno} o marcou em uma denúncia\n\n Acesse agora: https://www.badesp.online/'
    elif tipo == 'Erro':
        msg['Subject'] = 'Erro na IA'
        corpo = f'Este email foi enviado pois houve um erro na IA \n\n{debug}.\n\n Acesse agora: https://www.badesp.online/'
    msg.attach(MIMEText(corpo, 'plain'))

    # Configurando o servidor SMTP do Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls() 
    server.login(remetente, senha)
    texto = msg.as_string()
    server.sendmail(remetente, destinario, texto)
    server.quit()
######-TESTE-######

@rotas_bp.before_app_request
def bloquear_usuario_suspenso_ou_inativo():
    rotas_livres = [
        "static",
        "rotalogin.cadastro",
        "rotas.Termos"
    ]

    if request.endpoint in rotas_livres:
        return

    if "user_id" not in session:
        return

    usuario = buscar_status_suspensao(session["user_id"])

    if not usuario:
        session.clear()
        return redirect(url_for("rotalogin.cadastro"))

    if usuario["cargo"] == "Aluno" and usuario.get("matricula_ativa") == 0:
        session.clear()
        return render_template("acesso_encerrado.html")

    if usuario.get("suspenso") == 1:
        if usuario["tipo_suspensao"] == "permanente":
            session.clear()
            return render_template("aluno_suspenso.html", usuario=usuario)

        if usuario["fim_suspensao"] and usuario["fim_suspensao"] > datetime.now():
            session.clear()
            return render_template("aluno_suspenso.html", usuario=usuario)

        if usuario["fim_suspensao"] and usuario["fim_suspensao"] <= datetime.now():
            if usuario.get("email_fim_suspensao_enviado") == 0:
                enviar_email_fim_suspensao(usuario)

            finalizar_suspensao_expirada(usuario["id"])
            return
        
@rotas_bp.route('/Login2', methods=['GET', 'POST'])
def cadastro2_pin():
    if not "user_id" in session:
        return redirect(url_for('rotalogin.cadastro'))
    if usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.inicio"))
    cargo = get_role(session["user_id"])

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

        cadastrar_pin(id, pin, escola, ano, turma, f'{ano}°{turma}')

        return redirect(url_for('rotas.inicio'))

    return render_template("cadastroaluno.html", cargo=cargo,turmas=mostrar_teams())

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
    
    expire()
    cargo = get_role(session["user_id"])
    usuario = buscar_usuario(session["user_id"])
    escola_usuario = usuario.get("escola")
    filtro = request.args.get('filtro', 'Tudo')

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))
    
    if filtro == 'Aprovado':
        reports = show_reports(session["user_id"], cargo, 'Aprovado.')
    elif filtro == 'Recusado':
        reports = show_reports(session["user_id"], cargo, 'Recusado.')
    elif filtro == 'Abertas':
        reports = show_reports(session["user_id"], cargo, 'Visto.')
    elif filtro == 'Arquivado':
        reports = show_reports(session["user_id"], cargo, 'Arquivado.')
    elif filtro == 'Esperando':
        reports = show_reports(session["user_id"], cargo, 'Em Análise.')
    elif filtro == 'Expirada':
        reports = show_reports(session["user_id"], cargo, 'Expirada.')
    else:
        reports = show_reports(session["user_id"], cargo, 'Tudo')

    if cargo == "Secretaria":
        return render_template("iniciosecretaria.html",usuario=usuario)
    elif cargo == 'Aluno':
        return render_template("inicio.html", reports=reports, usuario=usuario,filtro=filtro)
    elif cargo == 'Professor':
        return render_template("iniciosecretaria.html",usuario=usuario)
    elif cargo == 'Admin':
        # HTML Temporario, criar uma pagina para admin.
        return render_template("inicio.html",usuario=usuario, reports=reports,filtro=filtro)

@rotas_bp.route('/Abertas')
def abertas():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    cargo = get_role(session["user_id"])
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    if cargo == 'Aluno':
        return redirect(url_for('rotas.inicio'))
    if not session.get("allow_folder"):
        return redirect(url_for("rotas.inicio"))
    
    expire()
    cargo = get_role(session["user_id"])
    usuario = buscar_usuario(session["user_id"])
    filtro = request.args.get('filtro', 'Tudo')

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))

    reports = show_reports(session["user_id"], cargo, 'Historico')
    
    # ===== PAGINAÇÃO =====
    page = int(request.args.get("page", 1))
    per_page = 10
    start = (page - 1) * per_page 
    end = start + per_page
    
    reports_paginadas = reports[start:end]
    total_pages = (len(reports) + per_page - 1) // per_page

    return render_template('historico.html', reports=reports_paginadas, usuario=usuario,page=page,total_pages=total_pages,filtro=filtro,tipo='Abertas')

@rotas_bp.route('/Resolvidas')
def Resolvidas():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    cargo = get_role(session["user_id"])
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    if not session.get("allow_folder"):
        return redirect(url_for("rotas.inicio"))
    
    if cargo == 'Aluno':
        return redirect(url_for('rotas.inicio'))
    
    filtro = request.args.get('filtro', 'Tudo')

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))
    
    if filtro == 'Aprovado':
        reports = show_reports(session["user_id"], cargo, 'Aprovado.')
    elif filtro == 'Recusado':
        reports = show_reports(session["user_id"], cargo, 'Recusado.')
    elif filtro == 'Arquivado':
        reports = show_reports(session["user_id"], cargo, 'Arquivado.')
    else:
        reports = show_reports(session["user_id"], cargo, 'Resolvidas')

    expire()
    cargo = get_role(session["user_id"])
    usuario = buscar_usuario(session["user_id"])
    filtro = request.args.get('filtro', 'Tudo')

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))
    
    # ===== PAGINAÇÃO =====
    page = int(request.args.get("page", 1))
    per_page = 10
    start = (page - 1) * per_page 
    end = start + per_page

    reports_paginadas = reports[start:end]
    total_pages = (len(reports) + per_page - 1) // per_page

    return render_template('historico.html', reports=reports_paginadas, usuario=usuario,page=page,total_pages=total_pages,filtro=filtro,tipo='Resolvidas')

######----------######

###### FEEDBACK ######
@rotas_bp.route('/Feedback', methods=['GET', 'POST'])
def feedback():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        tipo = request.form.get('tipo', '').strip()
        mensagem = request.form.get('feedback', '').strip()

        if not titulo or not tipo or not mensagem:
            return redirect(url_for('rotas.feedback'))

        cargo = get_role(session["user_id"])
        create_feedback(titulo, tipo, mensagem, cargo)

        return redirect(url_for('rotas.inicio'))

    resp = make_response(render_template(
        'feedback.html',
        usuario=buscar_usuario(session["user_id"])  # necessário pro header funcionar
    ))

    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'

    return resp


###### ADMIN ######

@rotas_bp.route('/Feedback/Admin', methods=['GET', 'POST'])
def feedback_show():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if get_role(session["user_id"]) != 'Admin':
        return redirect(url_for('rotas.inicio'))
    
    feedback = show_feedback(get_role(session["user_id"]))
    return render_template('show_feedback.html', feedback=feedback)

@rotas_bp.route('/Feedback/Admin/Delete/<int:id>', methods=['POST'])
def excluir_feedback(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    if get_role(session["user_id"]) != 'Admin':
        return redirect(url_for('rotas.inicio'))
    delete_feedback(id)
    return redirect(url_for('rotas.feedback_show'))
    
######----------######

###### MOSTRAR DENUNCIAS #######
@rotas_bp.route('/Denuncias')
def reports():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    cargo = get_role(session["user_id"])
    if cargo == 'Aluno':
        return redirect(url_for('rotas.inicio'))
    if not session.get("allow_folder"):
        return redirect(url_for("rotas.inicio"))
    
    expire()
    usuario = buscar_usuario(session["user_id"])
    reports = show_reports(session["user_id"], cargo, 'Em Análise.')
    
    page = int(request.args.get("page", 1))
    per_page = 6
    start = (page - 1) * per_page 
    end = start + per_page

    reports_paginadas = reports[start:end]
    total_pages = (len(reports) + per_page - 1) // per_page
    
    return render_template("secretaria.html", reports=reports_paginadas, usuario=usuario,page=page,total_pages=total_pages,filtro='Esperando')

######----------######

###### AJUDA ######
@rotas_bp.route('/Ajuda')
def ajuda():
    if "user_id" not in session:
        return render_template('ajuda.html',usuario=False)
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    return render_template('ajuda.html',usuario=buscar_usuario(session["user_id"]), cargo=get_role(session["user_id"]))
######----------######


###### PAGINA DE DENUNCIA ######
@rotas_bp.route('/Denuncia', methods=['GET', 'POST'])
def denuncia():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    cargo = get_role(session["user_id"])
    if cargo != 'Aluno' and cargo != 'Admin':
        return redirect(url_for('rotas.inicio'))
    
    usuario = buscar_usuario(session["user_id"])
    # Alunos só veem colegas da mesma escola
    alunos_por_turma = buscar_nome_aluno(escola=usuario.get("escola"))

    nomeprof = buscar_nome_professor()
    nomesecretaria = buscar_nome_secretaria()

    if request.method == 'POST':
        if not check_reports(session['user_id']):
            return f"""
    <script>
        window.location.href = "{url_for('rotas.inicio')}";
        alert("Você precisa esperar 5 minutos antes de criar outra denúncia.");
    </script>
    """
        
        titulo = request.form.get('titulo')
        tipo = request.form.get('tipo')
        descricao = request.form.get('descricao')
        quem = request.form.get('quem')
        pessoa = request.form.get('pessoa')
        envolvidos = request.form.get('lista_envolvidos_final')

        if pessoa != 'any':
            envio_email(buscar_email(pessoa), pegar_no_nome(session['user_id']), 'Marcar', None)

        create_report(titulo, tipo, descricao, session["user_id"], 'Em Análise.', quem, pessoa,envolvidos)
        
        return redirect(url_for('rotas.inicio'))

    # GET
    resp = make_response(render_template('denuncia.html', professor=nomeprof, secretaria=nomesecretaria,usuario=usuario, alunos_por_turma=alunos_por_turma))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp
######----------######


###### DELETAR DENUNCIA SE ESTIVER EM ANALISE OU EXPIRADA ######
@rotas_bp.route('/Inicio/delete/<int:id>', methods=['POST'])
def excluir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    cargo = get_role(session["user_id"])
    if cargo != 'Aluno':
        return redirect(url_for('rotas.inicio'))
    
    status = get_report_status(id)
    if status == 'Em Análise.' or status == 'Expirada.' or status == 'Aprovado.' or status == 'Recusado.':
        delete_reports(id, session["user_id"])
        return redirect(url_for('rotas.inicio'))
    else:
        return f"""
            <script>
                alert("Não é mais possível deletar a denúncia.");
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

    status = get_report_status(id)
    if status == 'Expirada.':
        create_report(titulo, tipo, descricao, session["user_id"], 'Em Análise.', quem, pessoa)
        delete_reports(id, session["user_id"])
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


@rotas_bp.route('/Termos')
def Termos():
    return render_template('termos.html')
