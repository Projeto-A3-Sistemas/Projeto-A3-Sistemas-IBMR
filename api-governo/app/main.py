"""API governamental SIMULADA (SDM).

Documentacao (Swagger): http://localhost:8001/docs

Servico independente, com banco proprio (db-governo). Nao e uma integracao
oficial com sistemas do governo.
"""
from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine

app = FastAPI(
    title="SDM - API Governamental Simulada",
    description="Simula o registro de animais com microchip e de vacinacao antirrabica.",
    version="0.1.0",
)


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


# ---- Rotas (descomente quando estiverem prontas) ----
# from app.routers import animais, vacinacoes, operacoes
# app.include_router(animais.router)
# app.include_router(vacinacoes.router)
# app.include_router(operacoes.router)
