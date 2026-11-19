--
-- PostgreSQL database dump
--


-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

-- Started on 2026-11-10 21:13:22

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 230 (class 1259 OID 16670)
-- Name: animal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.animal (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    data_nascimento date,
    idade_estimada_meses integer,
    sexo character(1) NOT NULL,
    cor character varying(50),
    peso_atual numeric(6,2),
    tutor_id integer NOT NULL,
    especie_id integer NOT NULL,
    raca_id integer,
    situacao character varying(10) DEFAULT 'ativo'::character varying NOT NULL,
    data_cadastro timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT animal_check CHECK (((data_nascimento IS NOT NULL) OR (idade_estimada_meses IS NOT NULL))),
    CONSTRAINT animal_idade_estimada_meses_check CHECK ((idade_estimada_meses >= 0)),
    CONSTRAINT animal_peso_atual_check CHECK ((peso_atual > (0)::numeric)),
    CONSTRAINT animal_sexo_check CHECK ((sexo = ANY (ARRAY['M'::bpchar, 'F'::bpchar]))),
    CONSTRAINT animal_situacao_check CHECK (((situacao)::text = ANY ((ARRAY['ativo'::character varying, 'inativo'::character varying])::text[])))
);


--
-- TOC entry 229 (class 1259 OID 16669)
-- Name: animal_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.animal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5045 (class 0 OID 0)
-- Dependencies: 229
-- Name: animal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.animal_id_seq OWNED BY public.animal.id;


--
-- TOC entry 234 (class 1259 OID 16736)
-- Name: consulta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.consulta (
    id integer NOT NULL,
    animal_id integer NOT NULL,
    veterinario_id integer NOT NULL,
    data_hora timestamp without time zone NOT NULL,
    motivo character varying(200) NOT NULL,
    anamnese text,
    sintomas text,
    diagnostico text,
    tratamento text,
    prescricao text,
    peso numeric(6,2),
    temperatura numeric(4,1),
    observacoes text,
    situacao character varying(20) DEFAULT 'agendada'::character varying NOT NULL,
    CONSTRAINT consulta_peso_check CHECK ((peso > (0)::numeric)),
    CONSTRAINT consulta_situacao_check CHECK (((situacao)::text = ANY ((ARRAY['agendada'::character varying, 'realizada'::character varying, 'cancelada'::character varying, 'nao_compareceu'::character varying])::text[])))
);


--
-- TOC entry 233 (class 1259 OID 16735)
-- Name: consulta_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.consulta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5046 (class 0 OID 0)
-- Dependencies: 233
-- Name: consulta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.consulta_id_seq OWNED BY public.consulta.id;


--
-- TOC entry 224 (class 1259 OID 16598)
-- Name: endereco; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.endereco (
    id integer NOT NULL,
    cep character varying(8) NOT NULL,
    logradouro character varying(150) NOT NULL,
    numero character varying(10) NOT NULL,
    complemento character varying(80),
    bairro character varying(80) NOT NULL,
    cidade character varying(80) NOT NULL,
    uf character(2) NOT NULL,
    codigo_ibge character varying(7)
);


--
-- TOC entry 223 (class 1259 OID 16597)
-- Name: endereco_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.endereco_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5047 (class 0 OID 0)
-- Dependencies: 223
-- Name: endereco_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.endereco_id_seq OWNED BY public.endereco.id;


--
-- TOC entry 220 (class 1259 OID 16387)
-- Name: especie; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.especie (
    id integer NOT NULL,
    nome character varying(50) NOT NULL,
    descricao text,
    situacao character varying(10) DEFAULT 'ativo'::character varying NOT NULL
);


--
-- TOC entry 219 (class 1259 OID 16386)
-- Name: especie_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.especie_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5048 (class 0 OID 0)
-- Dependencies: 219
-- Name: especie_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.especie_id_seq OWNED BY public.especie.id;


