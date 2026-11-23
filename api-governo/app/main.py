"""API governamental SIMULADA (SDM).

Documentacao (Swagger): http://localhost:8001/docs

Servico independente, com banco proprio (db-governo). Nao e uma integracao
oficial com sistemas do governo.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.session import engine
from app.schemas import AVISO
from app.services import modo_falha
from app.services.operacoes import ErroGoverno

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

app = FastAPI(
    title="SDM - API Governamental Simulada",
    description=(
        "**Serviço simulado para fins acadêmicos — não é integração oficial.**\n\n"
        "Registro de animais com microchip e de vacinação antirrábica, com protocolo, "
        "idempotência (`Idempotency-Key`) e simulação de falhas."
    ),
    version="1.0.0",
)

# Falha simulada (RF36): liga/desliga em POST /api/governo/admin/modo-falha
app.middleware("http")(modo_falha.middleware_modo_falha)


@app.exception_handler(ErroGoverno)
async def erro_governo(_: Request, erro: ErroGoverno):
    return JSONResponse(status_code=erro.status,
                        content={"codigo": erro.codigo, "mensagem": erro.mensagem,
                                 "protocolo": erro.protocolo, "aviso": AVISO})


@app.exception_handler(RequestValidationError)
async def dados_invalidos(_: Request, erro: RequestValidationError):
    detalhes = "; ".join(
        f"{'.'.join(str(p) for p in e['loc'][1:]) or e['loc'][0]}: {e['msg']}" for e in erro.errors()
    )
    return JSONResponse(status_code=422,
                        content={"codigo": "DADOS_INVALIDOS", "mensagem": detalhes,
                                 "protocolo": None, "aviso": AVISO})


@app.get("/health", tags=["Status"])
def health():
    """Confere se a API esta no ar e se consegue falar com o banco."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        banco = "ok"
    except Exception:
        banco = "indisponivel"
    return {"api": "ok", "banco": banco}


# ---- Rotas ----
from app.routers import admin, animais, operacoes, vacinacoes  # noqa: E402

app.include_router(animais.router)
app.include_router(vacinacoes.router)
app.include_router(operacoes.router)
app.include_router(admin.router)
