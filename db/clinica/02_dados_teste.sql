--
-- PostgreSQL database dump
--



-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-11-10 21:32:29

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5004 (class 0 OID 16598)
-- Dependencies: 224
-- Data for Name: endereco; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.endereco VALUES (1, '20040020', 'Rua da Assembleia', '10', 'Sala 5', 'Centro', 'Rio de Janeiro', 'RJ', '3304557');
INSERT INTO public.endereco VALUES (2, '22041001', 'Rua Barata Ribeiro', '200', NULL, 'Copacabana', 'Rio de Janeiro', 'RJ', '3304557');


--
-- TOC entry 5000 (class 0 OID 16387)
-- Dependencies: 220
-- Data for Name: especie; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.especie VALUES (1, 'Cão', 'Canis lupus familiaris', 'ativo');
INSERT INTO public.especie VALUES (2, 'Gato', 'Felis catus', 'ativo');
INSERT INTO public.especie VALUES (3, 'Ave', 'Aves domésticas e de companhia', 'ativo');


--
-- TOC entry 5002 (class 0 OID 16400)
-- Dependencies: 222
-- Data for Name: raca; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.raca VALUES (1, 'Labrador', 'Porte grande', 'ativo', 1);
INSERT INTO public.raca VALUES (2, 'Poodle', 'Porte pequeno a médio', 'ativo', 1);
INSERT INTO public.raca VALUES (3, 'Siamês', 'Pelo curto', 'ativo', 2);
INSERT INTO public.raca VALUES (4, 'Persa', 'Pelo longo', 'ativo', 2);
INSERT INTO public.raca VALUES (5, 'Calopsita', 'Ave de pequeno porte', 'ativo', 3);


--
-- TOC entry 5006 (class 0 OID 16612)
-- Dependencies: 226
-- Data for Name: tutor; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.tutor VALUES (1, 'Maria Silva', '12345678901', '1990-05-20', 'maria@email.com', '21999990001', 1, '2026-11-10 19:48:18.056557', 'ativo');
INSERT INTO public.tutor VALUES (2, 'João Souza', '98765432100', '1985-11-03', 'joao@email.com', '21999990002', 2, '2026-11-10 19:48:18.056557', 'ativo');


--
-- TOC entry 5010 (class 0 OID 16670)
-- Dependencies: 230
-- Data for Name: animal; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.animal VALUES (1, 'Rex', '2020-03-15', NULL, 'M', 'Caramelo', 28.50, 1, 1, 1, 'ativo', '2026-11-10 19:55:46.240273');
INSERT INTO public.animal VALUES (2, 'Mia', '2022-07-01', NULL, 'F', 'Cinza', 4.20, 1, 2, 3, 'ativo', '2026-11-10 19:55:46.240273');
INSERT INTO public.animal VALUES (3, 'Thor', '2021-10-10', NULL, 'M', 'Preto', 12.00, 2, 1, NULL, 'ativo', '2026-11-10 19:55:46.240273');


--
-- TOC entry 5008 (class 0 OID 16638)
-- Dependencies: 228
-- Data for Name: veterinario; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.veterinario VALUES (1, 'Ana Lima', '11122233344', '12345', 'RJ', 'ana@clinica.com', '21988880001', 'HASH_FICTICIO_ANA', true, '2026-11-10 19:51:32.111843', '2026-11-10 19:51:32.111843', 'ativo', NULL);
INSERT INTO public.veterinario VALUES (2, 'Carlos Pereira', '55566677788', '23456', 'RJ', 'carlos@clinica.com', '21988880002', 'HASH_FICTICIO_CARLOS', true, '2026-11-10 19:51:32.111843', '2026-11-10 19:51:32.111843', 'inativo', NULL);
INSERT INTO public.veterinario VALUES (3, 'Beatriz Costa', '99988877766', '34567', 'SP', 'beatriz@clinica.com', '21988880003', 'HASH_FICTICIO_BEATRIZ', false, NULL, '2026-11-10 19:51:32.111843', 'ativo', NULL);