--
-- TOC entry 238 (class 1259 OID 16800)
-- Name: integracao_governo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.integracao_governo (
    id integer NOT NULL,
    animal_id integer NOT NULL,
    vacina_id integer,
    tipo_operacao character varying(30) NOT NULL,
    protocolo_externo character varying(50),
    chave_idempotencia character varying(100) NOT NULL,
    situacao character varying(12) DEFAULT 'pendente'::character varying NOT NULL,
    data_solicitacao timestamp without time zone DEFAULT now() NOT NULL,
    data_resposta timestamp without time zone,
    tentativas integer DEFAULT 0 NOT NULL,
    mensagem_erro text,
    CONSTRAINT integracao_governo_situacao_check CHECK (((situacao)::text = ANY ((ARRAY['pendente'::character varying, 'enviada'::character varying, 'confirmada'::character varying, 'falha'::character varying])::text[]))),
    CONSTRAINT integracao_governo_tipo_operacao_check CHECK (((tipo_operacao)::text = ANY ((ARRAY['cadastro_animal'::character varying, 'atualizacao_animal'::character varying, 'vacina_antirrabica'::character varying])::text[])))
);


--
-- TOC entry 237 (class 1259 OID 16799)
-- Name: integracao_governo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.integracao_governo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5049 (class 0 OID 0)
-- Dependencies: 237
-- Name: integracao_governo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.integracao_governo_id_seq OWNED BY public.integracao_governo.id;


--
-- TOC entry 222 (class 1259 OID 16400)
-- Name: raca; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.raca (
    id integer NOT NULL,
    nome character varying(50) NOT NULL,
    descricao text,
    situacao character varying(10) DEFAULT 'ativo'::character varying NOT NULL,
    especie_id integer NOT NULL
);


--
-- TOC entry 221 (class 1259 OID 16399)
-- Name: raca_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.raca_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5050 (class 0 OID 0)
-- Dependencies: 221
-- Name: raca_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.raca_id_seq OWNED BY public.raca.id;


--
-- TOC entry 226 (class 1259 OID 16612)
-- Name: tutor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tutor (
    id integer NOT NULL,
    nome_completo character varying(150) NOT NULL,
    cpf character varying(11) NOT NULL,
    data_nascimento date NOT NULL,
    email character varying(120) NOT NULL,
    telefone character varying(20) NOT NULL,
    endereco_id integer NOT NULL,
    data_cadastro timestamp without time zone DEFAULT now() NOT NULL,
    situacao character varying(10) DEFAULT 'ativo'::character varying NOT NULL,
    CONSTRAINT tutor_situacao_check CHECK (((situacao)::text = ANY ((ARRAY['ativo'::character varying, 'inativo'::character varying])::text[])))
);


--
-- TOC entry 225 (class 1259 OID 16611)
-- Name: tutor_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tutor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5051 (class 0 OID 0)
-- Dependencies: 225
-- Name: tutor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tutor_id_seq OWNED BY public.tutor.id;


--
-- TOC entry 236 (class 1259 OID 16765)
-- Name: vacina; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vacina (
    id integer NOT NULL,
    animal_id integer NOT NULL,
    veterinario_id integer NOT NULL,
    nome_vacina character varying(100) NOT NULL,
    tipo_vacina character varying(50) NOT NULL,
    antirrabica boolean DEFAULT false NOT NULL,
    fabricante character varying(100) NOT NULL,
    numero_lote character varying(50) NOT NULL,
    data_aplicacao date,
    dose character varying(30) NOT NULL,
    via_aplicacao character varying(30),
    data_proxima_dose date,
    validade_lote date NOT NULL,
    observacoes text,
    situacao character varying(10) DEFAULT 'agendada'::character varying NOT NULL,
    CONSTRAINT vacina_check CHECK ((((situacao)::text <> 'aplicada'::text) OR (data_aplicacao IS NOT NULL))),
    CONSTRAINT vacina_situacao_check CHECK (((situacao)::text = ANY ((ARRAY['agendada'::character varying, 'aplicada'::character varying, 'cancelada'::character varying])::text[])))
);


--
-- TOC entry 235 (class 1259 OID 16764)
-- Name: vacina_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vacina_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5052 (class 0 OID 0)
-- Dependencies: 235
-- Name: vacina_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vacina_id_seq OWNED BY public.vacina.id;


