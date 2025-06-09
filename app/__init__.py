from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
app = Flask(__name__)  # define antes de usar
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ocorrencias.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta'
db.init_app(app)

migrate = Migrate(app, db)  # agora app já está definido

# Evita importações circulares
from app import routes, models
