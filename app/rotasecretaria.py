from flask import Flask, session, redirect, url_for, Blueprint,render_template
from authlib.integrations.flask_client import OAuth
from app.bancodedadosusuario import buscar_cargo, pegar_no_nome
from app.bancodedadosdenuncia import buscar_status_denuncia, abrir_denunciabanquinho, pegar_na_denuncia_haha, mostrar_denuncias, buscar_visto

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


###### ABRIR DENUNCIA SE NÃO ESTIVER EXPIRADA ######
@rota_secretaria.route('/Inicio/abrir/<int:id>', methods=['POST'])
def abrir_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for('rotalogin.cadastro'))

    cargo = buscar_cargo(session["user_id"])

    if cargo == "Secretaria":

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
######----------######


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
######----------######


###### APROVAR ######
@rota_secretaria.route('/Inicio/Aprovar/<int:id>', methods=['POST'])
def aprovar(id):
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
######----------######

# Abre a denuncia #
@rota_secretaria.route("/detalhe/<int:id>")
def detalhe_denuncia(id):
    if "user_id" not in session:
        return redirect(url_for("rotalogin.cadastro"))
    
    cargo = buscar_cargo(session['user_id'])
    
    if cargo == 'Secretaria':
        print(buscar_visto(id))
        print(pegar_no_nome(session['user_id']))
        
        visto = buscar_visto(id)
        nomezin = pegar_no_nome(session['user_id'])

        # se denuncia não foi aberta por ninguem
        if visto == None or visto == 'Ninguém':
            abrir_denunciabanquinho(id, cargo, nomezin)
            denuncia = pegar_na_denuncia_haha(id)

        # se denuncia foi aberta pelo mesmo usuario e esse mesmo usuario deseja reabrir
        elif visto == nomezin:
            abrir_denunciabanquinho(id, cargo, nomezin)
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
        
        return render_template("DenunciaAberta.html", usuario=denuncia)
    
    return redirect(url_for('rotas.inicio'))

######----------######