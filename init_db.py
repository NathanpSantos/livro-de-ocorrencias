# init_db.py

from app import app, db

# Cria as tabelas no banco de dados
with app.app_context():
    db.create_all()
    print("✅ Banco de dados inicializado com sucesso!")
