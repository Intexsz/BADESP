from flask import Flask, session, redirect, url_for, Blueprint,render_template, request, flash
from authlib.integrations.flask_client import OAuth
from app.database.db_usuario import get_role, pegar_no_nome, usuario_tem_pin, buscar_nome_aluno, novo_pin_secretaria,buscar_usuario,listar_alunose, mudar_turma, check_team, novo_pin, contar_alunos_cadastrados, desativar_e_limpar_2fa
from app.database.db_denuncia import get_report_status, open_report_db, get_report, checar_envolvidos, contar_denuncias_abertas, contar_denuncias_novas, contar_denuncias_resolvidas
from app.database.db_denuncia import update_status, post_comment, check_coment,list_reports,list_approved
from app.database.db_site import create_team, mostrar_teams, delete_team, check_teams, get_conn as expire_get_conn
from app.database.db_usuario import suspender_user, buscar_aluno_por_id, alterar_matricula_ativa, buscar_status_suspensao, remover_suspensao_user, salvar_segredo_2fa, ativar_2fa_usuario
from app.email.email_service import  enviar_email_suspensao, enviar_email_suspensao_removida_aluno, enviar_email_suspensao_removida_suspensor, enviar_email_acesso_encerrado
from app.database.db_denuncia import expire
import qrcode
from datetime import datetime
import pyotp
import os
import io

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

@secretaria.before_request
def check_2af():
  if 'user_id' in session:
    return

  rotas_permitidas_2fa = [
      'rotasecretaria.configurar_2fa',
      'rotasecretaria.configurar_2fa2',
      'rotasecretaria.reconfigurar_2fa',
      'rotasecretaria.qrcode_route',
      'rotasecretaria.ativar_2fa_post',
      'rotasecretaria.login_challenge',
      'rotalogin.logout',
  ]

  if 'pre_user_id' in session:
    if request.endpoint not in rotas_permitidas_2fa:
      user_id = session.get('pre_user_id')
      usuario = buscar_usuario(user_id)

      if usuario and usuario.get('two_factor_enabled') == 1:
        return redirect(url_for('rotasecretaria.login_challenge'))
      else:
        return redirect(url_for('rotasecretaria.configurar_2fa'))


@secretaria.route('/allow_detail', methods=['POST'])
def allow_detail():
    if request.method == 'POST':
        id = request.form.get('idzin')
        session["allow_detail"] = True
        session["allow_folder"] = True
        return redirect(url_for(f"rotasecretaria.detalhe_denuncia", id=id))

@secretaria.route('/allow_folder', methods=['POST'])
def autoria_entrar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        session["allow_folder"] = True
        if nome == 'Alunos':
            return redirect(url_for(f"rotasecretaria.listar_alunos"))
        elif nome == 'Resolvidas':
            return redirect(url_for(f"rotas.Resolvidas"))
        elif nome == 'Abertas':
            return redirect(url_for(f"rotas.abertas"))
        elif nome == 'Novas':
            return redirect(url_for(f"rotas.reports"))

###### ABRIR DENUNCIA SE NÃO ESTIVER EXPIRADA(acho que não está sendo utilizada) ######
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
            flash("Denuncia expirada.", "warning")
            return redirect(url_for("rotas.inicio"))
    else:
        flash("Você não tem permissão para abrir esta denuncia.", "error")
        return redirect(url_for('rotas.inicio'))
######----------######

