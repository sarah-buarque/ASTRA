from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.utils import secure_filename

import os
import requests

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

from utils import db
from models import Usuario, Projeto
from config import Config

# ==================================================
# CARREGA VARIÁVEIS DE AMBIENTE (.env)
# ==================================================
load_dotenv()

# ==================================================
# CRIAÇÃO DA APLICAÇÃO
# ==================================================
app = Flask(__name__)

# ==================================================
# CONFIGURAÇÃO CENTRALIZADA
# ==================================================
app.config.from_object(Config)

# ==================================================
# BANCO DE DADOS
# ==================================================
db.init_app(app)
migrate = Migrate(app, db)

# ==================================================
# LOGIN MANAGER
# ==================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ==================================================
# OAUTH SUAP
# ==================================================

oauth = OAuth(app)

oauth.register(
    name="suap",
    client_id=app.config["SUAP_CLIENT_ID"],
    client_secret=app.config["SUAP_CLIENT_SECRET"],
    authorize_url="https://suap.ifrn.edu.br/o/authorize/",
    access_token_url="https://suap.ifrn.edu.br/o/token/",
    client_kwargs={"scope": "identificacao"}
)


# ==================================================
# ROTAS PRINCIPAIS
# ==================================================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/contato")
def contato():
    return render_template("contato.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


# ==================================================
# LOGIN (AGORA VIA SUAP)
# ==================================================

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login/suap")
def login_suap():
    redirect_uri = url_for("callback_suap", _external=True)
    return oauth.suap.authorize_redirect(redirect_uri)


# ==================================================
# CALLBACK SUAP
# ==================================================

@app.route("/oauth/callback")
def callback_suap():

    token = oauth.suap.authorize_access_token()
    access_token = token["access_token"]

    resposta = requests.get(
        "https://suap.ifrn.edu.br/api/rh/eu/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    dados = resposta.json()

    usuario = Usuario.query.filter_by(
        email=dados["email"]
    ).first()

    # ==================================================
    # CASO 1: USUÁRIO NÃO EXISTE → VAI PARA CADASTRO
    # ==================================================
    if not usuario:

        session["suap_dados"] = {
            "suap_id": dados["identificacao"],
            "nome": dados["nome_usual"],
            "email": dados["email"],
            "matricula": dados["identificacao"],
            "foto": dados.get("foto"),
            "campus": dados.get("campus")
        }

        flash("Complete seu cadastro", "info")
        return redirect(url_for("cadastro"))

    # ==================================================
    # CASO 2: USUÁRIO EXISTE → LOGIN NORMAL
    # ==================================================
    login_user(usuario)

    if usuario.perfil == "servidor":
        return redirect(url_for("areaservidor"))
    else:
        return redirect(url_for("areaaluno"))


# ==================================================
# CADASTRO (AGORA COM SUAP AUTO-PREENCHIDO)
# ==================================================

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    suap_data = session.get("suap_user")

    if request.method == 'POST':

        nascimento = datetime.strptime(
            request.form['nascimento'], "%Y-%m-%d"
        ).date()

        usuario = Usuario(
            perfil=request.form['perfil'],
            nome=request.form['nome'],
            matricula=request.form['matricula'],
            nascimento=nascimento,
            email=request.form['email'],
            telefone=request.form['telefone'],

            suap_id=suap_data["suap_id"] if suap_data else None,
            foto=suap_data["foto"] if suap_data else None
        )

        # senha "dummy" (não será usada mais)
        #usuario.set_senha("suap_auth_only")

        db.session.add(usuario)
        db.session.commit()

        session.pop("suap_user", None)

        flash("Cadastro concluído!", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html", suap=suap_data)


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ==================================================
# ÁREA ALUNO
# ==================================================

@app.route('/areaaluno')
@login_required
def areaaluno():

    if current_user.perfil != "aluno":
        return redirect(url_for("login"))

    projetos = Projeto.query.all()

    return render_template(
        "areaaluno.html",
        usuario=current_user,
        projetos=projetos
    )


# ==================================================
# ÁREA SERVIDOR
# ==================================================

@app.route('/areaservidor')
@login_required
def areaservidor():

    if current_user.perfil != "servidor":
        return redirect(url_for("login"))

    projetos = Projeto.query.all()

    return render_template(
        "areaservidor.html",
        usuario=current_user,
        projetos=projetos
    )


# ==================================================
# PROJETOS (MANTIDO ORIGINAL)
# ==================================================

@app.route('/projetos')
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


# ==================================================
# EDITAR PERFIL
# ==================================================

@app.route('/editarperfil', methods=['GET', 'POST'])
@login_required
def editarperfil():

    usuario = current_user

    if request.method == 'POST':

        # ==================================================
        # CAMPOS PERMITIDOS PARA EDIÇÃO
        # ==================================================

        usuario.nome = request.form.get('nome')
        usuario.telefone = request.form.get('telefone')

        nascimento = request.form.get('nascimento')

        if nascimento:
            try:
                usuario.nascimento = datetime.strptime(
                    nascimento, "%Y-%m-%d"
                ).date()
            except ValueError:
                flash("Data de nascimento inválida", "error")
                return redirect(url_for('editarperfil'))

        # ==================================================
        # SALVAR ALTERAÇÕES
        # ==================================================

        db.session.commit()

        flash('Perfil atualizado com sucesso!', 'success')

        # ==================================================
        # REDIRECIONAMENTO POR PERFIL
        # ==================================================

        if current_user.perfil == "servidor":
            return redirect(url_for('areaservidor'))
        else:
            return redirect(url_for('areaaluno'))

    return render_template('editarperfil.html', usuario=usuario)


# ==================================================
# EXCLUIR USUÁRIO
# ==================================================

@app.route('/excluir_usuario', methods=['POST'])
@login_required
def excluir_usuario():

    db.session.delete(current_user)
    db.session.commit()
    logout_user()

    return redirect(url_for("home"))


# ==================================================
# PROJETOS CRUD (MANTIDO)
# ==================================================

@app.route('/criarprojeto', methods=['GET', 'POST'])
def criarprojeto():

    if request.method == 'POST':

        file = request.files.get('imagem')
        imagem = None

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            caminho = os.path.join('static/uploads', filename)
            file.save(caminho)
            imagem = caminho

        projeto = Projeto(
            titulo=request.form.get('titulo'),
            edital=request.form.get('edital'),
            nome_projeto=request.form.get('nome_projeto'),
            coordenador=request.form.get('coordenador'),
            campus=request.form.get('campus'),
            vagas=int(request.form.get('vagas')) if request.form.get('vagas') else None,
            descricao=request.form.get('descricao'),
            data_projeto=datetime.strptime(request.form.get('data_projeto'), '%Y-%m-%d').date(),
            tipo_projeto=request.form.get('tipo_projeto'),
            imagem=imagem
        )

        db.session.add(projeto)
        db.session.commit()

        return redirect(url_for("areaservidor"))

    return render_template("criarprojeto.html")


@app.route('/editarprojeto/<int:projeto_id>', methods=['GET', 'POST'])
@login_required
def editarprojeto(projeto_id):

    projeto = Projeto.query.get_or_404(projeto_id)

    if request.method == 'POST':

        projeto.titulo = request.form.get('titulo')
        projeto.edital = request.form.get('edital')
        projeto.nome_projeto = request.form.get('nome_projeto')
        projeto.campus = request.form.get('campus')
        projeto.coordenador = request.form.get('coordenador')
        projeto.vagas = int(request.form.get('vagas')) if request.form.get('vagas') else None
        projeto.descricao = request.form.get('descricao')
        projeto.tipo_projeto = request.form.get('tipo_projeto')

        db.session.commit()

        return redirect(url_for("areaservidor"))

    return render_template('editarprojeto.html', projeto=projeto)


@app.route('/excluirprojeto/<int:projeto_id>', methods=['POST'])
@login_required
def excluirprojeto(projeto_id):

    projeto = Projeto.query.get_or_404(projeto_id)

    db.session.delete(projeto)
    db.session.commit()

    return redirect(url_for("areaservidor"))


# ==================================================
# INIT DB
# ==================================================

with app.app_context():
    db.create_all()


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":
    app.run(debug=True, port=5001)