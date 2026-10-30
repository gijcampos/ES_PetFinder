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

CREATE TABLE pet_tutor(
  id_pet   INT NOT NULL,
  id_tutor INT NOT NULL,
  PRIMARY KEY (id_pet, id_tutor),
  FOREIGN KEY (id_tutor)   REFERENCES tutor(id_tutor)     ON DELETE CASCADE,
  FOREIGN KEY (id_pet) REFERENCES clinica(id_pet) ON DELETE CASCADE
  );

-- TESTE, PARA FUNCIONAMENTO DAS TABELAS, APAGAR CASO SEJA UTILIZADO!!
INSERT INTO usuario (nome, email, telefone, senha_hash) VALUES
('Ana Souza',    'ana@email.com',      '44988887777', 'hash_de_teste'),
('Carlos Silva', 'carlos@email.com',   '44977778888', 'hash_de_teste'),
('Beatriz Lima', 'beatriz@email.com',  '44966665555', 'hash_de_teste');

INSERT INTO tutor (id_tutor) VALUES (1), (3);

INSERT INTO contato_emergencia (id_contato, id_tutor, parentesco) VALUES
(2, 1, 'Amigo(a)'),
(3, 1, 'Outros'),
(2, 3, 'Pai');

INSERT INTO endereco (id_tutor, cep, logradouro, bairro, numero, cidade, estado, latitude, longitude) VALUES
(1, '87020000', 'Avenida Brasil',   'Zona 4', '1000', 'Maringá', 'PR', -23.425300, -51.938200),
(3, '87013000', 'Avenida Colombo',  'Zona 7', '500',  'Maringá', 'PR', -23.409800, -51.936100);

INSERT INTO pet (id_coleira, id_tutor, nome, especie, raca, idade) VALUES
('COL000001', 1, 'Thor', 'Cachorro', 'Labrador',    4),
('COL000002', 1, 'Mel',  'Gato',     'Siamês',      2),
('COL000003', 3, 'Luna', 'Cachorro', 'Poodle',      6);

INSERT INTO historico_localizacao (id_coleira, data_hora, latitude, longitude) VALUES
('COL000001', DATE_SUB(NOW(), INTERVAL 120 MINUTE), -23.425300, -51.938200),
('COL000001', DATE_SUB(NOW(), INTERVAL 10 MINUTE),  -23.426500, -51.939000),
('COL000002', DATE_SUB(NOW(), INTERVAL 5 MINUTE),   -23.425300, -51.938200),
('COL000003', DATE_SUB(NOW(), INTERVAL 1 DAY),      -23.409800, -51.936100);

INSERT INTO clinica (nome, endereco, telefone) VALUES
('Clínica VetCare',  'Rua das Flores, 100 - Maringá/PR',  '4432221111'),
('Pet Saúde 24h',    'Avenida XV, 200 - Maringá/PR',      '4433334444');

INSERT INTO horario_funcionamento (id_clinica, dia_semana, abre, fecha) VALUES
(1, 2, '08:00', '18:00'), (1, 3, '08:00', '18:00'), (1, 4, '08:00', '18:00'),
(1, 5, '08:00', '18:00'), (1, 6, '08:00', '18:00'), (1, 7, '08:00', '12:00'),
(2, 1, '00:00', '23:59'), (2, 2, '00:00', '23:59'), (2, 3, '00:00', '23:59'),
(2, 4, '00:00', '23:59'), (2, 5, '00:00', '23:59'), (2, 6, '00:00', '23:59'),
(2, 7, '00:00', '23:59');

INSERT INTO tutor_clinica (id_tutor, id_clinica) VALUES (1, 1), (1, 2), (3, 1);

INSERT INTO agendamento (id_tutor, id_coleira, id_clinica, data_hora) VALUES
(1, 'COL000001', 1, DATE_ADD(NOW(), INTERVAL 2 DAY)),
(3, 'COL000003', 1, DATE_ADD(NOW(), INTERVAL 3 DAY));

INSERT INTO notificacao (id_usuario, id_tutor_origem, id_coleira, tipo, data_hora, mensagem) VALUES
(1, 1, 'COL000001', 'SAIDA_RAIO',    DATE_SUB(NOW(), INTERVAL 9 MINUTE), 'Thor saiu do raio de 2 m do endereço.'),
(2, 1, NULL,        'AVISO_CONTATO', DATE_SUB(NOW(), INTERVAL 8 MINUTE), 'Ana está fora da cidade e precisa de ajuda com o pet.');