###### MOSTRAR O DETALHE DAS DENUNCIAS ######
@secretaria.route("/detalhe/<int:id>", methods=['POST', 'GET'])
def detalhe_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for("rotalogin.cadastro"))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    if not session.get("allow_detail") or not session.get("allow_folder"):
        flash("Erro: Você não tem permissão para abrir esta denuncia. Por favor, Navegue até ela normalmente.", "error")
        return redirect(url_for("rotas.inicio"))

    usuario_logado = buscar_usuario(session['user_id'])
    cargo = get_role(session['user_id'])
    if cargo in ('Secretaria', 'Professor'):

        nomezin = pegar_no_nome(session['user_id'])

        open_report_db(id, cargo, nomezin, session['user_id'], escola_usuario=usuario_logado.get("escola"))
        denuncia = get_report(id, escola_usuario=usuario_logado.get("escola"))
        
        if denuncia == 'no':
            flash("Erro: Denuncia não encontrada.", "error")
            return redirect(url_for("rotas.inicio"))
        
        session.pop("allow_folder", None)
        session.pop("allow_detail", None)
        return render_template("denuncia_aberta.html", usuario=denuncia,tipo_usuario='secretaria',usuario2=usuario_logado, envolvidos = checar_envolvidos(id))
    
    elif cargo == 'Aluno':
        usuario_logado_aluno = buscar_usuario(session['user_id'])
        denuncia = get_report(id, escola_usuario=usuario_logado_aluno.get("escola"))
        nome = pegar_no_nome(session['user_id'])

        if denuncia == 'no':
            flash("Erro: Denuncia não encontrada.", "error")
            return redirect(url_for("rotas.inicio"))

        # só o dono da denúncia pode abrir
        if denuncia['nome'] != nome:
            flash("Erro: Somente o dono da denuncia pode abri-la.", "error")
            return redirect(url_for("rotas.inicio"))

        session.pop("allow_detail", None)
        session.pop("allow_folder", None)
        return render_template("denuncia_aberta.html", usuario=denuncia,tipo_usuario='Aluno',usuario2=usuario_logado_aluno, envolvidos = checar_envolvidos(id))
    elif cargo == 'Admin':
        usuario_logado_admin = buscar_usuario(session['user_id'])
        denuncia = get_report(id)
        nome = pegar_no_nome(session['user_id'])

        if denuncia == 'no':
            flash("Erro: Denuncia não encontrada.", "error")
            return redirect(url_for("rotas.inicio"))

        # só o dono da denúncia pode abrir
        if denuncia['nome'] != nome:
            return redirect(url_for("rotas.inicio"))

        session.pop("allow_detail", None)
        session.pop("allow_folder", None)
        return render_template("denuncia_aberta.html", usuario=denuncia,tipo_usuario='Aluno',usuario2=usuario_logado_admin, envolvidos = checar_envolvidos(id))
    else:
        return redirect(url_for('rotas.inicio'))
######----------######

###### ROTA PARA OS COMENTARIOS ######
@secretaria.route('/Comentar/<int:id>', methods=['POST'])
def comentar(id):
    comentario = request.form.get('comentario')
    checagem = check_coment(id)
    
    if not comentario:
        flash("Você não pode comentar aqui.", "error")
        return redirect(url_for('rotas.inicio'))
    
    if checar_stats(id) == 'Erro':
        flash("Erro em checar dados.", "error")
        return redirect(url_for("rotas.inicio"))

    elif checar_stats(id) == 'Expirou':
        flash("Erro: Denuncia expirada.", "error")
        return redirect(url_for("rotas.inicio"))

    if checar_stats(id) and checagem == '':
        cargo = get_role(session['user_id'])
        usuario = buscar_usuario(session['user_id'])
        session["allow_detail"] = True
        session["allow_folder"] = True
        post_comment(comentario, id, cargo, session['user_id'], escola_usuario=usuario.get("escola"))
    else:
        flash("Erro: Você não pode comentar.", "error")
        return redirect(url_for("rotas.inicio"))
    
    return redirect(url_for('rotasecretaria.detalhe_denuncia', id=id))
######----------######

###### ROTAS PARA MUDAR STATUS DA DENUNCIA ######
@secretaria.route('/Inicio/Recusar/<int:id>', methods=['POST', 'GET'])
def recusar(id):
    if checar_stats(id) == 'Expirou':
        flash("Erro: Denuncia expirada.", "error")
        return redirect(url_for("rotas.inicio"))

    if checar_stats(id):
        cargo = get_role(session['user_id'])
        usuario = buscar_usuario(session['user_id'])
        update_status(id, cargo, 'Recusado.', session['user_id'], escola_usuario=usuario.get("escola"))
        flash("Denuncia recusada com sucesso!", "sucess")

    return redirect(url_for('rotas.inicio'))
    
@secretaria.route('/Inicio/Aprovar/<int:id>', methods=['POST', 'GET'])
def aprovar(id):
    if checar_stats(id) == 'Expirou':
        flash("Erro: Denuncia expirada.", "error")
        return redirect(url_for("rotas.inicio"))

    if checar_stats(id):
        cargo = get_role(session['user_id'])
        usuario = buscar_usuario(session['user_id'])
        update_status(id, cargo, 'Aprovado.', session['user_id'], escola_usuario=usuario.get("escola"))
        flash("Denuncia aprovada com sucesso!", "sucess")

    return redirect(url_for('rotas.inicio'))
######----------######

