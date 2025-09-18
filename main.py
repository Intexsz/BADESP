from flask import Flask, redirect, url_for, render_template, request
# a
mensagem = ''
app = Flask(__name__)

user = 'usuarios.txt'
app.secret_key = "AGOCSPX-as9HxMU0xYAbQQlwiNZMpB73irZ7"

CLIENT_ID = "334998652961-c43b5pt422pnfqk98t56pu4d6aphi5fe.apps.googleusercontent.com"

def validar_cpf(cpf):
    cpf = cpf.replace(".", "").replace("-", "")
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig1 = (soma * 10 % 11) % 10

    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig2 = (soma * 10 % 11) % 10

    return dig1 == int(cpf[9]) and dig2 == int(cpf[10])

# rota que busca os usuarios e senhas no arquivo usuarios.txt
@app.route('/login', methods=['POST', 'GET'])
def login():
    mensagem = ""
    # se o metodo for post ele pega os dados do formulario
    if request.method == "POST":
        usuario_digitado = request.form["nome"]
        senha_digitada = request.form["senha"]

        # Ler usuários do arquivo
        usuarios = {}
        # abre o arquivo e le as linhas
        with open(user, "r", encoding="utf-8") as arquivo:
            # para cada linha no arquivo
            for linha in arquivo:
                # remove espaços em branco
                linha = linha.strip()
                # se a linha não estiver em branco
                if linha:
                    # separa o nome e a senha
                    nome, senha = linha.split(":")
                    # adiciona no dicionario
                    usuarios[nome] = senha

        # Checar se usuário e senha batem
        if usuario_digitado in usuarios and usuarios[usuario_digitado] == senha_digitada:
            mensagem = f"Login concluido! Bem-vindo, {usuario_digitado}!"
            return render_template('concluido.html', mensagem=mensagem)
        else:
            mensagem = "Usuário ou senha incorretos!"

    return render_template("login.html", mensagem=mensagem)

# rota para mostrar todos os usuarios e suas senhas
@app.route('/hack')
def hack():
    # mostrar todos os usuarios e suas senhas em uma lista
    with open(user, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines() # ler todas as linhas
        usuarios = [linha.strip() for linha in linhas] # limpa as linhas
        return render_template('hacks.html', usuarios=usuarios) # enviar

# informando os metodos que a rota pode receber
@app.route('/', methods=['POST', 'GET'])
def cadastro():
    global mensagem
    if request.method == 'POST':
        cpf = request.form['cpf']
        senhas = request.form['senha']
        confirmar = request.form['confirmar']
        
        usuarios = {}
        # abre o arquivo e le as linhas
        with open(user, "r", encoding="utf-8") as arquivo:
            # para cada linha no arquivo
            for linha in arquivo:
            # remove espaços em branco
                linha = linha.strip()
                # se a linha não estiver em branco
                if linha:
                    # separa o nome e a senha
                    nome, senha = linha.split(":")
                    # adiciona no dicionario
                    usuarios[nome] = senhas

        if cpf in usuarios and usuarios[cpf] == senhas:
            mensagem = 'usuario ja cadastrado.'
            return render_template('cadastro.html', mensagem=mensagem)
        else:
            if senhas != confirmar:
                mensagem = 'As senhas devem ser iguais'
                return render_template('cadastro.html', mensagem = mensagem)
            else:
                if True:
                    mensagem = 'Cadastro concluido. Bem vindo CPF: {}, a sua senha é: {}'.format(cpf, senhas)
                    # escreve o novo usuario
                    with open(user, "a", encoding="utf-8") as arquivo:
                        arquivo.write(f'{cpf}:{senhas}\n')
                    return redirect(url_for('home'))
                else:
                    mensagem = 'CPF informado invalido'
                    return render_template('cadastro.html', mensagem=mensagem)   
    else:
        return render_template('cadastro.html', mensagem = '')

@app.route('/home')
def home():
    global mensagem
    return render_template('concluido.html',mensagem=mensagem)

if __name__ == '__main__':
  app.run(debug=True)
