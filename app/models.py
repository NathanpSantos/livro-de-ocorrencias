from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db  # <- importa 'db' do __init__.py já inicializado

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    tipo = db.Column(db.String(20), default='morador')
    numero_casa = db.Column(db.String(20), nullable=False)

class Ocorrencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pendente')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    resposta = db.Column(db.Text)
    respondido_por = db.Column(db.String(100))
    usuario = db.relationship('Usuario', backref='ocorrencias')
    data_ultima_resposta = db.Column(db.DateTime)

class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ocorrencia_id = db.Column(db.Integer, db.ForeignKey('ocorrencia.id'), nullable=False)
    status = db.Column(db.String(50))
    resposta = db.Column(db.Text)
    data_resposta = db.Column(db.DateTime, default=datetime.utcnow)
