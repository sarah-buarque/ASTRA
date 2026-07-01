from utils import db
from flask_login import UserMixin
from datetime import datetime


# ==================================================
# USUÁRIO (AGORA COM SUAP)
# ==================================================

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)

    # Identificador único do SUAP
    suap_id = db.Column(db.String(50), unique=True, nullable=False)

    perfil = db.Column(db.String(22), nullable=False)  # aluno / servidor

    nome = db.Column(db.String(150), nullable=False)

    matricula = db.Column(db.String(50), nullable=False)

    nascimento = db.Column(db.Date, nullable=True)

    email = db.Column(db.String(150), nullable=False, unique=True)

    telefone = db.Column(db.String(20), nullable=False)

    # Foto vinda do SUAP
    foto = db.Column(db.String(500), nullable=True)


    # ==================================================
    # MÉTODOS (mantidos só para compatibilidade)
    # ==================================================

    def __repr__(self):
        return f"<Usuario {self.nome} - {self.email}>"


# ==================================================
# PROJETO (MANTIDO IGUAL AO SEU ORIGINAL)
# ==================================================

class Projeto(db.Model):
    __tablename__ = "projeto"

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(150), nullable=False)

    edital = db.Column(db.String(100), nullable=True)

    nome_projeto = db.Column(db.String(150), nullable=False)

    imagem = db.Column(db.String(150), nullable=True)

    coordenador = db.Column(db.String(100), nullable=False)

    campus = db.Column(db.String(100), nullable=False)

    vagas = db.Column(db.Integer, nullable=True)

    descricao = db.Column(db.Text, nullable=False)

    data_projeto = db.Column(db.Date, nullable=False)

    tipo_projeto = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Projeto {self.nome_projeto}>"