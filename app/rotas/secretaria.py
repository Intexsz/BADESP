from flask import Flask, session, redirect, url_for, Blueprint,render_template, request, flash
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
from app.database.db_usuario import get_role, pegar_no_nome, usuario_tem_pin, buscar_nome_aluno, novo_pin_secretaria,buscar_usuario,listar_alunose, mudar_turma, check_team, novo_pin, alterar_escola_aluno
from app.database.db_denuncia import get_report_status, open_report_db, get_report, checar_envolvidos
from app.database.db_denuncia import update_status, post_comment, check_coment,list_reports,list_approved
from app.database.db_site import create_team, mostrar_teams, delete_team, check_teams
from app.database.db_usuario import suspender_user, buscar_aluno_por_id, alterar_matricula_ativa, buscar_status_suspensao, remover_suspensao_user
from app.email.email_service import  enviar_email_suspensao, enviar_email_suspensao_removida_aluno, enviar_email_suspensao_removida_suspensor, enviar_email_acesso_encerrado
import os

app = Flask(__name__)
secretaria = Blueprint('rotasecretaria', __name__)

CLIENT_ID = os.getenv("CLIENT_ID")

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

def liberar_acesso():
    """Libera acesso ao painel por 5 minutos."""
    session["pin_autorizado_ate"] = (
        datetime.now() + timedelta(minutes=5)
    ).timestamp()


def acesso_liberado():
    """Verifica se a autorização ainda está válida."""

    tempo = session.get("pin_autorizado_ate")

    if tempo is None:
        return False

    if datetime.now().timestamp() > tempo:
        session.pop("pin_autorizado_ate", None)
        return False

    return True

def checar_stats(id):
    status = get_report_status(id)
    if status == None:
        return 'Erro'
    
    if status == 'Expirada.':
        return 'Expirou'
    
    cargo = get_role(session['user_id'])
    if cargo == 'Secretaria' or cargo == 'Professor':
        if status != 'Expirada.':
            return True
        else:
            return 'Expirou'
    else:
        return False

@secretaria.route('/allow_detail', methods=['POST'])
def allow_detail():

    id = request.form.get("idzin")

    liberar_acesso()

    return redirect(url_for("rotasecretaria.detalhe_denuncia", id=id))

@secretaria.route('/allow_folder', methods=['POST'])
def autoria_entrar():

    nome = request.form.get("nome")

    liberar_acesso()

    if nome == "Alunos":
        return redirect(url_for("rotasecretaria.listar_alunos"))

    elif nome == "Resolvidas":
        return redirect(url_for("rotas.Resolvidas"))

    elif nome == "Abertas":
        return redirect(url_for("rotas.abertas"))

    elif nome == "Novas":
        return redirect(url_for("rotas.reports"))

    return redirect(url_for("rotas.inicio"))

