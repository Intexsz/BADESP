import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

remetente = os.getenv("EMAIL_SENDER")
senha = os.getenv("EMAIL_PASSWORD")


def enviar_email_simples(destinatario, assunto, corpo):
    if not destinatario:
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto

        msg.attach(MIMEText(corpo, "plain", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha)

        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()

        return True

    except Exception as e:
        print("[EMAIL] Erro ao enviar email:", e)
        return False


def formatar_data(data):
    if not data:
        return "Permanente"

    try:
        return data.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        return str(data)


def enviar_email_suspensao(aluno):
    if aluno["tipo_suspensao"] == "permanente":
        duracao = "Permanente"
        fim = "Não possui data de término"
    else:
        duracao = "Temporária"
        fim = formatar_data(aluno["fim_suspensao"])

    assunto = "Sua conta foi suspensa - B.A.D.E.S.P"

    corpo = f"""
Olá, {aluno["nome"]}.

Sua conta foi suspensa no sistema B.A.D.E.S.P.

Motivo:
{aluno["motivo_suspensao"]}

Quem suspendeu:
{aluno["suspenso_por_nome"]}

Horário da suspensão:
{formatar_data(aluno["data_suspensao"])}

Tipo da suspensão:
{duracao}

Término da suspensão:
{fim}

Caso tenha dúvidas, entre em contato com a secretaria da escola.

B.A.D.E.S.P
"""

    return enviar_email_simples(aluno["email"], assunto, corpo)


def enviar_email_fim_suspensao(aluno):
    assunto = "Sua suspensão terminou - B.A.D.E.S.P"

    corpo = f"""
Olá, {aluno["nome"]}.

Sua suspensão no sistema B.A.D.E.S.P terminou.

Você já pode acessar o sistema novamente.

Acesse:
https://www.badesp.online/

B.A.D.E.S.P
"""

    return enviar_email_simples(aluno["email"], assunto, corpo)


def enviar_email_suspensao_removida_aluno(aluno, removido_por):
    assunto = "Sua suspensão foi removida - B.A.D.E.S.P"

    corpo = f"""
Olá, {aluno["nome"]}.

Sua suspensão foi removida por {removido_por["nome"]}.

Você já pode acessar o sistema novamente.

B.A.D.E.S.P
"""

    return enviar_email_simples(aluno["email"], assunto, corpo)


def enviar_email_suspensao_removida_suspensor(aluno, removido_por):
    if not aluno.get("suspenso_por_email"):
        return False

    assunto = "Suspensão removida - B.A.D.E.S.P"

    corpo = f"""
Olá, {aluno["suspenso_por_nome"]}.

A suspensão que você aplicou ao aluno {aluno["nome"]} foi removida.

Removida por:
{removido_por["nome"]}

Email de quem removeu:
{removido_por["email"]}

B.A.D.E.S.P
"""

    return enviar_email_simples(aluno["suspenso_por_email"], assunto, corpo)


def enviar_email_acesso_encerrado(aluno):
    assunto = "Seu acesso foi encerrado - B.A.D.E.S.P"

    corpo = f"""
Olá, {aluno["nome"]}.

Seu acesso ao sistema B.A.D.E.S.P foi encerrado.

Este sistema é exclusivo para alunos que ainda estão cursando na escola.

Mesmo que seu email institucional continue funcionando, o acesso ao sistema foi bloqueado porque sua matrícula não está mais ativa.

B.A.D.E.S.P
"""

    return enviar_email_simples(aluno["email"], assunto, corpo)