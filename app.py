from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "segredo123"

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

        # Autenticação fictícia (troque por banco de dados)
        if usuario == "admin" and senha == "123":
            return "Login realizado com sucesso!"

        flash("Usuário ou senha incorretos!")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/recuperar-senha")
def recuperar_senha():
    return render_template("recuperarsenha.html")


@app.route("/cadastro")
def cadastro():
    return "<h2>Página de cadastro</h2>"

@app.route('/projetos')
def projetos():
    return render_template('projetos.html')

@app.route('/projeto/<nome>')
def projeto(nome):
    return render_template('projeto_detalhe.html', nome=nome)

if __name__ == "__main__":
    app.run(debug=True)