###### ABRIR DENUNCIA SE NÃO ESTIVER EXPIRADA ######
@secretaria.route('/Inicio/abrir/<int:id>', methods=['POST'])
def abrir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    usuario = buscar_usuario(session["user_id"])
    cargo = get_role(session["user_id"])
    if cargo == "Secretaria" or cargo == 'Professor':
        status = get_report_status(id)
        if status != 'Expirada.':
            nome = pegar_no_nome(session['user_id'])
            open_report_db(id, cargo, nome, session['user_id'], escola_usuario=usuario.get("escola"))
            return redirect(url_for('rotas.inicio'))
        else:
            return f"""
            <script>
                alert("A denuncia expirou.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
    else:
        return redirect(url_for('rotas.inicio'))
######----------######

###### MOSTRAR O DETALHE DAS DENUNCIAS ######
@secretaria.route("/detalhe/<int:id>", methods=['POST', 'GET'])
def detalhe_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for("rotalogin.cadastro"))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    usuario_logado = buscar_usuario(session['user_id'])
    cargo = get_role(session['user_id'])
    if cargo in ('Secretaria', 'Professor'):

        nomezin = pegar_no_nome(session['user_id'])

        open_report_db(id, cargo, nomezin, session['user_id'], escola_usuario=usuario_logado.get("escola"))
        denuncia = get_report(id, escola_usuario=usuario_logado.get("escola"))
        
        if denuncia == 'no':
            return "Denúncia não encontrada ou fora da sua escola", 404
        
        return render_template("denuncia_aberta.html", usuario=denuncia,tipo_usuario='secretaria',usuario2=usuario_logado, envolvidos = checar_envolvidos(id))
    
    elif cargo == 'Aluno':
        usuario_logado_aluno = buscar_usuario(session['user_id'])
        denuncia = get_report(id, escola_usuario=usuario_logado_aluno.get("escola"))
        nome = pegar_no_nome(session['user_id'])

        if denuncia == 'no':
            return "Denúncia não encontrada ou fora da sua escola", 404

        # só o dono da denúncia pode abrir
        if denuncia['nome'] != nome:
            return f"""
        <script>
            alert("Você não tem permissão para acessar esta denúncia.");
            window.location.href = "{url_for('rotas.inicio')}";
        </script>"""

        session.pop("allow_detail", None)
        session.pop("allow_folder", None)
        return render_template("denuncia_aberta.html", usuario=denuncia,tipo_usuario='Aluno',usuario2=usuario_logado_aluno, envolvidos = checar_envolvidos(id))
    elif cargo == 'Admin':
        usuario_logado_admin = buscar_usuario(session['user_id'])
        denuncia = get_report(id)
        nome = pegar_no_nome(session['user_id'])

        if denuncia == 'no':
            return "Denúncia não encontrada", 404

        # só o dono da denúncia pode abrir
        if denuncia['nome'] != nome:
            return f"""
        <script>
            alert("Você não tem permissão para acessar esta denúncia.");
            window.location.href = "{url_for('rotas.inicio')}";
        </script>"""

        session.pop("allow_detail", None)
        session.pop("allow_folder", None)
        return render_template("denuncia_aberta.html", usuario=denuncia,tipo_usuario='Aluno',usuario2=usuario_logado_admin, envolvidos = checar_envolvidos(id))
    else:
        return redirect(url_for('rotas.inicio'))
######----------######

###### ROTA PARA OS COMENTARIOS ######
@secretaria.route('/Comentar/<int:id>', methods=['POST'])
def comentar(id):
    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    comentario = request.form.get('comentario')
    checagem = check_coment(id)
    
    if not comentario:
        return redirect(url_for('rotas.inicio'))
    
    if checar_stats(id) == 'Erro':
        return f"""
            <script>
                alert("Erro.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
    elif checar_stats(id) == 'Expirou':
        return f"""
            <script>
                alert("A denuncia expirou.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
    if checar_stats(id) and checagem == '':
        cargo = get_role(session['user_id'])
        usuario = buscar_usuario(session['user_id'])
        post_comment(comentario, id, cargo, session['user_id'], escola_usuario=usuario.get("escola"))
    else:
        return f"""
            <script>
                alert("Comentario ja feito.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
    
    return redirect(url_for('rotasecretaria.detalhe_denuncia', id=id))
######----------######

###### ROTAS PARA MUDAR STATUS DA DENUNCIA ######
@secretaria.route('/Inicio/Recusar/<int:id>', methods=['POST'])
def recusar(id):

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    if checar_stats(id) == 'Expirou':
        return f"""
        <script>
            alert("A denúncia expirou.");
            window.location.href="{url_for('rotas.inicio')}";
        </script>
        """

    if checar_stats(id):
        cargo = get_role(session['user_id'])
        usuario = buscar_usuario(session['user_id'])

        update_status(
            id,
            cargo,
            'Recusado.',
            session['user_id'],
            escola_usuario=usuario.get("escola")
        )

    return redirect(
        url_for("rotasecretaria.detalhe_denuncia", id=id)
    )
@secretaria.route('/Inicio/Aprovar/<int:id>', methods=['POST'])
def aprovar(id):

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    if checar_stats(id) == 'Expirou':
        return f"""
        <script>
            alert("A denúncia expirou.");
            window.location.href="{url_for('rotas.inicio')}";
        </script>
        """

    if checar_stats(id):
        cargo = get_role(session['user_id'])
        usuario = buscar_usuario(session['user_id'])

        update_status(
            id,
            cargo,
            'Aprovado.',
            session['user_id'],
            escola_usuario=usuario.get("escola")
        )

    return redirect(
        url_for("rotasecretaria.detalhe_denuncia", id=id)
    )
######----------######

###### ROTAS PARA ARQUIVAR A DENUNCIA ######
@secretaria.route('/Inicio/Arquivar/<int:id>', methods=['POST'])
def arquivar(id):

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    if checar_stats(id) == 'Expirou':
        return f"""
        <script>
            alert("A denúncia expirou.");
            window.location.href="{url_for('rotas.inicio')}";
        </script>
        """

    if checar_stats(id):
        cargo = get_role(session['user_id'])
        usuario = buscar_usuario(session['user_id'])

        update_status(
            id,
            cargo,
            'Arquivado.',
            session['user_id'],
            escola_usuario=usuario.get("escola")
        )

    return redirect(
        url_for("rotasecretaria.detalhe_denuncia", id=id)
    )
######----------######

###### ROTA PARA Mudar PIN ######
@secretaria.route('/MudarPIN', methods=['GET', 'POST'])
def alunos():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    usuario = buscar_usuario(session["user_id"])
    cargo = get_role(session['user_id'])
    if cargo in ('Secretaria', 'Professor'):
    # pega alunos da mesma escola
        alunos_por_turma = buscar_nome_aluno(escola=usuario.get("escola"))

        if request.method == "POST":
            pin = request.form.get("pin")
            aluno = request.form.get("aluno")
            turma = request.form.get("turma")

            if pin == '0' or pin == '000000':
                return f"""
            <script>
                alert("não pode ser somente 0");
                window.location.href = "{url_for('rotasecretaria.alunos')}";
            </script>
        """
            else:
                novo_pin(pin, aluno, turma)
                return f"""
            <script>
                alert("Pin atualizado com sucesso!");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
        
        return render_template("recuperacao_pin.html", alunos_por_turma=alunos_por_turma, tipo='Aluno',usuario=buscar_usuario(session['user_id']))
    else:
        return redirect(url_for('rotas.inicio'))
######----------######

@secretaria.route('/MudarPIN/gestaomudanças', methods=['GET', 'POST'])
def gestao():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    usuario = buscar_usuario(session["user_id"])
    cargo = get_role(session['user_id'])
    if cargo in ('Secretaria', 'Professor'):
        alunos_por_turma = buscar_nome_aluno(escola=usuario.get("escola"))
        
        if request.method == "POST":
            gestao = pegar_no_nome(session['user_id'])
            pin = request.form.get("pin")

            novo_pin_secretaria(pin, gestao)
            return f"""
            <script>
                alert("Pin de {gestao} atualizado com sucesso!");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
        
        return render_template("recuperacao_pin.html", alunos_por_turma=alunos_por_turma, tipo='Gestão',usuario=usuario)
    else:
        return redirect(url_for('rotas.inicio'))
######----------######

@secretaria.route('/Turmas', methods=['GET', 'POST'])
def turmas():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    
    cargo = get_role(session['user_id'])
    if cargo in ('Secretaria', 'Professor'):
        if request.method == 'POST':
            ano = request.form.get('ano')
            turma = request.form.get('turma').upper()
            if check_teams(f'{ano}°{turma}') is None:
                create_team(f'{ano}°{turma}')
                return redirect(url_for('rotasecretaria.turmas'))
            flash(f"Não é possivel criar a turma {ano}°{turma}, Turma ja existente", "erro")
            return redirect(url_for('rotasecretaria.turmas'))
        
        return render_template("turmas.html", turmas=mostrar_teams(), usuario=buscar_usuario(session['user_id']))
    else:
        return redirect(url_for('rotas.inicio'))
    
@secretaria.route('/RemoverTurma', methods=['POST'])
def remove_team():
    turma = request.form.get('nome_turma_input')
    
    if not turma:
        return redirect(url_for('rotasecretaria.turmas'))
    alunos_na_turma = check_team(turma)
    
    if alunos_na_turma:
        flash(f"Não é possível remover a turma {turma}: {len(alunos_na_turma)} aluno(s) associado(s).", "erro")
        return redirect(url_for('rotasecretaria.turmas'))
    
    delete_team(turma)
    flash(f"Turma {turma} removida com sucesso!", "sucesso")
    return redirect(url_for('rotasecretaria.turmas'))

@secretaria.route('/AlterarTodasTurmas', methods=['POST'])
def alterar_todas_turmas():
    ids = request.form.getlist('aluno_ids')
    anos = request.form.getlist('lista_anos')
    turmas = request.form.getlist('lista_turmas')

    if len(ids) == len(anos) == len(turmas):
        for i in range(len(ids)):
            aluno_id = ids[i]
            novo_ano = anos[i]
            nova_turma = turmas[i]
            anoseturmas = f"{novo_ano}°{nova_turma}"
            
            mudar_turma(aluno_id, novo_ano, nova_turma, anoseturmas)
    return redirect(url_for('rotasecretaria.listar_alunos'))

@secretaria.route('/Alunos', methods=['GET'])
def listar_alunos():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))
    
    usuario = buscar_usuario(session["user_id"])
    cargo = get_role(session['user_id'])
    if cargo not in ('Secretaria', 'Professor'):
        return redirect(url_for('rotas.inicio'))

    ano = request.args.get("Ano", "Todos")
    serie = request.args.get("Serie", "Todos")

    if ano == "Todos":
        serie = "Todos"

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotasecretaria.listar_alunos', filtro=querer))
    
    # Filtrar por escola do usuário logado
    alunos = listar_alunose(ano=ano, serie=serie, escola=usuario.get("escola"))

    if alunos:
        alunos = listar_alunose(ano=ano, serie=serie, escola=usuario.get("escola"))

