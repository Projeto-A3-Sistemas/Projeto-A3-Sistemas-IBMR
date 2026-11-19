"""API privada da clinica veterinaria (SDM).

Documentacao (Swagger): http://localhost:8000/docs

Para cada modulo novo, crie o router em app/routers/ e registre aqui com
app.include_router(...).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db.session import engine

app = FastAPI(
    title="SDM - API da Clinica",
    description="API privada do Sistema de Gestao de Clinica Veterinaria.",
    version="0.1.0",
)

# Libera o frontend (React/Vite) a chamar a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# ---- Rotas dos modulos (descomente quando cada parte estiver pronta) ----
# from app.routers import auth, tutores, animais, veterinarios, especies, racas
# app.include_router(auth.router)
# app.include_router(tutores.router)
# app.include_router(animais.router)
# app.include_router(veterinarios.router)
# app.include_router(especies.router)
# app.include_router(racas.router)
