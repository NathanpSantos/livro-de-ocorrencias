from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Tratamento para URL do banco de dados (Render usa postgres://)
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///banco.db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    # Chave secreta
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')

    # Inicialização do banco e migrações
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
