# Relatório de Testes e Garantia da Qualidade (QA) — Sistema SDM

* **Projeto:** Sistema de Gestão de Clínica Veterinária (SDM) — Projeto Integrador A3 (IBMR)
* **Responsável QA (P6):** Qualidade, Testes Integrados e Documentação Técnica
* **Data da Execução:** 25/11/2026
* **Status Geral:** Aprovado (100% dos 16 cenários obrigatórios validados com sucesso)

---

## 1. Objetivo e Escopo

Este relatório documenta a validação funcional, de regras de negócio e de integração entre a **API Privada da Clínica Veterinária**, a **API Governamental Simulada** e o serviço externo **ViaCEP**. Os testes cobrem o fluxo completo de cadastro, atendimento clínico, imunização antirrábica, resiliência a falhas de comunicação, reenvio manual e idempotência.

---

## 2. Ambiente e Ferramentas de Teste

A infraestrutura foi executada localmente via containers Docker (`docker-compose up --build`), garantindo isolamento entre os bancos de dados e serviços:

| Serviço / Ferramenta | Endereço / Porta | Finalidade na Validação |
| :--- | :--- | :--- |
| **API da Clínica (FastAPI)** | `http://localhost:8000` (`Swagger: /docs`) | Endpoints operacionais da clínica e fila de integrações |
| **API Governamental (FastAPI)** | `http://localhost:8001` (`Swagger: /docs`) | Recepção de vacinas antirrábicas, protocolos e modo falha |
| **Frontend Web** | `http://localhost:5173` | Interface do sistema integrada às APIs |
| **Bancos PostgreSQL** | Portas `5432` (Clínica) e `5433` (Governo) | Persistência relacional independente |
| **Postman (Collection Runner)** | Coleção v2.1 (`tests/postman/`) | Execução automatizada sequencial dos 16 testes |

---

## 3. Matriz de Execução dos 16 Testes Obrigatórios

| Caso | Cenário Testado | Requisições na Coleção | Requisitos / Regras | Resultado Obtido | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Teste 01** | Listagem e cadastro de veterinário ativo com hash de senha | `Teste 01a`, `Teste 01b` | RF01, RF02, RNF01 | Status `200`/`201`; senha oculta no retorno e situação `ativo` | **PASS** |
| **Teste 02** | Consulta individual de veterinário por ID | `Teste 02` | RF02 | Status `200 OK` com dados completos do profissional | **PASS** |
| **Teste 03** | Bloqueio de CPF e e-mail duplicados no cadastro de veterinário | `Teste 03` | RN01 | Requisição duplicada rejeitada (`400`/`409`/`422`) | **PASS** |
| **Teste 04** | Exclusão lógica (inativação) de veterinário | `Teste 04a`, `Teste 04b` | RF04, RN01 | Status `200 OK`; registro mantido com `situacao: "inativo"` | **PASS** |
| **Teste 05** | Cadastro de tutor vinculado a endereço e bloqueio de CPF duplicado | `Teste 05a`, `Teste 05b` | RF09, RN02 | Cadastro retorna `201 Created`; segundo cadastro com mesmo CPF bloqueado | **PASS** |
| **Teste 06** | Consulta ViaCEP válido (`01001000`), inexistente (`00000000`) e endereço | `Teste 06a`, `06b`, `06c` | RF10, RF11 | CEP válido retorna `UF: SP`; inexistente tratado sem erro `500` | **PASS** |
| **Teste 07** | Cadastro de animal e vínculo de microchip RFID único | `03a`, `Teste 07a`, `07b` | RF13, RF15, RF16, RF18 | Animal e microchip vinculados com status `201 Created` | **PASS** |
| **Teste 08** | Bloqueio de microchip RFID duplicado | `Teste 08` | RF17, RN05 | Tentativa de reuso do mesmo código bloqueada (`400`/`409`/`422`) | **PASS** |
| **Teste 09** | Registro de consulta clínica e consulta ao histórico do animal | `Teste 09a`, `Teste 09b` | RF21, RF22 | Consulta salva (`201`) e listada no histórico (`200 OK`) | **PASS** |
| **Teste 10** | Registro de vacina não antirrábica e histórico de próximas doses | `Teste 10 & 13`, `Teste 10b` | RF23, RF24 | Vacina registrada localmente (`201`) com data de reforço | **PASS** |
| **Teste 11** | Atualização cadastral do animal e consulta na API Governamental | `Teste 11b`, `Teste 11a` | RF15, RF25, RF33 | Dados atualizados na clínica e sincronizados no governo após vacina | **PASS** |
| **Teste 12** | Registro de vacina antirrábica e comunicação automática ao governo | `Teste 12a`, `Teste 12b` | RF23, RF26, RF27 | Integração gerada com status `enviada` e `protocolo_externo` válido | **PASS** |
| **Teste 13** | Isolamento de vacina comum (não comunica à API Governamental) | `Teste 10 & 13`, `12b & 13b` | RF32 | Vacina não antirrábica ausente da fila de integrações externas | **PASS** |
| **Teste 14** | Simulação de indisponibilidade do governo e enfileiramento local | `Teste 14a`, `14b`, `14c` | RF28, RF36, RN11, RN13 | Modo `INDISPONIVEL` ativado; vacina salva (`201`) e fila marcada como `pendente`/`falha` | **PASS** |
| **Teste 15** | Normalização do governo (`DESLIGADO`) e reenvio manual da pendência | `Teste 15a`, `Teste 15b` | RF29, RF36 | Reenvio executado com `200 OK`, alterando status para `enviada` com protocolo | **PASS** |
| **Teste 16** | Bloqueio de reenvio duplicado (idempotência) e auditoria no governo | `Teste 16a`, `16b`, `16c` | RF30, RF37, RN12 | Repetição não duplica registro; protocolo único confirmado na API Governamental | **PASS** |

---

## 4. Artefatos e Evidências

* **Coleção Postman:** `tests/postman/SDM.postman_collection.json`
* **Ambiente Postman:** `tests/postman/SDM.postman_environment.json`
* **Evidências de Execução (Prints):** Disponíveis na pasta `tests/postman/`, comprovando:
  * Execução completa no Postman Collection Runner com `0` falhas (`PASS` em todas as asserções);
  * Documentação Swagger/OpenAPI ativa em `http://localhost:8000/docs` (API Clínica) e `http://localhost:8001/docs` (API Governamental).
