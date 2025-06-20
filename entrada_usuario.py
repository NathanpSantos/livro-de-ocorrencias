from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(email='acondominio568@gmail.com').first():
        admin = Usuario(
            nome='Administrador',
            email='acondominio568@gmail.com',
            senha_hash=generate_password_hash('admin123'),
            tipo='admin',
            numero_casa='ADM'  # ✅ Adicione esse campo se ele for obrigatório
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin cadastrado com sucesso!")
    else:
        print("⚠️ Admin já existe.")
