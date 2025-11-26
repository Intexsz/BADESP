from flask import Flask, session, redirect, url_for, Blueprint,render_template, request
from authlib.integrations.flask_client import OAuth
from app.database.db_usuario import buscar_cargo, pegar_no_nome, usuario_tem_pin, buscar_nome_aluno, novo_pin, novo_pin_secretaria,buscar_usuario,listar_alunose
from app.database.db_denuncia import buscar_status_denuncia, abrir_denunciabanquinho, pegar_na_denuncia_haha, buscar_visto
from app.database.db_denuncia import atualizar_statuse, publicar_comentario, buscar_comentario,listar_denuncias,listar_aprovacao

app = Flask(__name__)
rota_secretaria = Blueprint('rotasecretaria', __name__)

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

def checar_stats(id):
    status = buscar_status_denuncia(id)
    if status == None:
        return 'Erro'
    
    if status == 'Expirada.':
        return 'Expirou'
    
    cargo = buscar_cargo(session['user_id'])
    if cargo == 'Secretaria' or cargo == 'Professor':
        if status != 'Expirada.':
            return True
        else:
            return 'Expirou'
    else:
        return False
    
###### ABRIR DENUNCIA SE NÃO ESTIVER EXPIRADA ######
@rota_secretaria.route('/Inicio/abrir/<int:id>', methods=['POST'])
def abrir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    cargo = buscar_cargo(session["user_id"])
    if cargo == "Secretaria" or cargo == 'Professor':
        status = buscar_status_denuncia(id)
        if status != 'Expirada.':
            abrir_denunciabanquinho(id, cargo, session['user_id'])
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
@rota_secretaria.route("/detalhe/<int:id>", methods=['POST', 'GET'])
def detalhe_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for("rotalogin.cadastro"))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))
    
    cargo = buscar_cargo(session['user_id'])
    if cargo in ('Secretaria', 'Professor'):
        
        visto = buscar_visto(id)
        nomezin = pegar_no_nome(session['user_id'])

        # se denuncia não foi aberta por ninguem
        if not visto or visto == 'Ninguém':
            abrir_denunciabanquinho(id, cargo, nomezin, session['user_id'])
            denuncia = pegar_na_denuncia_haha(id)

        # se denuncia foi aberta pelo mesmo usuario e esse mesmo usuario deseja reabrir
        elif visto == nomezin:
            abrir_denunciabanquinho(id, cargo, nomezin, session['user_id'])
            denuncia = pegar_na_denuncia_haha(id)
        else:
            # se foi aberta por outra pessoa
            return f"""
            <script>
                alert("Denuncia ja aberta por {visto}.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
            """
        
        if denuncia == 'no':
            return "Denúncia não encontrada", 404
        
        return render_template("DenunciaAberta.html", usuario=denuncia,tipo_usuario='secretaria',usuario2=buscar_usuario(session['user_id']))
    
    elif cargo == 'Aluno':
        denuncia = pegar_na_denuncia_haha(id)
        nome = pegar_no_nome(session['user_id'])


        if denuncia == 'no':
            return "Denúncia não encontrada", 404

        # só o dono da denúncia pode abrir
        if denuncia['nome'] != nome:
            return f"""
        <script>
            alert("Você não tem permissão para acessar esta denúncia.");
            window.location.href = "{url_for('rotas.inicio')}";
        </script>
        """

        return render_template("DenunciaAberta.html", usuario=denuncia,tipo_usuario='Aluno',usuario2=buscar_usuario(session['user_id']))
    else:
        return redirect(url_for('rotas.inicio'))
######----------######