###### ROTAS PARA ARQUIVAR A DENUNCIA ######
@secretaria.route('/Inicio/Arquivar/<int:id>', methods=['POST', 'GET'])
def arquivar(id):
    if checar_stats(id) == 'Expirou':
        return redirect(url_for("rotas.inicio"))
    if checar_stats(id):
        cargo = get_role(session['user_id'])
        update_status(id, cargo, 'Arquivado.', session['user_id'])
        flash("Denuncia arquivada com sucesso!", "sucess")

    return redirect(url_for('rotas.inicio'))
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
            turma = request.form.get("turma")
            email = request.form.get("email_aluno")

            if pin == '0' or pin == '000000':
                flash("Não pode ser somente 0", "erro")
                return redirect(url_for('rotasecretaria.alunos'))
            else:
                novo_pin(pin, email, turma)
                flash("Pin atualizado com sucesso!", "sucesso")
                return render_template("recuperacao_pin.html", alunos_por_turma=alunos_por_turma, tipo='Aluno', usuario=usuario)
        
        return render_template("recuperacao_pin.html", alunos_por_turma=alunos_por_turma, tipo='Aluno', usuario=usuario)
    else:
        flash("Erro: Você não tem permissão para acessar isso. Consulte a secretaria se deseja alterar seu PIN.", "error")
        return redirect(url_for('rotas.inicio'))


