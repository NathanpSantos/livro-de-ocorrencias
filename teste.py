import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

EMAIL_ADMIN = "acondominio568@gmail.com"
EMAIL_SENDER = "nathanprsantos160@gmail.com"
EMAIL_PASSWORD = "cdipawzflagimwer"

def test_email():
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_ADMIN
    msg['Subject'] = "Teste de Envio"
    corpo = "Se você está lendo isso, o envio de e-mail está funcionando!"
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

if __name__ == "__main__":
    test_email()