###### ROTA PARA OS COMENTARIOS ######
@rota_secretaria.route('/Comentar/<int:id>', methods=['POST'])
def comentar(id):
    comentario = request.form.get('comentario')
    checagem = buscar_comentario(id)
    
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
        cargo = buscar_cargo(session['user_id'])
        publicar_comentario(comentario, id, cargo, session['user_id'])
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
@rota_secretaria.route('/Inicio/Recusar/<int:id>', methods=['POST', 'GET'])
def recusar(id):
    if checar_stats(id) == 'Expirou':
        return f"""
            <script>
                alert("A denuncia expirou.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
    if checar_stats(id):
        cargo = buscar_cargo(session['user_id'])
        atualizar_statuse(id, cargo, 'Recusado.', session['user_id'])
    
    return redirect(url_for('rotas.inicio'))
    
@rota_secretaria.route('/Inicio/Aprovar/<int:id>', methods=['POST', 'GET'])
def aprovar(id):
    if checar_stats(id) == 'Expirou':
        return f"""
            <script>
                alert("A denuncia expirou.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
    if checar_stats(id):
        cargo = buscar_cargo(session['user_id'])
        atualizar_statuse(id, cargo, 'Aprovado.', session['user_id'])

    return redirect(url_for('rotas.inicio'))
######----------######

###### ROTAS PARA ARQUIVAR A DENUNCIA ######
@rota_secretaria.route('/Inicio/Arquivar/<int:id>', methods=['POST', 'GET'])
def arquivar(id):
    if checar_stats(id) == 'Expirou':
        return f"""
            <script>
                alert("A denuncia expirou.");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
    if checar_stats(id):
        cargo = buscar_cargo(session['user_id'])
        atualizar_statuse(id, cargo, 'Arquivado.', session['user_id'])

    return redirect(url_for('rotas.inicio'))
######----------######

###### ROTA PARA MUDAR O PIN ######
@rota_secretaria.route('/MudarPIN', methods=['GET', 'POST'])
def alunos():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    cargo = buscar_cargo(session['user_id'])
    if cargo in ('Secretaria', 'Professor'):
    # pega todos os alunos organizados por turma
        alunos_por_turma = buscar_nome_aluno()

        if request.method == "POST":
            turma = request.form.get("turma")
            aluno = request.form.get("aluno")
            pin = request.form.get("pin")
            novo_pin(pin, aluno, turma)
            return f"""
            <script>
                alert("Pin de {aluno} de turma {turma} atualizado com sucesso!");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
        
        return render_template("recuperacao_pin.html", alunos_por_turma=alunos_por_turma, tipo='Aluno',usuario=buscar_usuario(session['user_id']))
    else:
        return redirect(url_for('rotas.inicio'))
######----------######

@rota_secretaria.route('/MudarPIN/gestaomudanças', methods=['GET', 'POST'])
def gestao():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))
    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    cargo = buscar_cargo(session['user_id'])
    if cargo in ('Secretaria', 'Professor'):
        alunos_por_turma = buscar_nome_aluno()
        
        if request.method == "POST":
            gestao = pegar_no_nome(session['user_id'])
            pin = request.form.get("pin")
            novo_pin_secretaria(pin, gestao)
            return f"""
            <script>
                alert("Seu pin foi atualizado com sucesso!");
                window.location.href = "{url_for('rotas.inicio')}";
            </script>
        """
        
        return render_template("recuperacao_pin.html", alunos_por_turma=alunos_por_turma, tipo='Gestão',usuario=buscar_usuario(session['user_id']))
    else:
        return redirect(url_for('rotas.inicio'))
######----------######

@rota_secretaria.route('/Alunos', methods=['GET'])
def listar_alunos():
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    if not usuario_tem_pin(session["user_id"]):
        return redirect(url_for("rotas.cadastro2_pin"))

    cargo = buscar_cargo(session['user_id'])
    if cargo not in ('Secretaria', 'Professor'):
        return redirect(url_for('rotas.inicio'))

    ano = request.args.get("Ano", "Todos")
    serie = request.args.get("Serie", "Todos")

    if ano == "Todos":
        serie = "Todos"

    if request.method == 'POST':
        querer = request.form.get('Olavo', 'Tudo')
        return redirect(url_for('rotas.inicio', filtro=querer))
    
    alunos = listar_alunose(ano=ano, serie=serie)

    if alunos:
        page = int(request.args.get("page", 1))
        per_page = 10
        start = (page - 1) * per_page 
        end = start + per_page

        denuncias_paginadas = alunos[start:end]
        total_pages = (len(alunos) + per_page - 1) // per_page
    
        return render_template(
        "aluno.html",
        alunos_por_turma=denuncias_paginadas,
        usuario=buscar_usuario(session['user_id']),
        filtro_ano=ano,
        filtro_serie=serie,
        alunose = alunos,
        quantia = listar_denuncias(alunos[0][0]),
        aproved = listar_aprovacao(alunos[0][0]),page=page,total_pages=total_pages
        )
    else:
        page = int(request.args.get("page", 1))
        per_page = 10
        start = (page - 1) * per_page 
        end = start + per_page

        denuncias_paginadas = alunos[start:end]
        total_pages = (len(alunos) + per_page - 1) // per_page
    
        return render_template(
        "aluno.html",
        alunos_por_turma=denuncias_paginadas,
        usuario=buscar_usuario(session['user_id']),
        filtro_ano=ano,
        filtro_serie=serie,
        alunose = alunos,
        page=page,total_pages=total_pages
        )