--
-- TOC entry 5014 (class 0 OID 16736)
-- Dependencies: 234
-- Data for Name: consulta; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.consulta VALUES (1, 1, 1, '2026-10-20 09:00:00', 'Check-up anual', NULL, NULL, 'Saudável', 'Nenhum', NULL, 28.50, 38.5, NULL, 'realizada');
INSERT INTO public.consulta VALUES (2, 1, 1, '2026-11-20 10:00:00', 'Retorno', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'agendada');
INSERT INTO public.consulta VALUES (3, 2, 1, '2026-10-25 14:30:00', 'Vômito', NULL, NULL, 'Gastrite leve', 'Dieta e hidratação', NULL, 4.20, 38.8, NULL, 'realizada');


--
-- TOC entry 5016 (class 0 OID 16765)
-- Dependencies: 236
-- Data for Name: vacina; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.vacina VALUES (1, 1, 1, 'Antirrábica', 'Antirrábica', true, 'Zoetis', 'L2026A', '2026-10-20', 'Dose única', 'Subcutânea', '2027-10-20', '2027-06-30', NULL, 'aplicada');
INSERT INTO public.vacina VALUES (2, 1, 1, 'V10', 'Polivalente', false, 'MSD', 'V10-889', '2026-10-20', '1ª dose', 'Subcutânea', '2026-12-01', '2027-03-31', NULL, 'aplicada');
INSERT INTO public.vacina VALUES (3, 2, 1, 'Antirrábica', 'Antirrábica', true, 'Boehringer', 'L2026B', '2026-10-25', 'Dose única', 'Subcutânea', '2027-10-25', '2027-08-31', NULL, 'aplicada');


--
-- TOC entry 5018 (class 0 OID 16800)
-- Dependencies: 238
-- Data for Name: integracao_governo; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.integracao_governo VALUES (1, 1, 1, 'vacina_antirrabica', 'GOV-2026-0001', 'VAC-1', 'confirmada', '2026-11-10 20:23:08.512795', '2026-11-10 20:36:44.918767', 1, NULL);
INSERT INTO public.integracao_governo VALUES (2, 2, 3, 'vacina_antirrabica', 'GOV-2026-0002', 'VAC-3', 'confirmada', '2026-11-10 20:23:08.512795', '2026-11-10 20:47:07.745028', 2, NULL);


--
-- TOC entry 5012 (class 0 OID 16706)
-- Dependencies: 232
-- Data for Name: vinculo_microchip; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.vinculo_microchip VALUES (2, 2, '985112345678902', 1, '2024-01-10', '2026-11-10 20:05:23.871919', 'ativo');
INSERT INTO public.vinculo_microchip VALUES (1, 1, '985112345678901', 1, '2024-01-10', '2026-11-10 20:05:23.871919', 'substituido');
INSERT INTO public.vinculo_microchip VALUES (4, 1, '985112345678999', 1, '2024-06-01', '2026-11-10 20:08:57.999713', 'ativo');


--
-- TOC entry 5024 (class 0 OID 0)
-- Dependencies: 229
-- Name: animal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.animal_id_seq', 4, true);


--
-- TOC entry 5025 (class 0 OID 0)
-- Dependencies: 233
-- Name: consulta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.consulta_id_seq', 3, true);


--
-- TOC entry 5026 (class 0 OID 0)
-- Dependencies: 223
-- Name: endereco_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.endereco_id_seq', 2, true);


--
-- TOC entry 5027 (class 0 OID 0)
-- Dependencies: 219
-- Name: especie_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.especie_id_seq', 3, true);


--
-- TOC entry 5028 (class 0 OID 0)
-- Dependencies: 237
-- Name: integracao_governo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.integracao_governo_id_seq', 3, true);


--
-- TOC entry 5029 (class 0 OID 0)
-- Dependencies: 221
-- Name: raca_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.raca_id_seq', 5, true);


--
-- TOC entry 5030 (class 0 OID 0)
-- Dependencies: 225
-- Name: tutor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tutor_id_seq', 3, true);


--
-- TOC entry 5031 (class 0 OID 0)
-- Dependencies: 235
-- Name: vacina_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vacina_id_seq', 4, true);


--
-- TOC entry 5032 (class 0 OID 0)
-- Dependencies: 227
-- Name: veterinario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.veterinario_id_seq', 3, true);


--
-- TOC entry 5033 (class 0 OID 0)
-- Dependencies: 231
-- Name: vinculo_microchip_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vinculo_microchip_id_seq', 4, true);


-- Completed on 2026-11-10 21:32:29

--
-- PostgreSQL database dump complete
--



