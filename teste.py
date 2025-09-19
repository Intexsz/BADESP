from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def casinha():
    return render_template('Login.html')

#oi
if __name__ == '__main__':
    app.run(debug=True)