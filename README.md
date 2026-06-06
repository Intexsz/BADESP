# BADESP

Sistema web desenvolvido com Flask com objetivo de registrar denuncias contra o bullying

## Sobre o Projeto

O BADESP (Base de Atendimento e Denúncias Escolares de São Paulo) é uma plataforma que permite que alunos denunciem o bullying ou qualquer outro problema referente a escola diretamente para a secretaria ou professores sobre problemas encontrados na escola, como:

- Atitudes inadequadas
- Casos de bullying
- Falta de materiais
- Irregularidades administrativas
- Outros problemas escolares

## ✨ Funcionalidades

# Alunos
- Cadastro de denúncias
- Upload de anexo
- Consulta de denúncias
- Histórico de ocorrências
- Enviar para alguém em especifico

# Administração

- Gerenciamento de denúncias
- Aprovação de denúncias
- Recusa de denúncias
- Arquivamento de denúncias
- Comentários nas denúncias

## Tecnologias Utilizadas

- Python
- MySQL
- HTML5
- CSS3
- JavaScript

## Instalação

1. Baixe o projeto, extraia-o e entre na pasta:

```bash
cd SNEP
```

2. No terminal rodando **python** instale as dependências digitando:

```bash
pip install -r requirements.txt
```
**Observação:** É necessário possuir o Python e o pip instalados corretamente.

3. Inicie o servidor:

   Modo Desenvolvimento:
   Entre no arquivo e execute-o:
   ```bash
   main.py
   ```

   Modo Produção:
   No terminal execute:
   ```bash
   # No Windows:
   python -m waitress --port=5000 main:app

   # No Linux/Mac:
   gunicorn main:app
   ```

4. Com o código sendo executado, acesse no navegador:

```text
http://127.0.0.1:5000
```
ou
```text
http://localhost:8080/login
```
**Atenção:** Para fazer Login no site, requer uma conta institucional google(preferência estadual)

## Status do Projeto

Em desenvolvimento.
