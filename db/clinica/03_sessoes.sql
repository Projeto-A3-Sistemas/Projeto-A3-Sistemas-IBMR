-- =====================================================================
-- clinica_db — sessões de login (P1)
-- Guarda o identificador (jti) dos tokens encerrados no logout até a
-- data em que expirariam. Não altera nenhuma tabela de 01_criar_tabelas.sql.
-- Roda sozinho quando o container db-clinica sobe pela primeira vez.
-- =====================================================================

CREATE TABLE IF NOT EXISTS token_revogado (
    jti        VARCHAR(36) PRIMARY KEY,
    expira_em  TIMESTAMP   NOT NULL
);
