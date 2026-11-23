"""Liga/desliga a falha simulada para a demonstração (P4 - RF36)."""
import os
import secrets

from fastapi import APIRouter, Header, HTTPException

from app.schemas import ModoFalha, ModoFalhaResposta
from app.services import modo_falha

router = APIRouter(prefix="/api/governo/admin", tags=["Administração (demonstração)"])

# Pode ser trocado pela variável GOVERNO_ADMIN_TOKEN no .env / docker-compose.
TOKEN = os.getenv("GOVERNO_ADMIN_TOKEN", "admin-sdm")


def _conferir(token: str) -> None:
    if not secrets.compare_digest(token, TOKEN):
        raise HTTPException(401, "X-Admin-Token inválido.")


@router.get("/modo-falha", response_model=ModoFalhaResposta)
def ver(x_admin_token: str = Header(alias="X-Admin-Token")):
    _conferir(x_admin_token)
    return modo_falha.obter()


@router.post("/modo-falha", response_model=ModoFalhaResposta)
def definir(cfg: ModoFalha, x_admin_token: str = Header(alias="X-Admin-Token")):
    """`DESLIGADO`, `INDISPONIVEL` (responde 503), `ERRO_VALIDACAO` (422) ou `LENTO`
    (espera `atraso_segundos` e depois processa, provocando timeout na clínica)."""
    _conferir(x_admin_token)
    return modo_falha.definir(cfg.tipo, cfg.atraso_segundos)
