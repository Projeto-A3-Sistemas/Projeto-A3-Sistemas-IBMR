# SDM — Sistema de Gestão de Clínica Veterinária

Projeto Integrador A3 — Sistemas Distribuídos e Mobile (IBMR). Entrega: 26/11/2026.

Sistema web para clínica veterinária com três serviços que se comunicam por HTTP:

| Serviço | Pasta | Endereço |
|---|---|---|
| API privada da clínica (FastAPI) | `api-clinica/` | http://localhost:8000/docs |
| API governamental **simulada** (FastAPI) | `api-governo/` | http://localhost:8001/docs |
| Frontend web (React + Vite) | `frontend/` | http://localhost:5173 |

A API da clínica também consome a API pública **ViaCEP**. Todos os dados são fictícios, e a API
governamental é simulada (não é integração oficial).

Documentação: [arquitetura](docs/arquitetura.md) · [tecnologias](docs/tecnologias.md) ·
[contrato da integração](docs/contrato-integracao-governo.md) · [fluxo no Git](docs/fluxo-git.md)

## Como rodar (Docker)

Precisa do **Docker Desktop** aberto.

```bash
# 1. Criar o arquivo de configuração (só na primeira vez)
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/Mac

# 2. Subir bancos e APIs
docker compose up --build
```

Na primeira vez, os scripts de `db/clinica` e `db/governo` criam as tabelas e os dados de teste
sozinhos. Para recriar tudo do zero (apaga os dados): `docker compose down -v`.

Confira se subiu: http://localhost:8000/health e http://localhost:8001/health devem mostrar
`"banco": "ok"`.

> Já tem PostgreSQL instalado usando a porta 5432? No `.env`, troque `CLINICA_DB_PORT=5432`
> por `CLINICA_DB_PORT=5434`.


## Como abrir o frontend

Com as APIs no ar (passo acima), em outro terminal, na pasta do projeto:

```bash
cd frontend

# Usar a API de verdade (só na primeira vez)
# Windows (PowerShell):
Set-Content .env.local "VITE_CLINIC_MODE=api`nVITE_CLINIC_API_URL=http://localhost:8000"
# Linux/Mac:
# printf "VITE_CLINIC_MODE=api\nVITE_CLINIC_API_URL=http://localhost:8000\n" > .env.local

npm ci
npm run dev -- --strictPort
```

Abra http://localhost:5173 e entre com `ana@clinica.com` / `Senha@123`.
Precisa do **Node.js 24**. No PowerShell, se o `npm` for bloqueado, use `npm.cmd`.
Mais detalhes em [`frontend/README.md`](frontend/README.md).

## Como rodar sem Docker (VS Code)

1. Instale o PostgreSQL 17 ou 18. Crie dois bancos: `clinica_db` e `governo_db`.
2. Rode os scripts **em ordem**, cada um no seu banco (pgAdmin ou `psql`):
   - `clinica_db`: `db/clinica/01_criar_tabelas.sql`, `02_dados_teste.sql`, `03_sessoes.sql`, `04_senhas_teste.sql`
   - `governo_db`: `db/governo/01_schema.sql`, `02_dados_teste.sql`
3. Copie `.env.example` para `.env`. Como os dois bancos ficam no mesmo PostgreSQL, ajuste
   `GOVERNO_DATABASE_URL` para a porta `5432` e coloque a sua senha nas duas URLs.
4. Em dois terminais:

```bash
cd api-governo
python -m venv .venv && .venv\Scripts\activate      # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8001 --reload
```

```bash
cd api-clinica
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

## Login e uso no Swagger

Todas as rotas da API da clínica exigem login, menos `/health` e `/api/auth/...`.

1. Abra http://localhost:8000/docs.
2. `POST /api/auth/login` com `{"email": "ana@clinica.com", "senha": "Senha@123"}`.
3. Copie o `access_token`, clique em **Authorize** (cadeado) e cole.

Veterinários de teste (senha `Senha@123` para todos):

| E-mail | Situação | Resultado do login |
|---|---|---|
| `ana@clinica.com` | ativa, senha confirmada | entra |
| `carlos@clinica.com` | inativo | 403 (teste 2) |
| `beatriz@clinica.com` | senha não confirmada | 403 (teste 3) até confirmar |

Para confirmar a senha da Beatriz: `POST /api/auth/solicitar-confirmacao` (o "e-mail" é simulado
e o token volta na resposta) e depois `POST /api/auth/confirmar-senha` com esse token.

Frontend: mandar o cabeçalho `Authorization: Bearer <access_token>` em todas as chamadas.

## Testes

```bash
# testes automáticos, sem banco nem Docker
cd api-clinica
pip install -r requirements.txt pytest
python -m pytest -v
cd ../api-governo
python -m pytest -v
cd ..

# teste ponta a ponta (APIs no ar e banco recém-criado)
pip install httpx
python tests/integracao/teste_ponta_a_ponta.py
```

A coleção do Postman e as evidências ficam em `tests/postman/`.

## Estrutura

```
.
├── docker-compose.yml     # sobe bancos e APIs
├── .env.example           # modelo de configuração (copie para .env)
├── db/
│   ├── clinica/           # scripts do banco da clínica (rodam sozinhos no Docker)
│   └── governo/           # scripts do banco do governo
├── api-clinica/           # API privada (FastAPI)
│   ├── app/
│   │   ├── main.py        # ponto de entrada; registra as rotas e exige login
│   │   ├── deps.py        # checagem do login (protege as rotas)
│   │   ├── core/          # configurações, senha e tokens
│   │   ├── db/            # conexão com o banco (get_db)
│   │   ├── models/        # tabelas (SQLAlchemy)
│   │   ├── schemas/       # entrada/saída (Pydantic)
│   │   ├── routers/       # endpoints
│   │   └── services/      # regras de negócio, ViaCEP, envio ao governo e reenvio
│   └── tests/
├── api-governo/           # API governamental simulada (FastAPI)
├── frontend/              # interface web (React + Vite)
├── docs/                  # requisitos, diagramas, arquitetura
└── tests/
    ├── integracao/        # teste ponta a ponta
    └── postman/           # coleção do Postman
```

## Equipe

| Papel | Responsável |
|---|---|
| P1 — Arquitetura, segurança (login) e integração entre APIs | João |
| P2 — Banco de dados | Grazzie |
| P3 — Backend da API privada | Gabriel |
| P4 — API governamental e integrações | Kailanny |
| P5 — Frontend | João V |
| P6 — QA, testes e documentação | Lili |

## Como trabalhar no Git

- `main`: versão estável (entregas)
- `develop`: integração — **crie sua branch a partir dela**
- `feature/<sua-parte>`: sua branch (ex.: `feature/tutores`)

Detalhes e checklist de revisão em [docs/fluxo-git.md](docs/fluxo-git.md).
