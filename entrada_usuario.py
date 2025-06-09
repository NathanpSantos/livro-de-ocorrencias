from app import app, db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(email='nathanprsantos@outlook.com').first():
        admin = Usuario(
            nome='Nathan',
            email='nathanprsantos@outlook.com',
            senha_hash=generate_password_hash('Nathan2010'),
            tipo='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin cadastrado com sucesso!")
    else:
        print("⚠️ Admin já existe.")
