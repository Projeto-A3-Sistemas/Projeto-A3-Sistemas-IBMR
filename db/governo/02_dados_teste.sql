-- =====================================================================
-- governo_db — dados de teste (FICTÍCIOS) — P4
-- Coerentes com db/clinica/02_dados_teste.sql: as integrações confirmadas
-- lá (GOV-2026-0001 / VAC-1 e GOV-2026-0002 / VAC-3) existem aqui com o
-- mesmo protocolo e a mesma chave. Roda depois do 01_schema.sql.
-- =====================================================================

INSERT INTO animal_governo (id, microchip, nome, especie, raca, sexo, data_nascimento,
                            tutor_nome, tutor_cpf, data_registro, data_atualizacao) VALUES
 (1, '985112345678999', 'Rex', 'Cão',  'Labrador', 'M', '2020-03-15', 'Maria Silva', '12345678901',
  '2026-10-20 09:30:00', '2026-10-20 09:30:00'),
 (2, '985112345678902', 'Mia', 'Gato', 'Siamês',   'F', '2022-07-01', 'Maria Silva', '12345678901',
  '2026-10-25 15:00:00', '2026-10-25 15:00:00');

INSERT INTO vacinacao_antirrabica (id, animal_id, fabricante, lote, vacina, data_aplicacao,
                                   veterinario_nome, veterinario_crmv, chave_idempotencia) VALUES
 (1, 1, 'Zoetis',     'L2026A', 'Antirrábica', '2026-10-20', 'Ana Lima', '12345/RJ', 'VAC-1'),
 (2, 2, 'Boehringer', 'L2026B', 'Antirrábica', '2026-10-25', 'Ana Lima', '12345/RJ', 'VAC-3');

INSERT INTO operacao (id, protocolo, tipo, situacao, data, mensagem) VALUES
 (1, 'GOV-2026-0001', 'VACINA_ANTIRRABICA', 'PROCESSADA', '2026-11-10 20:36:44',
  'Vacinação antirrábica registrada; microchip=985112345678999; chave=VAC-1'),
 (2, 'GOV-2026-0002', 'VACINA_ANTIRRABICA', 'PROCESSADA', '2026-11-10 20:47:07',
  'Vacinação antirrábica registrada; microchip=985112345678902; chave=VAC-3'),
 (3, 'GOV-2026-0003', 'CADASTRO_ANIMAL', 'PROCESSADA', '2026-10-20 09:30:00',
  'Animal registrado; microchip=985112345678999; chave=-'),
 (4, 'GOV-2026-0004', 'CADASTRO_ANIMAL', 'PROCESSADA', '2026-10-25 15:00:00',
  'Animal registrado; microchip=985112345678902; chave=-');

-- Próximo protocolo gerado pela API: GOV-2026-0005
SELECT setval('animal_governo_id_seq', 2, true);
SELECT setval('vacinacao_antirrabica_id_seq', 2, true);
SELECT setval('operacao_id_seq', 4, true);
