CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(255) PRIMARY KEY,
    nome VARCHAR(255),
    email VARCHAR(255),
    foto TEXT,
    cargo VARCHAR(50),
    pin VARCHAR(10),
    escola VARCHAR(255),
    ano VARCHAR(50),
    turma VARCHAR(50),
    turmano VARCHAR(100),

    suspenso TINYINT DEFAULT 0,
    motivo_suspensao TEXT,
    data_suspensao DATETIME,
    fim_suspensao DATETIME,
    tipo_suspensao VARCHAR(50),
    suspenso_por_id VARCHAR(255),
    suspenso_por_nome VARCHAR(255),
    suspenso_por_email VARCHAR(255),
    email_fim_suspensao_enviado TINYINT DEFAULT 0,
    matricula_ativa TINYINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS lista_turmas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ano_serie TEXT
);

CREATE TABLE IF NOT EXISTS denuncias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    titulo TEXT NOT NULL,
    tipo TEXT,
    gravidade TEXT NOT NULL,
    descricao TEXT NOT NULL,
    descricao_ia TEXT,
    comentario TEXT,
    data TEXT NOT NULL,
    datavisto TEXT,
    user_id VARCHAR(255) NOT NULL,
    status TEXT NOT NULL,
    cargo TEXT,
    nome TEXT NOT NULL,
    visto TEXT,
    especifico TEXT,
    ano INT,
    turma TEXT,
    envolvidos TEXT,
    escola VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(255) NOT NULL,
    feedback TEXT NOT NULL,
    horario VARCHAR(255) NOT NULL,
    tipo VARCHAR(255) NOT NULL,
    cargo VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(255) NOT NULL UNIQUE,
    font_size INT NOT NULL DEFAULT 16,

    CONSTRAINT fk_config
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS notificacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(255) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    horario VARCHAR(255) NOT NULL,

    CONSTRAINT fk_notificacao
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);