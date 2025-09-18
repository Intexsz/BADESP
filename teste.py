from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route('/')
def casinha():
    return render_template('Login.html')


if __name__ == '__main__':
    app.run(debug=True)