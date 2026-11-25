# Relatório de testes do A3

Validação realizada em **25/11/2026** com dados fictícios. O front-end do P5 foi executado em React/Vite, com FastAPI e dois bancos PostgreSQL em containers isolados. O back-end correspondeu ao commit `75a53c3` do [PR #4](https://github.com/Projeto-A3-Sistemas/Projeto-A3-Sistemas-IBMR/pull/4), que inclui as rotas de integração do PR #3.

## Resultados

| Verificação | Resultado |
|---|---|
| Suíte automatizada da API da clínica | 30 testes aprovados |
| Suíte automatizada da API governamental simulada | 20 testes aprovados |
| Roteiro ponta a ponta `tests/integracao/teste_ponta_a_ponta.py` do PR #4 | 37 verificações aprovadas, 0 falhas |
| Front-end em modo API | Login, sessão após recarregar, logout, cadastro e primeiro acesso de veterinário, fluxos clínicos e tela de integrações verificados no Chrome |
| Front-end em modo demonstração | Acesso e saída com dados locais, sem chamadas de API |
| Layout | Navegação nas seis áreas em 1440, 390 e 320 px no Chrome |
| Compilação e lint | `npm run build` aprovado e `npm run lint` sem avisos |

## Cenários obrigatórios do enunciado

| Nº | Cenário | Resultado observado |
|---|---|---|
| 1–4 | Login válido, profissional inativo, senha pendente e senha incorreta | Sessão aberta para a conta válida. Contas inativas ou pendentes bloqueadas com HTTP 403. Senha incorreta rejeitada com HTTP 401. |
| 5 | Cadastrar tutor e repetir CPF | Primeiro cadastro aceito. CPF repetido rejeitado com HTTP 409. |
| 6 | CEP válido e inexistente | Endereço devolvido pelo ViaCEP. CEP inexistente rejeitado com HTTP 404. |
| 7–8 | Cadastrar animal, vincular chip e repetir código | Cadastro e vínculo aceitos. Código repetido rejeitado com HTTP 409. |
| 9 | Registrar e consultar atendimento | Atendimento visível no histórico do animal. |
| 10 | Registrar vacina e consultar próxima dose | Aplicação persistida e data da próxima dose disponível. |
| 11 | Cadastrar e atualizar animal no governo simulado | Cadastro confirmado e atualização recebida pelo serviço simulado. |
| 12–13 | Aplicar antirrábica e vacina comum | Antirrábica confirmada com protocolo. Vacina comum sem comunicação obrigatória. |
| 14–15 | Indisponibilidade e recuperação | Vacina permaneceu aplicada na clínica. Comunicação ficou pendente e foi confirmada após recuperação. Reenvio manual também verificado no navegador em cenário isolado. |
| 16 | Repetição após timeout | Operação original confirmada com a mesma chave de idempotência e sem duplicar a aplicação no governo simulado. |

Também foram verificados o bloqueio das rotas privadas sem token, a confirmação simulada da senha, a revogação do token após logout, a substituição do chip com histórico e a exclusão de agendamentos cancelados da lista de próximas doses.

## Reprodução

1. Inicie as duas APIs com os scripts de banco da revisão de autenticação. Confira os endpoints de saúde.
2. Siga as instruções de testes do [README da raiz](../README.md) da revisão que inclui o PR #4. O roteiro ponta a ponta precisa de um banco novo de teste e acesso ao ViaCEP.
3. Suba o [front-end em modo API](../frontend/README.md#modo-api) e siga o [roteiro de demonstração](roteiro-demonstracao.md).

Os resultados acima são da combinação testada em ambiente isolado. A versão integrada que será entregue deve passar pela mesma conferência após os merges.
