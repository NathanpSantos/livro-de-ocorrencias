from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Usuario, Ocorrencia, Historico
from app import db, app
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import os
from flask import send_file
from io import BytesIO
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from .models import Ocorrencia, Usuario

main = Blueprint('main', __name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/usuarios')
def listar_usuarios():
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('login'))
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        numero_casa = request.form['numero_casa']  # NOVO
        senha_hash = generate_password_hash(senha)

        novo_usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash, numero_casa=numero_casa)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['usuario_id'] = usuario.id
            session['usuario_tipo'] = usuario.tipo
            return redirect(url_for('painel'))
        else:
            erro = "Email ou senha inválidos."
    return render_template('login.html', erro=erro)

@app.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    tipo = session['usuario_tipo']
    filtro_status = request.args.get('filtro_status')
    if tipo == 'admin':
        ocorrencias = Ocorrencia.query.filter_by(status=filtro_status).all() if filtro_status else Ocorrencia.query.all()
        resumo = {
            'total': Ocorrencia.query.count(),
            'pendentes': Ocorrencia.query.filter_by(status='Pendente').count(),
            'em_analise': Ocorrencia.query.filter_by(status='Em análise').count(),
            'respondidas': Ocorrencia.query.filter_by(status='Respondida').count()
        }
    else:
        ocorrencias = Ocorrencia.query.filter_by(usuario_id=usuario_id).all()
        resumo = {}
    return render_template('painel.html', ocorrencias=ocorrencias, tipo=tipo, resumo=resumo)

@app.route('/nova_ocorrencia', methods=['POST'])
def nova_ocorrencia():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    tipo = request.form['tipo']
    descricao = request.form['descricao']
    nova = Ocorrencia(usuario_id=session['usuario_id'], tipo=tipo, descricao=descricao)
    db.session.add(nova)
    db.session.commit()
    return redirect(url_for('painel'))

@app.route('/responder/<int:id>', methods=['POST'])
def responder(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('login'))
    resposta = request.form['resposta']
    ocorrencia = Ocorrencia.query.get(id)
    if ocorrencia:
        ocorrencia.resposta = resposta
        ocorrencia.status = 'Respondida'
        historico = Historico(ocorrencia_id=ocorrencia.id, resposta=resposta, status='Respondida')
        ocorrencia.data_ultima_resposta = datetime.utcnow()
        db.session.add(historico)
        db.session.commit()
    return redirect(url_for('painel'))

@app.route('/editar_ocorrencia/<int:id>', methods=['GET', 'POST'])
def editar_ocorrencia(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    ocorrencia = Ocorrencia.query.get(id)
    if session['usuario_tipo'] != 'admin' and ocorrencia.usuario_id != session['usuario_id']:
        return redirect(url_for('painel'))
    if request.method == 'POST':
        ocorrencia.tipo = request.form['tipo']
        ocorrencia.descricao = request.form['descricao']
        historico = Historico(ocorrencia_id=ocorrencia.id, resposta=ocorrencia.resposta, status=ocorrencia.status)
        db.session.add(historico)
        db.session.commit()
        return redirect(url_for('painel'))
    return render_template('editar_ocorrencia.html', ocorrencia=ocorrencia)

@app.route('/editar_resposta/<int:id>', methods=['GET', 'POST'])
def editar_resposta(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('login'))
    ocorrencia = Ocorrencia.query.get(id)
    if request.method == 'POST':
        ocorrencia.resposta = request.form['resposta']
        ocorrencia.status = 'Respondida'
        historico = Historico(ocorrencia_id=ocorrencia.id, resposta=ocorrencia.resposta, status='Respondida')
        db.session.add(historico)
        db.session.commit()
        return redirect(url_for('painel'))
    return render_template('editar_resposta.html', ocorrencia=ocorrencia)

@app.route('/historico/<int:ocorrencia_id>')
def historico_respostas(ocorrencia_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    ocorrencia = Ocorrencia.query.get(ocorrencia_id)
    if not ocorrencia:
        return redirect(url_for('painel'))
    historico = Historico.query.filter_by(ocorrencia_id=ocorrencia_id).order_by(Historico.data_resposta.desc()).all()
    return render_template('historico_respostas.html', ocorrencia=ocorrencia, historico=historico)

@app.route('/promover/<int:id>')
def promover_usuario(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('login'))

    usuario = Usuario.query.get(id)
    if usuario:
        usuario.tipo = 'admin'
        db.session.commit()

    return redirect(url_for('listar_usuarios'))

@app.route('/excluir/<int:id>')
def excluir_usuario(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('login'))

    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()

    return redirect(url_for('listar_usuarios'))

@app.route('/rebaixar/<int:id>')
def rebaixar_usuario(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('login'))

    usuario = Usuario.query.get(id)
    if usuario:
        usuario.tipo = 'morador'
        db.session.commit()

    return redirect(url_for('listar_usuarios'))

@app.route('/exportar_excel')
def exportar_excel():
    ocorrencias = Ocorrencia.query.all()
    dados = [{
        'Tipo': o.tipo,
        'Descrição': o.descricao,
        'Status': o.status,
        'Data de Criação': o.data_criacao.strftime('%d/%m/%Y %H:%M'),
        'Usuário': o.usuario.nome if o.usuario else 'Desconhecido'
    } for o in ocorrencias]

    df = pd.DataFrame(dados)
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    return send_file(excel_buffer, as_attachment=True, download_name='relatorio_ocorrencias.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/exportar_pdf')
def exportar_pdf():
    ocorrencias = Ocorrencia.query.all()
    dados = [{
        'Tipo': o.tipo,
        'Descrição': o.descricao,
        'Status': o.status,
        'Data de Criação': o.data_criacao.strftime('%d/%m/%Y %H:%M'),
        'Usuário': o.usuario.nome if o.usuario else 'Desconhecido'
    } for o in ocorrencias]

    df = pd.DataFrame(dados)

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    table_data = [df.columns.tolist()] + df.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    doc.build([table])
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name='relatorio_ocorrencias.pdf', mimetype='application/pdf')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
