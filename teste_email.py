import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Dados do remetente e destinatário
remetente = 'denunciasdehaytalo@gmail.com'
senha = 'fpui zjlf ammk kpym'
destinatario = 'juniorsolva2017@gmail.com'

# Criando a mensagem
msg = MIMEMultipart()
msg['From'] = remetente
msg['To'] = destinatario
msg['Subject'] = 'Marcação em Denuncia'

corpo = 'Este email foi enviado a você pois o aluno o marcou em uma denúncia'
msg.attach(MIMEText(corpo, 'plain'))

# Configurando o servidor SMTP do Gmail
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()  # Segurança
server.login(remetente, senha)
texto = msg.as_string()
server.sendmail(remetente, destinatario, texto)
server.quit()

print('Email enviado com sucesso!')