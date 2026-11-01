CREATE DATABASE IF NOT EXISTS coleira_pet CHARACTER SET utf8mb4;
USE coleira_pet;

-- Filhos primeiro, pais por último
DROP TABLE IF EXISTS pet_tutor;
DROP TABLE IF EXISTS notificacao;
DROP TABLE IF EXISTS agendamento;
DROP TABLE IF EXISTS historico_localizacao;
DROP TABLE IF EXISTS tutor_clinica;
DROP TABLE IF EXISTS horario_funcionamento;
DROP TABLE IF EXISTS clinica;
DROP TABLE IF EXISTS pet;
DROP TABLE IF EXISTS endereco;
DROP TABLE IF EXISTS contato_emergencia;
DROP TABLE IF EXISTS tutor;
DROP TABLE IF EXISTS usuario;


CREATE TABLE usuario (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  nome       VARCHAR(100) NOT NULL,
  email      VARCHAR(120) NOT NULL UNIQUE,
  telefone   CHAR(11)     NOT NULL,
  senha_hash VARCHAR(255) NOT NULL
);

CREATE TABLE tutor (
  id_tutor INT PRIMARY KEY,
  FOREIGN KEY (id_tutor) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE contato_emergencia (
  id_contato INT NOT NULL,
  id_tutor   INT NOT NULL,
  parentesco ENUM('Pai','Mãe','Filho(a)','Amigo(a)','Cônjuge','Outros') NOT NULL,
  PRIMARY KEY (id_contato, id_tutor),
  FOREIGN KEY (id_contato) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
  FOREIGN KEY (id_tutor)   REFERENCES tutor(id_tutor)     ON DELETE CASCADE
);

CREATE TABLE endereco (
  id_endereco INT AUTO_INCREMENT PRIMARY KEY,
  id_tutor    INT NOT NULL,
  cep         CHAR(8)      NOT NULL,
  logradouro  VARCHAR(150) NOT NULL,
  bairro      VARCHAR(80),
  numero      VARCHAR(10),
  cidade      VARCHAR(80)  NOT NULL,
  estado      CHAR(2)      NOT NULL,
  latitude    DECIMAL(9,6),
  longitude   DECIMAL(9,6),
  FOREIGN KEY (id_tutor) REFERENCES tutor(id_tutor) ON DELETE CASCADE
);

CREATE TABLE pet (
  id_coleira CHAR(9) PRIMARY KEY,
  id_tutor   INT NOT NULL,
  nome       VARCHAR(60) NOT NULL,
  especie    VARCHAR(30),
  raca       VARCHAR(50),
  idade      TINYINT UNSIGNED,
  FOREIGN KEY (id_tutor) REFERENCES tutor(id_tutor)
);

CREATE TABLE historico_localizacao (
  id_localizacao BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_coleira     CHAR(9) NOT NULL,
  data_hora      DATETIME NOT NULL,
  latitude       DECIMAL(9,6) NOT NULL,
  longitude      DECIMAL(9,6) NOT NULL,
  FOREIGN KEY (id_coleira) REFERENCES pet(id_coleira) ON DELETE CASCADE,
  INDEX (id_coleira, data_hora)
);

CREATE TABLE clinica (
  id_clinica INT AUTO_INCREMENT PRIMARY KEY,
  nome       VARCHAR(100) NOT NULL,
  endereco   VARCHAR(200) NOT NULL,
  telefone   VARCHAR(20)
);

CREATE TABLE horario_funcionamento (
  id_clinica INT NOT NULL,
  dia_semana TINYINT NOT NULL,
  abre       TIME NOT NULL,
  fecha      TIME NOT NULL,
  PRIMARY KEY (id_clinica, dia_semana),
  FOREIGN KEY (id_clinica) REFERENCES clinica(id_clinica) ON DELETE CASCADE,
  CHECK (dia_semana BETWEEN 1 AND 7)
);

CREATE TABLE tutor_clinica (
  id_tutor   INT NOT NULL,
  id_clinica INT NOT NULL,
  PRIMARY KEY (id_tutor, id_clinica),
  FOREIGN KEY (id_tutor)   REFERENCES tutor(id_tutor)     ON DELETE CASCADE,
  FOREIGN KEY (id_clinica) REFERENCES clinica(id_clinica) ON DELETE CASCADE
);

CREATE TABLE agendamento (
  id_agendamento INT AUTO_INCREMENT PRIMARY KEY,
  id_tutor       INT NOT NULL,
  id_coleira     CHAR(9) NOT NULL,
  id_clinica     INT NOT NULL,
  data_hora      DATETIME NOT NULL,
  FOREIGN KEY (id_tutor)   REFERENCES tutor(id_tutor),
  FOREIGN KEY (id_coleira) REFERENCES pet(id_coleira),
  FOREIGN KEY (id_clinica) REFERENCES clinica(id_clinica),
  UNIQUE (id_clinica, data_hora)   -- evita dois agendamentos no mesmo horário
);

CREATE TABLE notificacao (
  id_notificacao  BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_usuario      INT NOT NULL,        -- quem recebe
  id_tutor_origem INT NOT NULL,        -- de quem é o alerta
  id_coleira      CHAR(9) NULL,        -- pet envolvido (opcional)
  tipo            ENUM('SAIDA_RAIO','AVISO_CONTATO') NOT NULL,
  data_hora       DATETIME NOT NULL,
  mensagem        VARCHAR(255) NOT NULL,
  lida            BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (id_usuario)      REFERENCES usuario(id_usuario) ON DELETE CASCADE,
  FOREIGN KEY (id_tutor_origem) REFERENCES tutor(id_tutor),
  FOREIGN KEY (id_coleira)      REFERENCES pet(id_coleira)
);

CREATE TABLE pet_tutor (
  id_pet   INT NOT NULL,
  id_tutor INT NOT NULL,
  PRIMARY KEY (id_pet, id_tutor),
  FOREIGN KEY (id_tutor) REFERENCES tutor(id_tutor) ON DELETE CASCADE,
  FOREIGN KEY (id_pet)   REFERENCES pet(id_pet)     ON DELETE CASCADE
);