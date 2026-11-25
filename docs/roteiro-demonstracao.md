# Roteiro de demonstração

## Antes de apresentar

1. Abra a versão combinada do front-end e das duas APIs. Confirme que `/health` das duas APIs devolve `banco: ok`.
2. Abra o front-end em modo API, o Swagger da clínica e o Swagger do governo simulado. Use as contas fictícias documentadas no README da revisão com autenticação.
3. Prepare um CPF fictício válido que ainda não esteja no banco, um código de microchip novo e os dados da aplicação. Confira se a API governamental está respondendo normalmente.

## Sequência

| Etapa | O que mostrar |
|---|---|
| Acesso | Mostre uma tentativa negada e entre com a veterinária ativa e confirmada. |
| Tutor e endereço | Consulte um CEP válido via ViaCEP. Complete o número, salve e abra o tutor cadastrado. |
| Animal e microchip | Cadastre o animal com espécie e raça compatíveis, vincule o chip e mostre o vínculo na ficha. |
| Consulta | Registre um atendimento e mostre o histórico na ficha. |
| Vacinação antirrábica | Ative a indisponibilidade simulada no Swagger do governo. Registre a antirrábica como aplicada e abra a comunicação em Integrações. |
| Recuperação | Mostre **Aplicada** na clínica e **Pendente** na comunicação. Desative a falha simulada e acione **Reenviar comunicação**. Se o reenvio automático já tiver confirmado, atualize a lista. |
| Confirmação | Mostre o protocolo do mesmo registro e confirme a operação no Swagger do governo. Explique como a mesma chave de idempotência evita duplicidade. Finalize com o logout. |

## Divisão das falas

- **P1** apresenta a arquitetura, a autenticação e a comunicação HTTP entre os serviços.
- **P2** apresenta o [diagrama e o modelo relacional](modelo-dados.md), com foco em chaves e restrições.
- **P3 e P4** explicam as rotas, o ViaCEP, os bancos separados, o modo de falha e o reenvio.
- **P5** conduz o fluxo na interface e mostra a diferença entre a aplicação da vacina e a confirmação governamental.
- **P6** apresenta o [relatório de testes](relatorio-testes.md) e as evidências dos casos obrigatórios.
