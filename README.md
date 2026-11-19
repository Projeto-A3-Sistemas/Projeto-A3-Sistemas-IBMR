# SDM — Sistema de Gestão de Clínica Veterinária

Projeto Integrador A3 — Sistemas Distribuídos e Mobile (IBMR).

Sistema web para clínica veterinária com três serviços que se comunicam por HTTP:

| Serviço | Pasta | Endereço |
|---|---|---|
| API privada da clínica (FastAPI) | `api-clinica/` | http://localhost:8000/docs |
| API governamental **simulada** (FastAPI) | `api-governo/` | http://localhost:8001/docs |
| Frontend web (React + Vite) | `frontend/` | http://localhost:5173 |

A API privada também consome a API pública **ViaCEP**. Todos os dados são fictícios
e a API governamental é simulada (não é integração oficial).

## Como rodar

Precisa ter o **Docker Desktop** aberto.

```bash
# 1. Criar o arquivo de configuração (só na primeira vez)
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/Mac

# 2. Subir bancos e APIs
docker compose up --build
```

Depois abra http://localhost:8000/docs (Swagger da API da clínica) e
http://localhost:8000/health (deve mostrar `"banco": "ok"`).

> Já tem PostgreSQL instalado no PC usando a porta 5432? No `.env`, troque
> `CLINICA_DB_PORT=5432` por `CLINICA_DB_PORT=5434`.

Para recriar o banco do zero (apaga os dados): `docker compose down -v`

## Estrutura

```
.
├── docker-compose.yml     # sobe bancos e APIs
├── .env.example           # modelo de configuração (copie para .env)
├── db/
│   ├── clinica/           # scripts do banco da clínica (rodam sozinhos no Docker)
│   └── governo/           # scripts do banco do governo
├── api-clinica/           # API privada (FastAPI)
│   └── app/
│       ├── main.py        # ponto de entrada; registre aqui os routers
│       ├── core/          # configurações
│       ├── db/            # conexão com o banco (get_db)
│       ├── models/        # tabelas (SQLAlchemy)
│       ├── schemas/       # entrada/saída (Pydantic)
│       ├── routers/       # endpoints
│       └── services/      # regras de negócio
├── api-governo/           # API governamental simulada (FastAPI)
├── frontend/              # interface web (React + Vite)
├── docs/                  # requisitos, diagramas, arquitetura
└── tests/postman/         # coleção de testes do Postman
```

## Equipe

| Papel | Responsável |
|---|---|
| P1 — Arquitetura, segurança (login) e integração entre APIs | |
| P2 — Banco de dados | Grazzie |
| P3 — Backend da API privada | Gabriel |
| P4 — API governamental e integrações | |
| P5 — Frontend | |
| P6 — QA, testes e documentação | |

## Como trabalhar no Git

- `main`: versão estável (entregas)
- `develop`: integração — **crie sua branch a partir dela**
- `feature/<sua-parte>`: sua branch (ex.: `feature/tutores`)

```bash
git checkout develop
git pull
git checkout -b feature/sua-parte
# ...trabalhe...
git add .
git commit -m "feat: descricao do que fez"
git push -u origin feature/sua-parte
```

Depois abra um **Pull Request para `develop`** no GitHub.
