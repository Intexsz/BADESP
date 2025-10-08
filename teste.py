from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def cadastro_pin():
    return render_template('cadastroaluno.html')

@app.route('/Ajuda')
def ajuda():
    return render_template('ajuda.html')

if __name__ == '__main__':
    app.run(debug=True)

