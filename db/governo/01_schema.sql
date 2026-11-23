-- =====================================================================
-- governo_db — banco da API Governamental SIMULADA (SDM / A3) — P4
-- Serviço simulado para fins acadêmicos. NÃO é integração oficial.
-- Tabelas e colunas iguais ao diagrama do Milestone 1.
-- Roda sozinho quando o container db-governo sobe pela primeira vez.
-- =====================================================================

CREATE TABLE IF NOT EXISTS animal_governo (
    id                BIGSERIAL PRIMARY KEY,
    microchip         VARCHAR(30)  NOT NULL UNIQUE,
    nome              VARCHAR(100) NOT NULL,
    especie           VARCHAR(50)  NOT NULL,
    raca              VARCHAR(50),
    sexo              CHAR(1)      NOT NULL CHECK (sexo IN ('M', 'F')),
    data_nascimento   DATE,
    tutor_nome        VARCHAR(150) NOT NULL,
    tutor_cpf         VARCHAR(11)  NOT NULL,
    data_registro     TIMESTAMP    NOT NULL DEFAULT NOW(),
    data_atualizacao  TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vacinacao_antirrabica (
    id                  BIGSERIAL PRIMARY KEY,
    animal_id           BIGINT       NOT NULL REFERENCES animal_governo (id),
    fabricante          VARCHAR(100) NOT NULL,
    lote                VARCHAR(50)  NOT NULL,
    vacina              VARCHAR(100) NOT NULL,
    data_aplicacao      DATE         NOT NULL,
    veterinario_nome    VARCHAR(150) NOT NULL,
    veterinario_crmv    VARCHAR(20)  NOT NULL,          -- número/UF, ex.: 12345/RJ
    chave_idempotencia  VARCHAR(100) NOT NULL UNIQUE    -- impede vacinação duplicada
);

CREATE TABLE IF NOT EXISTS operacao (
    id         BIGSERIAL PRIMARY KEY,
    protocolo  VARCHAR(40) NOT NULL UNIQUE,              -- GOV-AAAA-NNNN
    tipo       VARCHAR(30) NOT NULL
               CHECK (tipo IN ('CADASTRO_ANIMAL', 'ATUALIZACAO_ANIMAL', 'VACINA_ANTIRRABICA')),
    situacao   VARCHAR(20) NOT NULL CHECK (situacao IN ('PROCESSADA', 'REJEITADA')),
    data       TIMESTAMP   NOT NULL DEFAULT NOW(),
    mensagem   TEXT                                      -- termina em "; microchip=...; chave=..."
);

CREATE INDEX IF NOT EXISTS idx_vacinacao_animal ON vacinacao_antirrabica (animal_id);
