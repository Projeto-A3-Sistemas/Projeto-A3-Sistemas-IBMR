# Tecnologias do projeto e por que foram escolhidas

O enunciado (seção 8) deixa a equipe escolher as tecnologias, desde que justifique as decisões
e cumpra os requisitos. Esta é a escolha da equipe, com o motivo de cada uma.

## Visão geral

| Camada | Tecnologia | Versão |
|---|---|---|
| Frontend | React + Vite | — |
| API privada da clínica | Python + FastAPI | Python 3.12, FastAPI 0.115 |
| API governamental simulada | Python + FastAPI (serviço separado) | idem |
| Banco de dados | PostgreSQL (um banco para cada API) | 18 |
| Acesso ao banco | SQLAlchemy 2 + psycopg 3 | 2.0 / 3.2 |
| Validação de dados | Pydantic 2 | 2.11 |
| Senhas | bcrypt | 4.3 |
| Login (token) | JWT com PyJWT | 2.10 |
| Chamadas HTTP entre serviços | httpx | 0.28 |
| Envio e reenvio ao governo | BackgroundTasks do FastAPI + thread em segundo plano | — |
| Documentação dos endpoints | Swagger/OpenAPI (gerado pelo FastAPI) | — |
| Testes | pytest (automáticos) e Postman (coleção) | — |
| Ambiente | Docker + Docker Compose | — |
| Versionamento | Git + GitHub (branches + pull requests) | — |
| Diagramas | Mermaid (desenhados pelo próprio GitHub) | — |

## Por que cada uma

**Python + FastAPI (as duas APIs).** A seção 8 sugere Python. O FastAPI gera o Swagger sozinho,
que é o entregável "Documentação dos endpoints" (seções 7 e 10). Ele também valida a entrada com
Pydantic, o que cobre a "validação dos dados no backend" (seção 7). As duas APIs usam a mesma
tecnologia, mas rodam como serviços separados, cada uma com seu banco, e só conversam por HTTP.
É isso que a seção 3.11 pede ("API independente", "persistência própria").

**PostgreSQL.** A seção 7 pede banco relacional. O modelo da seção 6 depende de chaves
estrangeiras e de regras de unicidade (CPF, e-mail, microchip, chave de idempotência), e o
PostgreSQL garante isso no próprio banco. Um exemplo é o índice "um microchip ativo por animal",
que faz o histórico de substituição (3.7) ficar certo mesmo se a API errar. São dois bancos:
`clinica_db` e `governo_db`, que é a separação exigida na 3.11.

**SQLAlchemy.** Mapeia as tabelas criadas pelos scripts SQL do P2 sem recriá-las. Os scripts em
`db/` são a fonte da verdade, e por isso não usamos Alembic: o entregável 6 pede "script de
criação e inicialização dos bancos", e os `.sql` já são isso.

**bcrypt.** A seção 3.1 pede "hash apropriado" e a seção 7 pede "armazenamento seguro de
credenciais". O bcrypt é feito para senha: é lento de propósito e usa um salt diferente em
cada senha. Senha nunca fica em texto puro (3.6).

**JWT (PyJWT).** O login devolve um token assinado que o frontend manda em toda requisição.
Assim a API não precisa guardar sessão. Para o "logout e encerramento da sessão" (3.1), o
identificador do token (`jti`) vai para a tabela `token_revogado` até expirar. O link de
confirmação de senha também é um token assinado, só que de outro tipo, e por isso não serve
para entrar no sistema.

**httpx.** É o cliente HTTP da API da clínica para falar com o ViaCEP e com a API do governo.
Ele tem timeout configurável, e a seção 7 pede "tratamento de erros HTTP, timeout e
indisponibilidade".

**Envio em segundo plano.** A regra 5 da seção 4 pede "novas tentativas automáticas ou manuais".
Logo depois de responder ao usuário, a API tenta o envio com as `BackgroundTasks` do próprio FastAPI,
e uma thread em segundo plano reenvia a cada 60 segundos o que ficou pendente. O reenvio manual é um
endpoint, e os três caminhos usam a mesma função, então a idempotência é a mesma em todos.

**React + Vite.** É o frontend web responsivo (seção 7), que conversa com a API da clínica só
por REST/JSON (seção 7: "comunicação entre frontend e backend por API REST").

**Docker Compose.** O enunciado não exige, mas facilita as "instruções para instalação e
execução" (entregável 10). Um comando (`docker compose up --build`) sobe os dois bancos e as
duas APIs, com os scripts SQL rodando sozinhos.

**Git + GitHub.** O controle de versão está na seção 8. Cada pessoa trabalha numa branch e
entra na `develop` por pull request revisado (ver `docs/fluxo-git.md`).

**Postman + pytest.** O Postman é a "coleção de testes das APIs" (entregável 8, responsabilidade
do P6). O pytest roda os testes automáticos de cada API sem precisar do Docker.

**Mermaid.** Os diagramas (arquitetura, fluxo da vacina, estados da integração) ficam escritos
dentro dos próprios `.md`, e o GitHub desenha. Assim eles ficam versionados junto com o código
(entregáveis 1 e 2).

## Portas

| Serviço | Porta |
|---|---|
| API da clínica | 8000 (Swagger em `/docs`) |
| API do governo | 8001 (Swagger em `/docs`) |
| Banco da clínica | 5432 |
| Banco do governo | 5433 |
| Frontend | 5173 |
