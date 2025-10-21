import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Dados do remetente e destinatário
remetente = 'juniorsolva2025@gmail.com'
senha = 'phlh cyyd btep epgy'
destinatario = '@gmail.com'

# Criando a mensagem
msg = MIMEMultipart()
msg['From'] = remetente
msg['To'] = destinatario
msg['Subject'] = 'Assunto do Email'

corpo = 'Sabia que vocês são muito?'
msg.attach(MIMEText(corpo, 'plain'))

# Configurando o servidor SMTP do Gmail
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()  # Segurança
server.login(remetente, senha)
texto = msg.as_string()
server.sendmail(remetente, destinatario, texto)
server.quit()

print('Email enviado com sucesso!')