# Adiciona denúncias totais e aprovadas a cada aluno
        alunos_processados = []
        for a in alunos:
            nome = a['nome'] # Acessa pela chave, não pelo índice
            total = list_reports(nome)
            aprov = list_approved(nome)

    # Para adicionar dados ao dicionário atual de forma limpa:
            a['total'] = total
            a['aprov'] = aprov
            alunos_processados.append(a)

# Paginação em cima da lista já processada
        page = int(request.args.get("page", 1))
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page

        reports_paginadas = alunos_processados[start:end]
        total_pages = (len(alunos_processados) + per_page - 1) // per_page

        return render_template(
    "aluno.html",
    alunos_por_turma=reports_paginadas,
    usuario=usuario,
    filtro_ano=ano,
    filtro_serie=serie,
    page=page,
    total_pages=total_pages,turmas=mostrar_teams()
    )

    else:
        page = int(request.args.get("page", 1))
        per_page = 10
        start = (page - 1) * per_page 
        end = start + per_page

        reports_paginadas = alunos[start:end]
        total_pages = (len(alunos) + per_page - 1) // per_page
    
        return render_template(
        "aluno.html",
        alunos_por_turma=reports_paginadas,
        usuario=usuario,
        filtro_ano=ano,
        filtro_serie=serie,
        alunose = alunos,
        page=page,total_pages=total_pages,turmas=mostrar_teams()
        )

