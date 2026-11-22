"""Simulação de falhas (RF36), ligada/desligada por POST /api/governo/admin/modo-falha.

O estado fica em memória: reiniciar o container volta ao modo normal.
"""
import asyncio
import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.schemas import AVISO

log = logging.getLogger("governo.modo_falha")

_estado = {"tipo": "DESLIGADO", "atraso_segundos": 10.0}

ROTAS_ISENTAS = ("/api/governo/admin", "/health", "/docs", "/openapi.json", "/redoc")


def obter() -> dict:
    return {**_estado, "ativo": _estado["tipo"] != "DESLIGADO"}


def definir(tipo: str, atraso_segundos: float) -> dict:
    _estado["tipo"] = tipo
    _estado["atraso_segundos"] = atraso_segundos
    log.warning("Modo falha alterado para %s (atraso=%ss)", tipo, atraso_segundos)
    return obter()


async def middleware_modo_falha(request: Request, call_next):
    caminho = request.url.path
    tipo = _estado["tipo"]

    if tipo == "DESLIGADO" or caminho.startswith(ROTAS_ISENTAS):
        return await call_next(request)

    if tipo == "INDISPONIVEL":
        log.warning("Falha simulada 503 em %s %s", request.method, caminho)
        return JSONResponse(
            status_code=503,
            content={"codigo": "SERVICO_INDISPONIVEL",
                     "mensagem": "Serviço temporariamente indisponível (falha simulada).",
                     "protocolo": None, "aviso": AVISO},
            headers={"Retry-After": "60"},
        )

    if tipo == "ERRO_VALIDACAO":
        log.warning("Erro de validação simulado em %s %s", request.method, caminho)
        return JSONResponse(
            status_code=422,
            content={"codigo": "DADOS_INVALIDOS",
                     "mensagem": "Dados recusados pela validação do governo (erro simulado).",
                     "protocolo": None, "aviso": AVISO},
        )

    # LENTO: atrasa e DEPOIS processa normalmente. Se o cliente desistir por
    # timeout, a operação pode ter sido gravada mesmo assim — é exatamente o
    # cenário em que a chave de idempotência evita duplicidade no reenvio.
    log.warning("Atraso simulado de %ss em %s %s", _estado["atraso_segundos"], request.method, caminho)
    await asyncio.sleep(_estado["atraso_segundos"])
    return await call_next(request)
