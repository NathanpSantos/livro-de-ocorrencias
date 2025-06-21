from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Usuario, Ocorrencia, Historico
from app import db
from datetime import datetime
from io import BytesIO
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from app.utils import enviar_email_ocorrencia
import os

EMAIL_ADMIN = os.environ.get('EMAIL_ADMIN')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('main.index.html')

@main.route('/usuarios')
def listar_usuarios():
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('main.login'))
    usuarios = Usuario.query.all()
    return render_template('main/usuarios.html', usuarios=usuarios)

@main.route('/cadastro', methods=['GET', 'POST'])
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
        return redirect(url_for('main.login'))
    return render_template('cadastro.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['usuario_id'] = usuario.id
            session['usuario_tipo'] = usuario.tipo
            return redirect(url_for('main.painel'))
        else:
            erro = "Email ou senha inválidos."
    return render_template('main/login.html', erro=erro)

@main.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))
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
    return render_template('main/painel.html', ocorrencias=ocorrencias, tipo=tipo, resumo=resumo)

@main.route('/nova_ocorrencia', methods=['POST'])
def nova_ocorrencia():
    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))
    tipo = request.form['tipo']
    descricao = request.form['descricao']

    usuario = Usuario.query.get(session['usuario_id'])

    nova = Ocorrencia(usuario_id=usuario.id, tipo=tipo, descricao=descricao)
    db.session.add(nova)
    db.session.commit()

    # Envia e-mail
    enviar_email_ocorrencia(usuario.nome, usuario.email, tipo, descricao)
    flash("Ocorrência enviada com sucesso! O administrador foi notificado por e-mail.", "success")
    return redirect(url_for('main.painel'))



@main.route('/responder/<int:id>', methods=['POST'])
def responder(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('main.login'))
    resposta = request.form['resposta']
    ocorrencia = Ocorrencia.query.get(id)
    if ocorrencia:
        ocorrencia.resposta = resposta
        ocorrencia.status = 'Respondida'
        historico = Historico(ocorrencia_id=ocorrencia.id, resposta=resposta, status='Respondida')
        ocorrencia.data_ultima_resposta = datetime.utcnow()
        db.session.add(historico)
        db.session.commit()
    return redirect(url_for('main.painel'))

@main.route('/editar_ocorrencia/<int:id>', methods=['GET', 'POST'])
def editar_ocorrencia(id):
    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))
    ocorrencia = Ocorrencia.query.get(id)
    if session['usuario_tipo'] != 'admin' and ocorrencia.usuario_id != session['usuario_id']:
        return redirect(url_for('main.painel'))
    if request.method == 'POST':
        ocorrencia.tipo = request.form['tipo']
        ocorrencia.descricao = request.form['descricao']
        historico = Historico(ocorrencia_id=ocorrencia.id, resposta=ocorrencia.resposta, status=ocorrencia.status)
        db.session.add(historico)
        db.session.commit()
        return redirect(url_for('main.painel'))
    return render_template('main/editar_ocorrencia.html', ocorrencia=ocorrencia)

@main.route('/editar_resposta/<int:id>', methods=['GET', 'POST'])
def editar_resposta(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('main.login'))
    ocorrencia = Ocorrencia.query.get(id)
    if request.method == 'POST':
        ocorrencia.resposta = request.form['resposta']
        ocorrencia.status = 'Respondida'
        historico = Historico(ocorrencia_id=ocorrencia.id, resposta=ocorrencia.resposta, status='Respondida')
        db.session.add(historico)
        db.session.commit()
        return redirect(url_for('main.painel'))
    return render_template('main/editar_resposta.html', ocorrencia=ocorrencia)

@main.route('/historico/<int:ocorrencia_id>')
def historico_respostas(ocorrencia_id):
    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))
    ocorrencia = Ocorrencia.query.get(ocorrencia_id)
    if not ocorrencia:
        return redirect(url_for('main.painel'))
    historico = Historico.query.filter_by(ocorrencia_id=ocorrencia_id).order_by(Historico.data_resposta.desc()).all()
    return render_template('main/historico_respostas.html', ocorrencia=ocorrencia, historico=historico)

@main.route('/promover/<int:id>')
def promover_usuario(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('main.login'))

    usuario = Usuario.query.get(id)
    if usuario:
        usuario.tipo = 'admin'
        db.session.commit()

    return redirect(url_for('main.listar_usuarios'))

@main.route('/excluir/<int:id>')
def excluir_usuario(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('main.login'))

    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()

    return redirect(url_for('main.listar_usuarios'))

@main.route('/rebaixar/<int:id>')
def rebaixar_usuario(id):
    if 'usuario_id' not in session or session['usuario_tipo'] != 'admin':
        return redirect(url_for('main.login'))

    usuario = Usuario.query.get(id)
    if usuario:
        usuario.tipo = 'morador'
        db.session.commit()

    return redirect(url_for('main.listar_usuarios'))

@main.route('/exportar_excel')
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


@main.route('/exportar_pdf')
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



@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