--
-- TOC entry 228 (class 1259 OID 16638)
-- Name: veterinario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.veterinario (
    id integer NOT NULL,
    nome_completo character varying(150) NOT NULL,
    cpf character varying(11) NOT NULL,
    crmv_numero character varying(15) NOT NULL,
    crmv_uf character(2) NOT NULL,
    email character varying(120) NOT NULL,
    telefone character varying(20) NOT NULL,
    senha_hash character varying(255) NOT NULL,
    senha_confirmada boolean DEFAULT false NOT NULL,
    data_confirmacao timestamp without time zone,
    data_cadastro timestamp without time zone DEFAULT now() NOT NULL,
    situacao character varying(10) DEFAULT 'ativo'::character varying NOT NULL,
    ultimo_acesso timestamp without time zone,
    CONSTRAINT veterinario_situacao_check CHECK (((situacao)::text = ANY ((ARRAY['ativo'::character varying, 'inativo'::character varying])::text[])))
);


--
-- TOC entry 227 (class 1259 OID 16637)
-- Name: veterinario_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.veterinario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5053 (class 0 OID 0)
-- Dependencies: 227
-- Name: veterinario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.veterinario_id_seq OWNED BY public.veterinario.id;


--
-- TOC entry 232 (class 1259 OID 16706)
-- Name: vinculo_microchip; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vinculo_microchip (
    id integer NOT NULL,
    animal_id integer NOT NULL,
    codigo_microchip character varying(30) NOT NULL,
    veterinario_id integer NOT NULL,
    data_implantacao date NOT NULL,
    data_vinculo timestamp without time zone DEFAULT now() NOT NULL,
    situacao character varying(12) DEFAULT 'ativo'::character varying NOT NULL,
    CONSTRAINT vinculo_microchip_situacao_check CHECK (((situacao)::text = ANY ((ARRAY['ativo'::character varying, 'substituido'::character varying])::text[])))
);


--
-- TOC entry 231 (class 1259 OID 16705)
-- Name: vinculo_microchip_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vinculo_microchip_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5054 (class 0 OID 0)
-- Dependencies: 231
-- Name: vinculo_microchip_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vinculo_microchip_id_seq OWNED BY public.vinculo_microchip.id;


--
-- TOC entry 4812 (class 2604 OID 16673)
-- Name: animal id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animal ALTER COLUMN id SET DEFAULT nextval('public.animal_id_seq'::regclass);


--
-- TOC entry 4818 (class 2604 OID 16739)
-- Name: consulta id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.consulta ALTER COLUMN id SET DEFAULT nextval('public.consulta_id_seq'::regclass);


--
-- TOC entry 4804 (class 2604 OID 16601)
-- Name: endereco id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.endereco ALTER COLUMN id SET DEFAULT nextval('public.endereco_id_seq'::regclass);


--
-- TOC entry 4800 (class 2604 OID 16390)
-- Name: especie id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.especie ALTER COLUMN id SET DEFAULT nextval('public.especie_id_seq'::regclass);


--
-- TOC entry 4823 (class 2604 OID 16803)
-- Name: integracao_governo id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integracao_governo ALTER COLUMN id SET DEFAULT nextval('public.integracao_governo_id_seq'::regclass);


--
-- TOC entry 4802 (class 2604 OID 16403)
-- Name: raca id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raca ALTER COLUMN id SET DEFAULT nextval('public.raca_id_seq'::regclass);


--
-- TOC entry 4805 (class 2604 OID 16615)
-- Name: tutor id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tutor ALTER COLUMN id SET DEFAULT nextval('public.tutor_id_seq'::regclass);


--
-- TOC entry 4820 (class 2604 OID 16768)
-- Name: vacina id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vacina ALTER COLUMN id SET DEFAULT nextval('public.vacina_id_seq'::regclass);


--
-- TOC entry 4808 (class 2604 OID 16641)
-- Name: veterinario id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinario ALTER COLUMN id SET DEFAULT nextval('public.veterinario_id_seq'::regclass);