@secretaria.route('/Alunos/Suspender/<id>', methods=['GET'])
def pagina_suspender_aluno(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        return redirect(url_for("rotas.inicio"))

    aluno = buscar_aluno_por_id(id)
    usuario = buscar_usuario(session["user_id"])

    if not aluno:
        return "Aluno não encontrado", 404

    return render_template(
        "suspender_aluno.html",
        aluno=aluno,
        usuario=usuario
    )


@secretaria.route('/Alunos/Suspender/<id>', methods=['POST'])
def suspender_acesso(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        return redirect(url_for("rotas.inicio"))

    motivo = request.form.get("motivo")
    tempo = request.form.get("tempo")

    if not motivo or not tempo:
        return "Preencha motivo e tempo da suspensão", 400

    suspensor = buscar_usuario(session["user_id"])

    sucesso = suspender_user(id, motivo, tempo, suspensor)

    if not sucesso:
        return "Tempo de suspensão inválido", 400

    aluno_atualizado = buscar_status_suspensao(id)

    enviar_email_suspensao(aluno_atualizado)

    return redirect(url_for("rotasecretaria.listar_alunos"))


@secretaria.route('/Alunos/RemoverSuspensao/<id>', methods=['POST'])
def remover_suspensao(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        return redirect(url_for("rotas.inicio"))

    aluno = buscar_status_suspensao(id)
    removedor = buscar_usuario(session["user_id"])

    if not aluno:
        return "Aluno não encontrado", 404

    if aluno["suspenso"] != 1:
        return redirect(url_for("rotasecretaria.listar_alunos"))

    id_suspensor = aluno.get("suspenso_por_id")
    email_suspensor = aluno.get("suspenso_por_email")

    remover_suspensao_user(id)

    enviar_email_suspensao_removida_aluno(aluno, removedor)

    if email_suspensor and str(id_suspensor) != str(session["user_id"]):
        enviar_email_suspensao_removida_suspensor(aluno, removedor)

    return redirect(url_for("rotasecretaria.listar_alunos"))


@secretaria.route('/Alunos/DesativarMatricula/<id>', methods=['POST'])
def desativar_matricula(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        return redirect(url_for("rotas.inicio"))

    aluno = buscar_usuario(id)

    if not aluno:
        return "Aluno não encontrado", 404

    alterar_matricula_ativa(id, False)

    enviar_email_acesso_encerrado(aluno)

    return redirect(url_for("rotasecretaria.listar_alunos"))


@secretaria.route('/Alunos/ReativarMatricula/<id>', methods=['POST'])
def reativar_matricula(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        return redirect(url_for("rotas.inicio"))

    alterar_matricula_ativa(id, True)

    return redirect(url_for("rotasecretaria.listar_alunos"))


@secretaria.route('/Alunos/AlterarEscola/<id>', methods=['POST'])
def alterar_escola_aluno_rota(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    if not acesso_liberado():
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    # APENAS secretaria pode alterar escola de aluno
    if cargo != "Secretaria":
        return redirect(url_for("rotas.inicio"))

    aluno = buscar_usuario(id)

    if not aluno:
        return "Aluno não encontrado", 404

    nova_escola = request.form.get("nova_escola")

    if not nova_escola:
        return redirect(url_for("rotasecretaria.listar_alunos"))

    sucesso = alterar_escola_aluno(id, nova_escola)

    if sucesso:
        return redirect(url_for("rotasecretaria.listar_alunos"))
    else:
        return "Erro ao alterar escola do aluno", 400