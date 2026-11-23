# API Governamental SIMULADA (P4)

> Serviço **simulado** para fins acadêmicos. Não é integração oficial.

Sobe junto com o resto pelo `docker compose up --build` (porta **8001**, banco `db-governo`
na porta **5433**). Os scripts `db/governo/01_schema.sql` e `02_dados_teste.sql` rodam sozinhos
na primeira vez que o banco sobe. Swagger: http://localhost:8001/docs

## Endpoints

| Método | Endpoint | O que faz | Requisito |
|---|---|---|---|
| POST | `/api/governo/animais` | Cadastra animal | RF33 |
| GET | `/api/governo/animais/{microchip}` | Consulta por microchip | RF33 |
| PUT | `/api/governo/animais/{microchip}` | Atualiza animal | RF33 |
| POST | `/api/governo/vacinacoes-antirrabicas` | Recebe vacinação (cabeçalho `Idempotency-Key` obrigatório) | RF34, RF35 |
| GET | `/api/governo/operacoes/{protocolo}` | Consulta operação | RF37 |
| GET/POST | `/api/governo/admin/modo-falha` | Vê/liga falha simulada (cabeçalho `X-Admin-Token`) | RF36 |
| GET | `/health` | Saúde do serviço (nunca afetado pelo modo falha) | — |

## Contrato com a API da clínica

**Envio de vacinação** (`POST /api/governo/vacinacoes-antirrabicas`, cabeçalho `Idempotency-Key: VAC-{id da vacina}`):
```json
{
  "microchip": "985112345678999",
  "vacina": "Rabisin",
  "fabricante": "Boehringer",
  "lote": "L2026C",
  "data_aplicacao": "2026-11-19",
  "veterinario_nome": "Ana Lima",
  "veterinario_crmv": "12345",
  "veterinario_crmv_uf": "RJ",
  "animal": {
    "nome": "Rex", "especie": "Cão", "raca": "Labrador", "sexo": "M",
    "data_nascimento": "2020-03-15", "tutor_nome": "Maria Silva", "tutor_cpf": "12345678901"
  }
}
```
O bloco `animal` é opcional, mas **recomendado enviar sempre**: se o animal ainda não estiver
registrado no governo, ele é cadastrado junto com a vacinação (enunciado, seção 4, regra 2:
a comunicação vale "independentemente de o animal já estar cadastrado"). Sem o bloco, e com
o animal ainda não registrado, a resposta é 422 `ANIMAL_NAO_CADASTRADO`.
Na clínica esses campos vêm de: `vinculo_microchip.codigo_microchip` (ativo), `vacina.nome_vacina`,
`vacina.fabricante`, `vacina.numero_lote`, `vacina.data_aplicacao`, `veterinario.nome_completo`,
`veterinario.crmv_numero`, `veterinario.crmv_uf`; no bloco `animal`: `animal.nome`, `especie.nome`,
`raca.nome` (ou null), `animal.sexo`, `animal.data_nascimento`, `tutor.nome_completo`, `tutor.cpf`.

**Cadastro de animal** (`POST /api/governo/animais`): `microchip`, `nome`, `especie` (nome da espécie),
`raca` (nome ou null), `sexo`, `data_nascimento`, `tutor_nome`, `tutor_cpf`.

**Resposta de sucesso** (201 na primeira vez; 200 + cabeçalho `Idempotent-Replayed: true` na repetição):
```json
{
  "protocolo": "GOV-2026-0005",
  "tipo": "VACINA_ANTIRRABICA",
  "situacao": "PROCESSADA",
  "mensagem": "Vacinação antirrábica registrada",
  "data": "2026-11-21T15:00:00",
  "reprocessada": false,
  "aviso": "Serviço governamental SIMULADO para fins acadêmicos — não é integração oficial."
}
```

**Erro**: `{"codigo": "...", "mensagem": "...", "protocolo": "GOV-... ou null", "aviso": "..."}`

| Status | Código | O que a clínica faz (seção 7.4 dos requisitos) |
|---|---|---|
| 201 / 200 | — | `confirmada`, grava `protocolo_externo` |
| 422 | `DADOS_INVALIDOS`, `ANIMAL_NAO_CADASTRADO`, `DATA_APLICACAO_INVALIDA` | `falha` (corrigir e reenviar) |
| 404 | `ANIMAL_NAO_ENCONTRADO` | `falha` |
| 409 | `MICROCHIP_JA_CADASTRADO`, `CHAVE_IDEMPOTENCIA_REUTILIZADA` | `falha` |
| 503 / 5xx / timeout | `SERVICO_INDISPONIVEL` | continua `pendente` |

## Idempotência (sem colunas extras: banco igual ao diagrama do M1)
- `vacinacao_antirrabica.chave_idempotencia` é UNIQUE: a mesma vacinação nunca entra duas vezes.
- Cada operação guarda no fim da `mensagem` o microchip e a chave
  (`...; microchip=985...; chave=VAC-1`). É assim que a repetição encontra o protocolo original.
- Mesma chave e mesmo conteúdo: devolve o mesmo protocolo. Conteúdo diferente: 409.
- Requisição rejeitada não "gasta" a chave: corrigido o dado, a clínica reenvia com a mesma.
- Protocolo sequencial `GOV-AAAA-NNNN`, no mesmo padrão dos dados de teste da clínica.

## Modo falha (testes 14 a 16)
Atende o item da seção 3.11 "simular erros de validação e indisponibilidade".
Token padrão: `admin-sdm` (pode ser trocado pela variável `GOVERNO_ADMIN_TOKEN`).
No Swagger, abra `POST /api/governo/admin/modo-falha`, preencha `X-Admin-Token` e envie:

| Corpo | Efeito |
|---|---|
| `{"tipo": "INDISPONIVEL"}` | todas as rotas respondem 503 (teste 14) |
| `{"tipo": "ERRO_VALIDACAO"}` | respondem 422: a clínica marca a integração como `falha` |
| `{"tipo": "LENTO", "atraso_segundos": 10}` | esperam 10 s e depois processam: a clínica desiste no timeout de 5 s, o governo grava, e o reenvio devolve o mesmo protocolo (teste 16) |
| `{"tipo": "DESLIGADO"}` | volta ao normal (teste 15) |

## Testes automatizados
```bash
cd api-governo
pip install -r requirements.txt pytest
python -m pytest -v        # usa SQLite em memória, não precisa do Docker
```
