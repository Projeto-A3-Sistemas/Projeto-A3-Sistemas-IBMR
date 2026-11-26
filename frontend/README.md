# Front-end da clínica veterinária

Interface web do SDM em React e Vite. Use Node.js 24, a versão usada nos testes da equipe.

## Modo demonstração

Na raiz do repositório, rode:

```bash
cd frontend
npm ci
npm run dev
```

Abra [http://localhost:5173](http://localhost:5173) e clique em **Entrar na demonstração**. Os dados fictícios desse modo ficam no navegador. O Docker é necessário apenas para o modo API.

## Modo API

Use a revisão do back-end que contém a autenticação do PR #4. Na raiz do projeto, crie `.env` a partir de `.env.example` se ainda precisar da configuração local e rode `docker compose up -d --build`. Confira se [a API da clínica](http://localhost:8000/health) e [a API governamental simulada](http://localhost:8001/health) retornam `"banco":"ok"`.

Em outro terminal, entre em `frontend` e crie o arquivo `.env.local` com:

```dotenv
VITE_CLINIC_MODE=api
VITE_CLINIC_API_URL=http://localhost:8000
```

Execute `npm ci` e `npm run dev -- --strictPort`. Se o Vite já estava aberto, reinicie-o para ler a configuração. Use a porta 5173, que a API da clínica libera no CORS. As contas fictícias de teste e as rotas estão documentadas no [README da raiz](../README.md) da revisão com autenticação.

Para voltar à demonstração, retire a configuração de modo API do `.env.local` e reinicie o Vite. No PowerShell, se a política de execução bloquear `npm`, use `npm.cmd`.

### Banco da clínica com volume existente

Um volume novo executa os scripts de inicialização automaticamente. Se o volume já existia antes da autenticação, aplique `db/clinica/03_sessoes.sql` para criar a tabela de revogação. Use `04_senhas_teste.sql` apenas em ambiente de teste para atualizar o hash das contas fictícias fornecidas pelo projeto.

No PowerShell, execute na raiz do projeto:

```powershell
Get-Content -Raw db/clinica/03_sessoes.sql | docker compose exec -T db-clinica sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## Verificações

```bash
npm run lint
npm run build
```

- [Modelo de dados](../docs/modelo-dados.md)
- [Relatório de testes](../docs/relatorio-testes.md)
- [Roteiro de demonstração](../docs/roteiro-demonstracao.md)
