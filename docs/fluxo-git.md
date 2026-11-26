# Fluxo de trabalho no Git

## Branches

| Branch | Para quê | Quem mexe |
|---|---|---|
| `main` | Versão estável, a que é entregue e apresentada | Só recebe merge da `develop` na entrega |
| `develop` | Integração: junta as partes de todo mundo | Só por pull request |
| `feature/<parte>` | Trabalho de cada pessoa (ex.: `feature/p3-crud`) | A própria pessoa |

Ninguém faz commit direto na `develop` nem na `main`.

## Passo a passo

```bash
git checkout develop
git pull                                # sempre partir da develop atualizada
git checkout -b feature/sua-parte
# ...trabalhe...
git add .
git commit -m "feat(pX): o que foi feito"
git push -u origin feature/sua-parte
```

Depois abra o **Pull Request para `develop`** e marque um revisor.

Se a `develop` mudar enquanto você trabalha:

```bash
git checkout develop && git pull
git checkout feature/sua-parte
git merge develop                       # resolve conflitos aqui, na sua branch
```

## Mensagens de commit

`tipo(parte): descrição`, por exemplo `feat(p1): login e logout` ou `fix(p3): CPF duplicado`.
Tipos: `feat` (novo), `fix` (correção), `docs` (documentação), `test` (testes).

## Revisão de pull request (checklist do P1)

Antes de aprovar:

- [ ] A branch parte da `develop` atual e não tem conflito.
- [ ] A API sobe (`docker compose up --build`) e o `/health` mostra `"banco": "ok"`.
- [ ] Os testes automáticos passam (`python -m pytest` em `api-clinica/` e `api-governo/`).
- [ ] Não cria um segundo model para uma tabela que já tem model (a API não sobe).
- [ ] Não altera as tabelas de `db/clinica/01_criar_tabelas.sql` sem combinar com o P2.
- [ ] Rotas novas são registradas no `main.py` junto das outras, e são protegidas por login
      (menos login e confirmação de senha).
- [ ] Não tem senha, token ou `.env` no commit.
- [ ] Mensagens de erro claras (404, 409, 422) em vez de erro 500.
