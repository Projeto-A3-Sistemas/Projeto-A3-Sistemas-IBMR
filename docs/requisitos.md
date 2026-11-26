# Requisitos do sistema

O Projeto A3 de Sistemas Distribuídos e Mobile reúne uma interface para a clínica veterinária, uma API privada e uma API governamental simulada. O veterinário opera pela interface, que chama a API da clínica. A clínica consulta o ViaCEP e comunica eventos obrigatórios ao serviço governamental por HTTP.

| Área | Requisito |
|---|---|
| Acesso | Autenticar somente veterinários ativos e com senha confirmada. Usar hash para a senha, confirmação com envio simulado, identificação da sessão e revogação no logout. Proteger as rotas clínicas. |
| Tutores | Cadastrar, consultar, atualizar e inativar. Validar a unicidade do CPF e associar um endereço. |
| Endereços | Buscar CEP no ViaCEP para preencher o endereço. Aceitar complemento, número e preenchimento manual quando a consulta não trouxer os dados. |
| Espécies e raças | Manter os catálogos pela API e mostrar no cadastro somente raças compatíveis com a espécie. Permitir raça indefinida. |
| Veterinários | Cadastrar e manter os dados do profissional, com CPF, CRMV, e-mail, telefone, situação e confirmação da senha. |
| Animais | Cadastrar e atualizar a ficha, com tutor, espécie, identificação e informações clínicas. Permitir consultar a situação de integração. |
| Microchip | Vincular um código RFID único ao animal, registrar o responsável e a data e preservar os vínculos anteriores na substituição. |
| Consultas | Registrar data, motivo, dados do atendimento, situação e responsável. Mostrar o histórico por animal. |
| Vacinas | Registrar classificação, fabricante, lote, validade, dose, via, situação e aplicação. Mostrar o histórico e a previsão da próxima dose. |
| Governo simulado | Cadastrar, consultar e atualizar animais por microchip e receber aplicações antirrábicas com protocolo. Manter banco separado da clínica. |
| Comunicação obrigatória | Na aplicação de uma antirrábica, gravar a vacinação na clínica e registrar a comunicação, inclusive quando o animal ainda não existe no serviço simulado. Uma vacina comum não gera essa comunicação obrigatória. |
| Falha e reenvio | Manter a aplicação local quando o governo estiver indisponível. Mostrar pendência, tentativas e protocolo. Reenviar com a mesma chave para impedir duplicidade. |

## Requisitos de qualidade

- Interface responsiva e validação dos formulários no navegador e na API.
- Persistência relacional e comunicação REST com tratamento de erro, timeout e indisponibilidade.
- Credenciais protegidas, rastreabilidade das comunicações e dados fictícios na demonstração.
- Código organizado, documentação das rotas e evidências dos testes dos cenários obrigatórios.

Consulte o [modelo de dados](modelo-dados.md), o [relatório de testes](relatorio-testes.md) e o [roteiro de demonstração](roteiro-demonstracao.md). O diagrama da arquitetura e o contrato entre os serviços ficam na documentação do [PR #4](https://github.com/Projeto-A3-Sistemas/Projeto-A3-Sistemas-IBMR/pull/4).
