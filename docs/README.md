# Documentação — SDM (Sistema de Gestão de Clínica Veterinária)

**Projeto Integrador A3 — Sistemas Distribuídos e Mobile (IBMR)**

**Milestone 1:** 29/10/2026 | **Entrega Final:** 26/11/2026

## Central de Atalhos da Documentação

Acesso rápido aos documentos principais e artefatos técnicos organizados na pasta `docs/`:

* **Documento de requisitos e arquitetura (Milestone 1)**
  * [Leitura nesta página — Seção 1](#1-documento-de-requisitos-e-arquitetura-milestone-1)
  * [Documento Original Completo (PDF)](./A3_SDM.pdf)

* **Diagrama entidade-relacionamento e modelo relacional**
  * [Leitura e visualização nesta página — Seção 2](#2-diagrama-entidade-relacionamento-e-modelo-relacional)
  * [Diagrama Entidade-Relacionamento — Modelo Conceitual (PNG)](./modelo-dados/MER_conceitual_clinica_vet_atributos.drawio.png)
  * [Diagrama Entidade-Relacionamento — Arquivo editável Draw.io (.drawio)](./modelo-dados/MER_conceitual_clinica_vet_atributos.drawio)
  * [Modelo Relacional — PostgreSQL (PNG)](./modelo-dados/MER_clinica_vet.png)
  * [Modelo Relacional — Estrutura do banco pgAdmin (.pgerd)](./modelo-dados/ERD_clinica_vet.pgerd)
  * [Diagrama ER em Código Mermaid — Clínica e Governo (MD)](./diagrama-er.md)

* **Desenho da arquitetura**
  * [Leitura e diagrama nesta página — Seção 3](#3-desenho-da-arquitetura)
  * [Imagem do Desenho da Arquitetura (PNG)](./arquitetura.png)

* **Relatório de testes (entrega final)**
  * [Matriz de cobertura nesta página — Seção 4](#4-relatório-de-testes-entrega-final)
  * [Relatório Completo de Testes e Evidências (MD)](./relatorio-testes.md)

### Atalhos para as Demais Pastas do Repositório

| Componente | Caminho no Repositório | Descrição |
| :--- | :--- | :--- |
| **Raiz do Projeto** | [`README.md`](../README.md) | Visão geral e instruções de execução |
| **Orquestração Docker** | [`docker-compose.yml`](../docker-compose.yml) | Subida dos 3 serviços e 2 bancos PostgreSQL |
| **Variáveis de Ambiente** | [`.env.example`](../.env.example) | Modelo de configuração de segredos e portas |
| **DDL Banco da Clínica** | [`db/clinica/01_schema.sql`](../db/clinica/01_schema.sql) | Script SQL de criação do `clinica_db` |
| **DDL Banco do Governo** | [`db/governo/01_schema.sql`](../db/governo/01_schema.sql) | Script SQL de criação do `governo_db` |
| **API Privada (FastAPI)** | [`api-clinica/`](../api-clinica/) | Backend principal da clínica veterinária |
| **API Governamental (FastAPI)** | [`api-governo/`](../api-governo/) | Serviço simulado de registro de microchips e vacinas |
| **Frontend Web (React + Vite)** | [`frontend/`](../frontend/) | Interface web utilizada pelo veterinário |
| **Coleção de Testes** | [`tests/`](../tests/) | Coleção Postman e suíte de testes automatizados |

## Mapa de Arquivos da Pasta `docs/`

```text
Projeto-A3-Sistemas-IBMR/
└── docs/
    ├── README.md                                              # Índice geral e documentação consolidada
    ├── A3_SDM.pdf                                             # Documento de Requisitos e Arquitetura (Milestone 1)
    ├── diagrama-er.md                                         # Diagramas ER em Mermaid (clinica_db e governo_db)
    ├── arquitetura.png                                        # Desenho visual da arquitetura distribuída
    ├── relatorio-testes.md                                    # Relatório final de execução dos 16 cenários de teste
    └── modelo-dados/                                          # Artefatos da modelagem do banco de dados
        ├── MER_conceitual_clinica_vet_atributos.drawio.png    # Diagrama conceitual (Notação de Chen)
        ├── MER_conceitual_clinica_vet_atributos.drawio        # Código-fonte editável do Draw.io
        ├── MER_clinica_vet.png                                # Diagrama lógico/físico (PostgreSQL)
        └── ERD_clinica_vet.pgerd                              # Definição estrutural exportada do pgAdmin
```

## 1. Documento de Requisitos e Arquitetura (Milestone 1)

> Arquivo original completo disponível em [`docs/A3_SDM.pdf`](./A3_SDM.pdf).

### 1.1. Visão Geral

O **SDM** é um sistema web para gestão de uma clínica veterinária (tutores, animais, veterinários, consultas, microchips RFID e vacinas), composto por **três serviços independentes** que se comunicam via HTTP/JSON:

1. **Frontend Web:** Interface responsiva utilizada pelo veterinário.
2. **API Privada da Clínica:** Concentra regras de negócio, autenticação, persistência e integrações externas.
3. **API Governamental Simulada:** Serviço independente para registro de animais com microchip RFID e recebimento de vacinações antirrábicas.

Além disso, a API privada consome a API pública **ViaCEP** para preenchimento automático de endereços.

> **Regra Central do Projeto:** Toda aplicação de vacina antirrábica deve ser comunicada obrigatoriamente à API governamental, com **tolerância a falhas** (fila de pendência e reenvio automático/manual) e **idempotência** (sem duplicidade no serviço externo).

### 1.2. Atores do Sistema

| Ator | Descrição |
| :--- | :--- |
| **Veterinário** | Único usuário humano do sistema. Precisa estar cadastrado, ativo e com senha confirmada. |
| **API ViaCEP** | Serviço público externo de consulta de CEP (`https://viacep.com.br/ws/{cep}/json/`). |
| **API Governamental Simulada** | Serviço desenvolvido pela equipe simulando a base regulatória governamental. |

### 1.3. Requisitos Funcionais (RF)

#### Autenticação e Controle de Acesso

* **RF01:** Login por e-mail e senha.
* **RF02:** Senha armazenada somente como hash (`bcrypt` ou `argon2`).
* **RF03:** Confirmação da senha por código/link enviado por e-mail (envio simulado).
* **RF04:** Bloqueio de veterinário inativo.
* **RF05:** Bloqueio de veterinário sem senha confirmada.
* **RF06:** Logout e encerramento de sessão.
* **RF07:** Proteção dos endpoints privados (JWT obrigatório).
* **RF08:** Registro de data/hora do último acesso.

#### Cadastros Base

* **RF09:** Tutor — incluir, consultar, alterar e inativar, com CPF validado e único.
* **RF10:** Endereço — cadastrar com consulta automática ao ViaCEP, permitindo complementação manual.
* **RF11:** Tratar CEP inexistente, timeout e indisponibilidade do ViaCEP.
* **RF12:** Espécie — catálogo (ex.: cão, gato, ave).
* **RF13:** Raça — catálogo vinculado à espécie; permitir "sem raça definida" e validar compatibilidade `raça <-> espécie`.
* **RF14:** Veterinário — manter dados do profissional (CRMV, UF, e-mail, situação etc.).
* **RF15:** Animal — cadastrar e atualizar, sempre vinculado a um tutor, uma espécie e (opcionalmente) uma raça.

#### Microchip RFID

* **RF16:** Vincular microchip a um animal por veterinário autenticado e ativo.
* **RF17:** Garantir unicidade global do código do microchip.
* **RF18:** Registrar veterinário responsável e data do vínculo.
* **RF19:** Substituir microchip preservando o histórico anterior.
* **RF20:** Consultar dados do animal e a situação da integração governamental.

#### Atendimento Clínico

* **RF21:** Registrar consultas (animal, veterinário, data/hora, motivo, anamnese, sintomas, diagnóstico, tratamento, prescrição, peso, temperatura, observações e situação).
* **RF22:** Consultar histórico de consultas por animal.
* **RF23:** Registrar vacinas aplicadas/agendadas (nome, tipo, indicador antirrábica, fabricante, lote, data, dose, via, próxima dose, validade do lote, observações e situação).
* **RF24:** Consultar histórico de vacinação e próximas doses previstas.

#### Integração Governamental & API Simulada

* **RF25:** Cadastrar e atualizar animal na API governamental.
* **RF26:** Comunicar toda vacina antirrábica aplicada à API governamental após o registro local.
* **RF27:** Registrar resultado da comunicação e protocolo retornado.
* **RF28:** Em caso de indisponibilidade, manter a vacinação local e deixar a comunicação pendente.
* **RF29:** Permitir reenvio automático (job periódico) e manual.
* **RF30:** Garantir idempotência para que reenvios não gerem duplicidade no serviço externo.
* **RF31:** Consultar o estado de cada comunicação.
* **RF32:** Não comunicar vacinas que não sejam antirrábicas.
* **RF33:** API Governamental — cadastrar, consultar (por microchip) e atualizar animal.
* **RF34:** API Governamental — receber e registrar vacinação antirrábica.
* **RF35:** API Governamental — validar dados, impedir duplicidade, gerar protocolo e retornar resultado.
* **RF36:** API Governamental — simular erros de validação e indisponibilidade (modo de falha configurável).
* **RF37:** API Governamental — consultar operação por protocolo.

### 1.4. Requisitos Não Funcionais (RNF)

* **RNF01:** Interface web responsiva.
* **RNF02:** Comunicação exclusiva via API REST entre frontend e backend.
* **RNF03:** Banco de dados relacional (PostgreSQL).
* **RNF04:** Validação de dados tanto no frontend quanto no backend.
* **RNF05:** Tratamento adequado de erros HTTP, timeout e indisponibilidade.
* **RNF06:** Autenticação e autorização nos endpoints protegidos.
* **RNF07:** Armazenamento seguro de credenciais (hash de senhas e segredos em variáveis de ambiente).
* **RNF08:** Log e auditoria das operações de integração.
* **RNF09:** Documentação interativa dos endpoints via Swagger/OpenAPI.
* **RNF10:** Código organizado em camadas e componentes.
* **RNF11:** Uso exclusivo de dados fictícios na demonstração.
* **RNF12:** Identificação explícita da API governamental como simulada na interface e na documentação.

### 1.5. Regras de Negócio (RN)

| ID | Regra de Negócio |
| :--- | :--- |
| **RN01** | Somente veterinário ativo e com senha confirmada pode acessar o sistema. |
| **RN02** | CPF de tutor e de veterinário deve ser válido e único. |
| **RN03** | Todo animal possui exatamente um tutor responsável. |
| **RN04** | A raça escolhida deve pertencer à espécie do animal (ou ser nula). |
| **RN05** | O código do microchip é único em todo o sistema, inclusive no histórico. |
| **RN06** | Um animal possui no máximo um vínculo de microchip ativo por vez. |
| **RN07** | Substituir microchip encerra o vínculo anterior (`ativo = false`, `data_fim`) e cria um novo, preservando o histórico. |
| **RN08** | A vacina é classificada como antirrábica pelo campo estruturado (`eh_antirrabica`), nunca por texto livre. |
| **RN09** | Vacina antirrábica aplicada gera uma solicitação de integração, independentemente de o animal já existir no serviço externo. |
| **RN10** | A comunicação externa ocorre somente após a gravação local da vacina. |
| **RN11** | Falha na comunicação externa nunca desfaz o registro local da vacina. |
| **RN12** | Cada solicitação possui chave de idempotência; repetir a chave retorna o mesmo resultado sem criar novo registro. |
| **RN13** | Registro local da vacina é independente da confirmação do governo; o sistema exibe ambos os estados separadamente. |
| **RN14** | A exclusão de registros é sempre lógica (via campo `situacao` ou `ativo`). |
| **RN15** | Para enviar vacina, o animal deve possuir microchip ativo e cadastro no governo (caso não tenha, a clínica envia `CADASTRO_ANIMAL` antes). |

### 1.6. Stack Tecnológica

| Camada | Tecnologia | Justificativa |
| :--- | :--- | :--- |
| **Frontend** | React + Vite | Componentização, resposta rápida e interface responsiva. |
| **API Privada** | Python 3.12 + FastAPI | Geração automática de Swagger/OpenAPI, validação com Pydantic e alta produtividade. |
| **API Governamental** | Python + FastAPI (projeto separado) | Mesma stack reduz curva de aprendizado mantendo independência total entre serviços. |
| **Banco de Dados** | PostgreSQL 16 | Banco relacional robusto com suporte a índices únicos parciais e restrições `CHECK`. |
| **ORM e Migrações** | SQLAlchemy 2 + Alembic | Mapeamento objeto-relacional e versionamento estruturado do esquema. |
| **Autenticação** | $JWT + bcrypt$ | Padrão seguro para APIs REST stateless. |
| **Jobs de Reenvio** | APScheduler | Processamento periódico de pendências dentro da API privada sem infraestrutura extra. |
| **Cliente HTTP** | `httpx` | Suporte nativo a timeouts configuráveis e políticas de retry. |
| **Testes** | Postman + `pytest` | Coleção de testes de integração exigida e testes automatizados. |
| **Infraestrutura Local** | Docker Compose | Orquestração dos 3 serviços e dos 2 bancos PostgreSQL com um único comando. |

## 2. Diagrama Entidade-Relacionamento e Modelo Relacional

O modelo de dados da clínica (`clinica_db`, `schema public`) possui **10 tabelas** principais, complementado por **3 tabelas** isoladas no banco governamental (`governo_db`). Todas as chaves primárias utilizam `BIGSERIAL` e a exclusão é lógica.

### 2.1. Artefatos da Modelagem

| Artefato | Formato | Atalho no Repositório |
| :--- | :--- | :--- |
| **Modelo Conceitual (MER)** | Imagem (PNG) | [`docs/modelo-dados/MER_conceitual_clinica_vet_atributos.drawio.png`](./modelo-dados/MER_conceitual_clinica_vet_atributos.drawio.png) |
| **Modelo Conceitual (Editável)** | Draw.io (`.drawio`) | [`docs/modelo-dados/MER_conceitual_clinica_vet_atributos.drawio`](./modelo-dados/MER_conceitual_clinica_vet_atributos.drawio) |
| **Modelo Relacional (PostgreSQL)** | Imagem (PNG) | [`docs/modelo-dados/MER_clinica_vet.png`](./modelo-dados/MER_clinica_vet.png) |
| **Esquema Exportado (pgAdmin)** | Projeto pgAdmin (`.pgerd`) | [`docs/modelo-dados/ERD_clinica_vet.pgerd`](./modelo-dados/ERD_clinica_vet.pgerd) |
| **Diagrama ER em Mermaid (Clínica + Governo)** | Markdown (MD) | [`docs/diagrama-er.md`](./diagrama-er.md) |

### 2.2. Visualização dos Diagramas

#### Diagrama Entidade-Relacionamento (Modelo Conceitual — Notação de Chen)

![Diagrama Entidade-Relacionamento (Modelo Conceitual)](./modelo-dados/MER_conceitual_clinica_vet_atributos.drawio.png)

#### Modelo Relacional (Lógico/Físico — PostgreSQL `schema public`)

![Modelo Relacional (PostgreSQL)](./modelo-dados/MER_clinica_vet.png)

### 2.3. Dicionário Resumido das Entidades

#### Banco da Clínica (`clinica_db`)

* **`endereco`:** `id` (PK), `cep`, `logradouro`, `numero`, `complemento`, `bairro`, `cidade`, `uf`, `codigo_ibge`.
* **`tutor`:** `id` (PK), `endereco_id` (FK), `nome_completo`, `cpf` (`UNIQUE`), `data_nascimento`, `email`, `telefone`, `data_cadastro`, `situacao` (`ATIVO`/`INATIVO`).
* **`especie`:** `id` (PK), `nome` (`UNIQUE`), `descricao`, `situacao`.
* **`raca`:** `id` (PK), `especie_id` (FK), `nome`, `descricao`, `situacao`, `UNIQUE(especie_id, nome)`.
* **`veterinario`:** `id` (PK), `nome_completo`, `cpf` (`UNIQUE`), `crmv_numero`, `crmv_uf` (`UNIQUE` em conjunto), `email` (`UNIQUE`), `telefone`, `senha_hash`, `senha_confirmada`, `data_confirmacao`, `codigo_confirmacao`, `codigo_expira_em`, `data_cadastro`, `situacao`, `ultimo_acesso`.
* **`animal`:** `id` (PK), `tutor_id` (FK `NOT NULL`), `especie_id` (FK `NOT NULL`), `raca_id` (FK `NULL`), `nome`, `data_nascimento`, `idade_estimada_meses`, `sexo`, `cor`, `peso_atual`, `situacao`. *(Regra `CHECK`: `data_nascimento` ou `idade_estimada_meses` preenchido)*.
* **`vinculo_microchip`:** `id` (PK), `animal_id` (FK), `veterinario_id` (FK), `codigo_microchip` (`UNIQUE` global), `data_vinculo`, `data_fim`, `ativo`, `motivo_substituicao`. *(Índice único parcial em `(animal_id)` onde `ativo = true`)*.
* **`consulta`:** `id` (PK), `animal_id` (FK), `veterinario_id` (FK), `data_hora`, `motivo`, `anamnese`, `sintomas`, `diagnostico`, `tratamento`, `prescricao`, `peso`, `temperatura`, `observacoes`, `situacao` (`AGENDADA`/`REALIZADA`/`CANCELADA`/`NAO_COMPARECEU`).
* **`vacina`:** `id` (PK), `animal_id` (FK), `veterinario_id` (FK), `nome_vacina`, `tipo`, `eh_antirrabica`, `fabricante`, `lote`, `data_aplicacao`, `dose_etapa`, `via_aplicacao`, `data_proxima_dose`, `validade_lote`, `observacoes`, `situacao` (`AGENDADA`/`APLICADA`/`CANCELADA`). *(Regras `CHECK`: `tipo = 'ANTIRRABICA'` <-> `eh_antirrabica = true`; `situacao = 'APLICADA'` exige `data_aplicacao`, `lote` e `fabricante`)*.
* **`integracao_governo`:** `id` (PK), `animal_id` (FK `NOT NULL`), `vacina_id` (FK `NULL`), `tipo_operacao` (`CADASTRO_ANIMAL`/`ATUALIZACAO_ANIMAL`/`VACINA_ANTIRRABICA`), `protocolo_externo`, `chave_idempotencia` (`UNIQUE`), `situacao` (`PENDENTE`/`ENVIADA`/`CONFIRMADA`/`FALHA`), `data_solicitacao`, `data_resposta`, `tentativas`, `mensagem_erro`, `payload_enviado` (JSON).

#### Banco da API Governamental (`governo_db`)

* **`animal_governo`:** `id` (PK), `microchip` (`UNIQUE`), `nome`, `especie`, `raca`, `sexo`, `data_nascimento`, `tutor_nome`, `tutor_cpf`, `data_registro`, `data_atualizacao`.
* **`vacinacao_antirrabica`:** `id` (PK), `animal_id` (FK), `fabricante`, `lote`, `vacina`, `data_aplicacao`, `veterinario_nome`, `veterinario_crmv`, `chave_idempotencia` (`UNIQUE`).
* **`operacao`:** `id` (PK), `protocolo` (`UNIQUE`), `tipo`, `situacao`, `data`, `mensagem`.

## 3. Desenho da Arquitetura

> Arquivo gráfico complementar disponível em [`docs/arquitetura.png`](./arquitetura.png).

### 3.1. Topologia de Serviços e Portas

| Serviço / Recurso | Porta | Banco Associado | Responsabilidade |
| :--- | :--- | :--- | :--- |
| **Frontend Web (React + Vite)** | `5173` | — | Interface do veterinário, validações de formulário e consumo da API privada. |
| **API Privada da Clínica (FastAPI)** | `8000` | `clinica_db` | Autenticação JWT, regras de negócio, persistência e integração com ViaCEP e Governo. |
| **API Governamental Simulada (FastAPI)** | `8001` | `governo_db` | Registro de animais e vacinações antirrábicas, geração de protocolos e simulação de falhas. |
| **PostgreSQL (Clínica)** | `5432` | `clinica_db` | Persistência operacional da clínica veterinária. |
| **PostgreSQL (Governo)** | `5433` | `governo_db` | Persistência isolada do órgão regulador (separação física demonstrável). |

### 3.2. Fluxo de Comunicação e Camadas

```mermaid
flowchart LR
    FE["Frontend Web<br/>(React + Vite :5173)"] -->|HTTP/JSON + Bearer JWT| API["API Privada da Clínica<br/>(FastAPI :8000)"]
    API -->|SQLAlchemy| DB1[("PostgreSQL<br/>clinica_db :5432")]
    API -->|GET /ws/cep/json/<br/>timeout 5s| VIACEP["API Pública<br/>ViaCEP"]
    API -->|HTTP/JSON +<br/>Idempotency-Key| GOV["API Governamental Simulada<br/>(FastAPI :8001)"]
    GOV -->|SQLAlchemy| DB2[("PostgreSQL<br/>governo_db :5433")]
```

* **Isolamento:** O frontend nunca se comunica diretamente com a API governamental nem com o ViaCEP.
* **Arquitetura em Camadas (API Privada):**
  * `routers`: Endpoints HTTP e validação de entrada.
  * `services`: Regras de negócio (ex.: `VacinaService`, `IntegracaoService`).
  * `repositories`: Acesso e persistência no banco de dados.
  * `models` / `schemas`: Entidades SQLAlchemy e DTOs Pydantic.
  * `clients`: Clientes HTTP isolados (`ViaCepClient`, `GovernoClient`).
  * `core`: Configurações, variáveis de ambiente, segurança JWT/bcrypt e logs.

### 3.3. Fluxo da Vacina Antirrábica e Máquina de Estados

1. O veterinário registra a vacina via `POST /api/vacinas` e a transação local é confirmada no `clinica_db`.
2. Se `eh_antirrabica = true` e `situacao = APLICADA`, cria-se um registro em `integracao_governo` com `situacao = PENDENTE`, `tipo_operacao = VACINA_ANTIRRABICA` e `chave_idempotencia` derivada do ID da aplicação.
3. Caso o animal ainda não possua cadastro confirmado no governo, a clínica envia primeiramente a operação `CADASTRO_ANIMAL`.
4. Ao iniciar o envio ao governo, o status muda para `ENVIADA`:
   * **Resposta `2xx` com protocolo:** status passa para `CONFIRMADA` (salva protocolo e `data_resposta`).
   * **Timeout, erro de conexão ou `5xx`:** retorna para `PENDENTE`, incrementa `tentativas` e grava `mensagem_erro`.
   * **Erro `4xx` de validação:** muda para `FALHA` (exige correção cadastral e reenvio manual).
5. Um job periódico (a cada 60 segundos via APScheduler) reprocessa registros `PENDENTE` até o limite de **5 tentativas automáticas** (após o limite, assume `FALHA`). Também há suporte para reenvio manual via `POST /api/integracoes/{id}/reenviar`.

### 3.4. Contratos Principais (Endpoints REST)

#### API Privada (`:8000`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Autentica veterinário e retorna token JWT |
| `POST` | `/api/auth/confirmar-senha` | Valida código de confirmação de cadastro |
| `POST` | `/api/auth/logout` | Encerra e invalida a sessão atual |
| `POST` / `GET` / `PUT` | `/api/tutores`, `/api/tutores/{id}` | CRUD completo de tutores |
| `GET` | `/api/cep/{cep}` | Consulta endereço via ViaCEP |
| `POST` / `GET` / `PUT` | `/api/animais`, `/api/animais/{id}` | Cadastro, listagem, detalhes e atualização de animais |
| `POST` | `/api/animais/{id}/microchip` | Vincula ou substitui microchip RFID |
| `POST` / `GET` | `/api/consultas`, `/api/animais/{id}/consultas` | Registro e histórico de consultas clínicas |
| `POST` / `GET` | `/api/vacinas`, `/api/animais/{id}/vacinas` | Registro de vacinas, histórico e próximas doses |
| `GET` | `/api/integracoes`, `/api/integracoes/{id}` | Consulta o estado das comunicações governamentais |
| `POST` | `/api/integracoes/{id}/reenviar` | Dispara reenvio manual da integração |

#### API Governamental Simulada (`:8001`)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/governo/animais` | Cadastra animal na base governamental |
| `GET` / `PUT` | `/api/governo/animais/{microchip}` | Consulta ou atualiza animal pelo código do microchip |
| `POST` | `/api/governo/vacinacoes-antirrabicas` | Registra vacinação antirrábica (exige cabeçalho `Idempotency-Key`) |
| `GET` | `/api/governo/operacoes/{protocolo}` | Consulta status e detalhes de operação pelo protocolo |
| `POST` | `/api/governo/admin/modo-falha` | Ativa/desativa simulação de indisponibilidade e erros |

## 4. Relatório de Testes (Entrega Final)

> Relatório detalhado e evidências da entrega final (**26/11/2026**) disponíveis em [`docs/relatorio-testes.md`](./relatorio-testes.md) e na coleção [`tests/`](../tests/).

### 4.1. Matriz de Cobertura dos 16 Testes Obrigatórios

| Cenário | Descrição do Teste | Requisitos / Regras Cobertos |
| :--- | :--- | :--- |
| **01 – 04** | Login válido, bloqueio de inativo, bloqueio de não confirmado e senha incorreta | `RF01` – `RF05`, `RN01` |
| **05** | Cadastro de tutor e bloqueio de CPF duplicado/inválido | `RF09`, `RN02` |
| **06** | Consulta de CEP válido e tratamento de CEP inexistente/indisponível | `RF10`, `RF11` |
| **07 – 08** | Cadastro de animal, vínculo de microchip e bloqueio de microchip duplicado | `RF15` – `RF18`, `RN05` |
| **09** | Registro de consulta clínica e consulta de histórico do animal | `RF21`, `RF22` |
| **10** | Registro de vacina e visualização de histórico / próximas doses | `RF23`, `RF24` |
| **11** | Cadastro e atualização de dados do animal na API governamental | `RF25`, `RF33` |
| **12 – 13** | Envio automático de vacina antirrábica e não envio de vacinas comuns | `RF26`, `RF32`, `RN08` |
| **14** | Simulação de indisponibilidade do governo e manutenção da vacina como `PENDENTE` | `RF28`, `RF36`, `RN11` |
| **15** | Reenvio automático/manual após recuperação do serviço e obtenção de protocolo | `RF29`, `RF27` |
| **16** | Repetição de envio com mesma `Idempotency-Key` sem gerar duplicidade | `RF30`, `RN12` |

## Checklist de Entregas

### Milestone 1 (29/10/2026)

* [x] Levantamento e detalhamento dos requisitos funcionais e não funcionais
* [x] Definição das regras de negócio (`RN01` a `RN15`)
* [x] Diagrama ER conceitual e modelo relacional PostgreSQL (`docs/modelo-dados/`)
* [x] Definição e justificativa da stack tecnológica
* [x] Especificação da arquitetura distribuída, contratos REST e máquina de estados
* [x] Estruturação do repositório Git e ambiente Docker Compose

### Entrega Final (26/11/2026)

* [x] Consolidação da documentação e atalhos em `docs/README.md`
* [ ] Upload do desenho da arquitetura (`docs/arquitetura.png`)
* [ ] Execução e registro de evidências dos 16 cenários obrigatórios (`docs/relatorio-testes.md` e `tests/`)
