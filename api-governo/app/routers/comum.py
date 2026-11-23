from fastapi import Response

from app.models import Operacao
from app.schemas import ErroResposta, ResultadoOperacao

ERROS = {
    404: {"model": ErroResposta, "description": "Não encontrado"},
    409: {"model": ErroResposta, "description": "Duplicidade ou chave reutilizada"},
    422: {"model": ErroResposta, "description": "Dados inválidos"},
    503: {"model": ErroResposta, "description": "Indisponível (falha simulada)"},
}


def resultado(op: Operacao, repetida: bool, response: Response) -> ResultadoOperacao:
    """Resposta padrão de escrita. Repetição: status 200 + cabeçalho Idempotent-Replayed."""
    if repetida:
        response.status_code = 200
        response.headers["Idempotent-Replayed"] = "true"
    texto = (op.mensagem or "").split("; microchip=")[0]
    return ResultadoOperacao(protocolo=op.protocolo, tipo=op.tipo, situacao=op.situacao,
                             mensagem=texto, data=op.data, reprocessada=repetida)
