from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from utils import db
import os

from flask_migrate import Migrate
from models import Usuario, Projeto


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db_usuario = os.getenv('DB_USERNAME')
db_senha = os.getenv('DB_PASSWORD')
db_mydb = os.getenv('DB_DATABASE')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

conexao = f"mysql+pymysql://{db_usuario}:{db_senha}@{db_host}:{db_port}/{db_mydb}"
app.config['SQLALCHEMY_DATABASE_URI'] = conexao
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuario = Usuario(
            perfil=request.form['perfil'],
            nome=request.form['nome'],
            matricula=request.form['matricula'],
            nascimento=request.form['nascimento'],
            email=request.form['email'],
            telefone=request.form['telefone']
        )

        if Usuario.query.filter_by(email=usuario.email).first():
            flash("Este e-mail já está cadastrado.", "error")
            return redirect(url_for('cadastro'))

        usuario.set_senha(request.form['senha'])

        db.session.add(usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_senha(senha):
            login_user(usuario)

            if usuario.perfil == "aluno":
                return redirect(url_for("areaaluno"))
            elif usuario.perfil == "servidor":
                return redirect(url_for("areaservidor"))

        flash("E-mail ou senha incorretos", "error")

    return render_template("login.html")

@app.route('/recuperar_senha')
def recuperar_senha():
    return render_template('recuperar_senha.html')

@app.route('/areaaluno')
@login_required
def areaaluno():
    if current_user.perfil != "aluno":
        return redirect(url_for("login"))

    projetos = Projeto.query.all()
    return render_template("areaaluno.html", usuario=current_user, projetos=projetos)


@app.route('/areaservidor')
@login_required
def areaservidor():
    if current_user.perfil != "servidor":
        return redirect(url_for("login"))
    projetos = Projeto.query.all()
    return render_template("areaservidor.html", usuario=current_user, projetos=projetos)



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


@app.route('/editarperfil', methods=['GET', 'POST'])
@login_required
def editarperfil():
    usuario = current_user 

    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.matricula = request.form['matricula']
        usuario.nascimento = request.form['nascimento']
        usuario.email = request.form['email']
        usuario.telefone = request.form['telefone']

       
        nova_senha = request.form.get('senha')
        if nova_senha:
            usuario.set_senha(nova_senha)

        db.session.commit()  
        flash('Dados atualizados com sucesso!', 'success')
        if current_user.perfil == "servidor":
            return redirect(url_for('areaservidor'))
        elif current_user.perfil == "aluno":
            return redirect(url_for('areaaluno'))
        
    return render_template('editarperfil.html', usuario=usuario)

@app.route('/excluir_usuario', methods=['POST'])
def excluir_usuario():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))  

   
    db.session.delete(current_user)
    db.session.commit()

    
    logout_user()

    
    return redirect(url_for('home'))

@app.route('/criarprojeto', methods=['GET', 'POST'])
def criarprojeto():
    if request.method == 'POST':
    
        titulo = request.form.get('titulo')
        edital = request.form.get('edital')
        nome_projeto = request.form.get('nome_projeto')
        coordenador = request.form.get('coordenador')
        campus = request.form.get('campus')
        vagas = request.form.get('vagas')
        descricao = request.form.get('descricao')
        data_projeto = request.form.get('data_projeto')
        tipo_projeto = request.form.get('tipo_projeto')

        
        if data_projeto:
            data_projeto = datetime.strptime(data_projeto, '%Y-%m-%d').date()
        if vagas:
            vagas = int(vagas)

       
        imagem = None
        file = request.files.get('imagem')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            caminho = os.path.join('static/uploads', filename)
            file.save(caminho)
            imagem = caminho

       
        novo_projeto = Projeto(
            titulo=titulo,
            edital=edital,
            nome_projeto=nome_projeto,
            coordenador=coordenador,
            campus=campus,
            vagas=vagas,
            descricao=descricao,
            data_projeto=data_projeto,
            tipo_projeto=tipo_projeto,
            imagem=imagem
        )

        
        db.session.add(novo_projeto)
        db.session.commit()

        flash('Projeto criado com sucesso!', 'success')
        return redirect(url_for('areaservidor'))

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

        data_projeto = request.form.get('data_projeto')
        if data_projeto:
            projeto.data_projeto = datetime.strptime(data_projeto, '%Y-%m-%d').date()

        file = request.files.get('imagem')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            caminho = os.path.join('static/uploads', filename)
            file.save(caminho)
            projeto.imagem = caminho

        db.session.commit()
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('areaservidor'))  

    return render_template('editarprojeto.html', projeto=projeto)

@app.route('/excluirprojeto/<int:projeto_id>', methods=['POST'])
@login_required
def excluirprojeto(projeto_id):
    projeto = Projeto.query.filter_by(
        id=projeto_id,
        coordenador_id=current_user.id
    ).first_or_404()

    db.session.delete(projeto)
    db.session.commit()

    flash('Projeto excluído com sucesso!', 'success')
    return redirect(url_for('areaservidor'))

@app.route('/detalhesprojeto')
def detalhesprojeto():
    return render_template("detalhesprojeto.html")

@app.route('/visualizarprojetos')
def visualizarprojetos():
    return render_template("visualizarprojetos.html")    


db.init_app(app)
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

