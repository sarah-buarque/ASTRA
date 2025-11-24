from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == "admin" and senha == "123":
            return "Login realizado com sucesso!"

    return render_template("login.html")

@app.route("/recuperar-senha")
def recuperar_senha():
    return render_template("recuperarsenha.html")

@app.route("/projetos")
def projetos():
    lista_projetos = [
        {"nome": "PISEW - Integrando Crianças Warao"},
        {"nome": "IFTech - Feira de Tecnologia"},
        {"nome": "Robótica ZN"},
        {"nome": "ASTRA - Ambiente de Saberes e Transmissão de Resultados Acadêmicoos"}
    ]
    return render_template("projetos.html", projetos=lista_projetos)

@app.route('/projeto/<nome>')
def projeto(nome):
    return render_template('projeto_detalhe.html', nome=nome)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form.get('usuario')
        nascimento = request.form['nascimento']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']
        return redirect(url_for('sucesso'))
    return render_template('cadastro.html')

@app.route('/sucesso')
def sucesso():
    return "<h2>Cadastro realizado com sucesso!</h2>"

if __name__ == "__main__":
    app.run(debug=True)

