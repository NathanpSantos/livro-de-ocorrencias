import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADMIN = os.environ.get('EMAIL_ADMIN')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

def enviar_email_ocorrencia(nome, email_usuario, tipo, descricao):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_ADMIN
    msg['Subject'] = f'Nova Ocorrência de {nome}'

    corpo = f"""
    Uma nova ocorrência foi registrada.

    Usuário: {nome}
    E-mail: {email_usuario}
    Tipo: {tipo}
    Descrição: {descricao}

    Acesse o sistema para responder.
    """

    msg.attach(MIMEText(corpo, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print("E-mail enviado com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


def enviar_email_resposta(nome, email_destino, tipo, resposta):
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = email_destino
    msg['Subject'] = f"Resposta da sua ocorrência ({tipo})"

    corpo = f"""
    Olá, {nome}!

    Sua ocorrência do tipo "{tipo}" foi respondida pelo administrador.

    Resposta:
    {resposta}

    Acompanhe o status no painel do sistema.

    Atenciosamente,
    Sistema de Ocorrências
    """

    msg.attach(MIMEText(corpo, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_SENDER, EMAIL_PASSWORD)
            servidor.send_message(msg)
            print("E-mail de resposta enviado ao morador.")
    except Exception as e:
        print(f"Erro ao enviar e-mail de resposta: {e}")