--
-- TOC entry 4815 (class 2604 OID 16709)
-- Name: vinculo_microchip id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vinculo_microchip ALTER COLUMN id SET DEFAULT nextval('public.vinculo_microchip_id_seq'::regclass);


--
-- TOC entry 4864 (class 2606 OID 16689)
-- Name: animal animal_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animal
    ADD CONSTRAINT animal_pkey PRIMARY KEY (id);


--
-- TOC entry 4871 (class 2606 OID 16752)
-- Name: consulta consulta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.consulta
    ADD CONSTRAINT consulta_pkey PRIMARY KEY (id);


--
-- TOC entry 4850 (class 2606 OID 16610)
-- Name: endereco endereco_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.endereco
    ADD CONSTRAINT endereco_pkey PRIMARY KEY (id);


--
-- TOC entry 4842 (class 2606 OID 16427)
-- Name: especie especie_nome_unico; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.especie
    ADD CONSTRAINT especie_nome_unico UNIQUE (nome);


--
-- TOC entry 4844 (class 2606 OID 16398)
-- Name: especie especie_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.especie
    ADD CONSTRAINT especie_pkey PRIMARY KEY (id);


--
-- TOC entry 4877 (class 2606 OID 16821)
-- Name: integracao_governo integracao_governo_chave_idempotencia_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integracao_governo
    ADD CONSTRAINT integracao_governo_chave_idempotencia_key UNIQUE (chave_idempotencia);


--
-- TOC entry 4879 (class 2606 OID 16819)
-- Name: integracao_governo integracao_governo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integracao_governo
    ADD CONSTRAINT integracao_governo_pkey PRIMARY KEY (id);


--
-- TOC entry 4846 (class 2606 OID 16668)
-- Name: raca raca_id_especie_unico; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raca
    ADD CONSTRAINT raca_id_especie_unico UNIQUE (id, especie_id);


--
-- TOC entry 4848 (class 2606 OID 16412)
-- Name: raca raca_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raca
    ADD CONSTRAINT raca_pkey PRIMARY KEY (id);


--
-- TOC entry 4852 (class 2606 OID 16631)
-- Name: tutor tutor_cpf_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tutor
    ADD CONSTRAINT tutor_cpf_key UNIQUE (cpf);


--
-- TOC entry 4854 (class 2606 OID 16629)
-- Name: tutor tutor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tutor
    ADD CONSTRAINT tutor_pkey PRIMARY KEY (id);


--
-- TOC entry 4875 (class 2606 OID 16787)
-- Name: vacina vacina_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vacina
    ADD CONSTRAINT vacina_pkey PRIMARY KEY (id);


--
-- TOC entry 4856 (class 2606 OID 16662)
-- Name: veterinario veterinario_cpf_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinario
    ADD CONSTRAINT veterinario_cpf_key UNIQUE (cpf);


--
-- TOC entry 4858 (class 2606 OID 16666)
-- Name: veterinario veterinario_crmv_numero_crmv_uf_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinario
    ADD CONSTRAINT veterinario_crmv_numero_crmv_uf_key UNIQUE (crmv_numero, crmv_uf);


--
-- TOC entry 4860 (class 2606 OID 16664)
-- Name: veterinario veterinario_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinario
    ADD CONSTRAINT veterinario_email_key UNIQUE (email);


--
-- TOC entry 4862 (class 2606 OID 16660)
-- Name: veterinario veterinario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.veterinario
    ADD CONSTRAINT veterinario_pkey PRIMARY KEY (id);


--
-- TOC entry 4867 (class 2606 OID 16723)
-- Name: vinculo_microchip vinculo_microchip_codigo_microchip_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vinculo_microchip
    ADD CONSTRAINT vinculo_microchip_codigo_microchip_key UNIQUE (codigo_microchip);


--
-- TOC entry 4869 (class 2606 OID 16721)
-- Name: vinculo_microchip vinculo_microchip_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vinculo_microchip
    ADD CONSTRAINT vinculo_microchip_pkey PRIMARY KEY (id);


--
-- TOC entry 4872 (class 1259 OID 16763)
-- Name: idx_consulta_animal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_consulta_animal ON public.consulta USING btree (animal_id);


