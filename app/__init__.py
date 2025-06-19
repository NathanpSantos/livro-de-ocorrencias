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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main
    app.register_blueprint(main)

    return app