###### ROTA PARA Gestao Alterar PIN ######
@secretaria.route('/MudarPIN/GestaoAlterar', methods=['GET', 'POST'])
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
            gestão_id = session['user_id']
            pin = request.form.get("pin")

            novo_pin_secretaria(pin, gestão_id)
            flash(f"Seu PIN foi atualizado com sucesso!", "sucesso")
            return render_template("recuperacao_pin.html", alunos_por_turma=alunos_por_turma, tipo='Gestão', usuario=usuario)
        
        return render_template("recuperacao_pin.html", alunos_por_turma=alunos_por_turma, tipo='Gestão', usuario=usuario)
    else:
        flash("Erro: Você não tem permissão para acessar isso. Consulte a secretaria se deseja alterar seu PIN.", "error")
        return redirect(url_for('rotas.inicio'))

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
        flash("Erro: Você não tem permissão para acessar isso. Consulte a secretaria se deseja alterar seu PIN.", "error")
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
    if not session.get("allow_folder"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for("rotas.inicio"))
    
    usuario = buscar_usuario(session["user_id"])
    cargo = get_role(session['user_id'])
    if cargo not in ('Secretaria', 'Professor'):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for('rotas.inicio'))

    ano = request.args.get("Ano", "Todos")
    serie = request.args.get("Serie", "Todos")
    # 1. CAPTURA SE A CHECKBOX ESTÁ MARCADA
    incluir_inativos = request.args.get("incluir_inativos") == "1"

    if ano == "Todos":
        serie = "Todos"

    # Busca alunos da escola
    alunos = listar_alunose(ano=ano, serie=serie, escola=usuario.get("escola")) or []

    # 2. FILTRA INATIVOS SE A CHECKBOX NÃO ESTIVER MARCADA
    if not incluir_inativos:
        alunos = [a for a in alunos if a.get('matricula_ativa', 1) == 1 and not a.get('suspenso')]

    # Processa denúncias totais e aprovadas para cada aluno
    alunos_processados = []
    for a in alunos:
        nome = a['nome']
        a['total'] = list_reports(nome)
        a['aprov'] = list_approved(nome)
        alunos_processados.append(a)

    # 3. PAGINAÇÃO LIMPA E ÚNICA
    page = int(request.args.get("page", 1))
    per_page = 10
    total_pages = max(1, (len(alunos_processados) + per_page - 1) // per_page)

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    reports_paginadas = alunos_processados[start:end]

    return render_template(
        "aluno.html",
        alunos_por_turma=reports_paginadas,
        usuario=usuario,
        filtro_ano=ano,
        filtro_serie=serie,
        incluir_inativos=incluir_inativos,  # Envia a variável para manter a checkbox marcada no HTML
        page=page,
        total_pages=total_pages,
        turmas=mostrar_teams()
    )

@secretaria.route('/Alunos/Suspender/<id>', methods=['GET'])
def pagina_suspender_aluno(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    if not session.get("allow_folder"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
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

    if not session.get("allow_folder"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
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

    if not session.get("allow_folder"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
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

    if not session.get("allow_folder"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
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

    if not session.get("allow_folder"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    if cargo not in ("Secretaria", "Professor"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for("rotas.inicio"))

    alterar_matricula_ativa(id, True)

    return redirect(url_for("rotasecretaria.listar_alunos"))

@secretaria.route('/2fa/configurar', methods=['GET'])
def configurar_2fa():
    if 'user_id' in session:
        return redirect(url_for('rotas.inicio'))
    if 'pre_user_id' not in session:
        return redirect(url_for('rotalogin.cadastro'))
    
    user_id = session.get('pre_user_id')
    cargo = get_role(user_id)
    if cargo == 'Aluno':
        session['user_id'] = user_id
        session.pop('pre_user_id', None)
        return redirect(url_for('rotas.inicio'))

    usuario = buscar_usuario(user_id)
    if not usuario:
        return redirect(url_for('rotalogin.cadastro'))

    val_2fa = usuario.get('two_factor_enabled')
    is_ativo = False
    if val_2fa is not None:
        if isinstance(val_2fa, bytes):
            is_ativo = val_2fa != b'\x00'
        else:
            is_ativo = bool(val_2fa) and val_2fa not in (0, '0', 'False', 'false')

    if is_ativo:
        if not session.get('permitir_reconfiguracao'):
            return redirect(url_for('rotasecretaria.login_challenge'))

    session.pop('permitir_reconfiguracao', None)

    if not usuario.get('otp_secret'):
        new_secret = pyotp.random_base32()
        salvar_segredo_2fa(user_id, new_secret)
        usuario['otp_secret'] = new_secret

    return render_template('configurar_2fa.html', usuario=usuario)


@secretaria.route('/2fa/reconfigurar', methods=['GET'])
def reconfigurar_2fa():
  user_id = session.get('pre_user_id') or session.get('user_id')

  if not user_id:
    return redirect(url_for('rotalogin.cadastro'))

  desativar_e_limpar_2fa(user_id)

  session['permitir_reconfiguracao'] = True
  session['pre_user_id'] = user_id

  return redirect(url_for('rotasecretaria.configurar_2fa'))


@secretaria.route('/login-challenge', methods=['GET', 'POST'])
def login_challenge():
  if 'user_id' in session:
    return redirect(url_for('rotas.inicio'))
  if 'pre_user_id' not in session:
    return redirect(url_for('rotalogin.cadastro'))

  user_id = session.get('pre_user_id')

  cargo = get_role(user_id)
  if cargo == 'Aluno':
    return redirect(url_for('rotas.inicio'))

  usuario = buscar_usuario(user_id)
  if not usuario or not usuario.get('otp_secret'):
    return redirect(url_for('rotalogin.cadastro'))

  if request.method == 'POST':
    code = request.form.get('code')
    totp = pyotp.TOTP(usuario['otp_secret'])

    if totp.verify(code):
      session['user_id'] = user_id
      session.pop('pre_user_id', None)
      return redirect(url_for('rotas.inicio'))

    flash('Código incorreto. Tente novamente.', 'erro')
    return redirect(url_for('rotasecretaria.login_challenge'))

  return render_template('login_challenge.html')

@secretaria.route('/2fa/qrcode')
def qrcode_route():
    if "user_id" in session:
        return redirect(url_for('rotas.inicio'))
    if "pre_user_id" not in session:
        return redirect(url_for("rotalogin.cadastro"))
    
    user_id = session.get("pre_user_id")

    cargo = get_role(user_id)
    if cargo == "Aluno":
        return redirect(url_for("rotas.inicio"))

    usuario = buscar_usuario(user_id)
    if not usuario or not usuario.get("otp_secret"):
        return redirect(url_for('rotalogin.cadastro'))
        
    totp = pyotp.TOTP(usuario["otp_secret"])
    uri = totp.provisioning_uri(name=usuario["email"], issuer_name="BADESP")
    
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return buf.getvalue(), 200, {"Content-Type": "image/png"}

@secretaria.route("/2fa/ativar", methods=["POST"])
def ativar_2fa_post():
  user_id = session.get("pre_user_id") or session.get("user_id")
  if not user_id:
    return redirect(url_for("rotalogin.cadastro"))

  codigo_digitado = request.form.get("codigo")

  usuario = buscar_usuario(user_id)
  if not usuario or not usuario.get("otp_secret"):
    return redirect(url_for("rotasecretaria.configurar_2fa"))

  totp = pyotp.TOTP(usuario["otp_secret"])

  if totp.verify(codigo_digitado):
    ativar_2fa_usuario(user_id)

    session["user_id"] = user_id
    session.pop("pre_user_id", None)
    flash("Verificação de 2 etapas concluida com sucesso!", "sucesso")

    return redirect(url_for("rotas.inicio"))
  else:
    flash("Código 2FA inválido inserido pelo usuário.", "erro")
    return redirect(url_for("rotasecretaria.configurar_2fa"))


# Não tenho certeza se está sendo usada ou se será usado
"""
@secretaria.route('/Alunos/AlterarEscola/<id>', methods=['POST'])
def alterar_escola_aluno_rota(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    if not session.get("allow_folder"):
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
        return redirect(url_for("rotas.inicio"))

    cargo = get_role(session["user_id"])

    # APENAS secretaria pode alterar escola de aluno
    if cargo != "Secretaria":
        flash("Erro: Você não tem permissão para acessar esta pagina.", "error")
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
"""