--
-- TOC entry 4873 (class 1259 OID 16798)
-- Name: idx_vacina_animal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vacina_animal ON public.vacina USING btree (animal_id);


--
-- TOC entry 4865 (class 1259 OID 16734)
-- Name: vinculo_ativo_unico; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX vinculo_ativo_unico ON public.vinculo_microchip USING btree (animal_id) WHERE ((situacao)::text = 'ativo'::text);


--
-- TOC entry 4882 (class 2606 OID 16695)
-- Name: animal animal_especie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animal
    ADD CONSTRAINT animal_especie_id_fkey FOREIGN KEY (especie_id) REFERENCES public.especie(id);


--
-- TOC entry 4883 (class 2606 OID 16700)
-- Name: animal animal_raca_id_especie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animal
    ADD CONSTRAINT animal_raca_id_especie_id_fkey FOREIGN KEY (raca_id, especie_id) REFERENCES public.raca(id, especie_id);


--
-- TOC entry 4884 (class 2606 OID 16690)
-- Name: animal animal_tutor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animal
    ADD CONSTRAINT animal_tutor_id_fkey FOREIGN KEY (tutor_id) REFERENCES public.tutor(id);


--
-- TOC entry 4887 (class 2606 OID 16753)
-- Name: consulta consulta_animal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.consulta
    ADD CONSTRAINT consulta_animal_id_fkey FOREIGN KEY (animal_id) REFERENCES public.animal(id);


--
-- TOC entry 4888 (class 2606 OID 16758)
-- Name: consulta consulta_veterinario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.consulta
    ADD CONSTRAINT consulta_veterinario_id_fkey FOREIGN KEY (veterinario_id) REFERENCES public.veterinario(id);


--
-- TOC entry 4891 (class 2606 OID 16822)
-- Name: integracao_governo integracao_governo_animal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integracao_governo
    ADD CONSTRAINT integracao_governo_animal_id_fkey FOREIGN KEY (animal_id) REFERENCES public.animal(id);


--
-- TOC entry 4892 (class 2606 OID 16827)
-- Name: integracao_governo integracao_governo_vacina_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integracao_governo
    ADD CONSTRAINT integracao_governo_vacina_id_fkey FOREIGN KEY (vacina_id) REFERENCES public.vacina(id);


--
-- TOC entry 4880 (class 2606 OID 16413)
-- Name: raca raca_especie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raca
    ADD CONSTRAINT raca_especie_id_fkey FOREIGN KEY (especie_id) REFERENCES public.especie(id);


--
-- TOC entry 4881 (class 2606 OID 16632)
-- Name: tutor tutor_endereco_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tutor
    ADD CONSTRAINT tutor_endereco_id_fkey FOREIGN KEY (endereco_id) REFERENCES public.endereco(id);


--
-- TOC entry 4889 (class 2606 OID 16788)
-- Name: vacina vacina_animal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vacina
    ADD CONSTRAINT vacina_animal_id_fkey FOREIGN KEY (animal_id) REFERENCES public.animal(id);


--
-- TOC entry 4890 (class 2606 OID 16793)
-- Name: vacina vacina_veterinario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vacina
    ADD CONSTRAINT vacina_veterinario_id_fkey FOREIGN KEY (veterinario_id) REFERENCES public.veterinario(id);


--
-- TOC entry 4885 (class 2606 OID 16724)
-- Name: vinculo_microchip vinculo_microchip_animal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vinculo_microchip
    ADD CONSTRAINT vinculo_microchip_animal_id_fkey FOREIGN KEY (animal_id) REFERENCES public.animal(id);


--
-- TOC entry 4886 (class 2606 OID 16729)
-- Name: vinculo_microchip vinculo_microchip_veterinario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vinculo_microchip
    ADD CONSTRAINT vinculo_microchip_veterinario_id_fkey FOREIGN KEY (veterinario_id) REFERENCES public.veterinario(id);


-- Completed on 2026-11-10 21:13:22

--
-- PostgreSQL database dump complete
--


