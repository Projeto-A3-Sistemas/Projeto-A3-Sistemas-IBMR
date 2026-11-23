"""API privada da clinica veterinaria (SDM).

Documentacao (Swagger): http://localhost:8000/docs

Para cada modulo novo, crie o router em app/routers/ e registre aqui com
app.include_router(...).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db.session import engine
from app.services.reenvio import ciclo_de_vida

app = FastAPI(
    title="SDM - API da Clinica",
    description="API privada do Sistema de Gestao de Clinica Veterinaria.",
    version="0.1.0",
    lifespan=ciclo_de_vida,
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


# ---- Rotas dos modulos ----
from app.routers import animais, consultas, tutores, vacinas, veterinarios  # noqa: E402

app.include_router(tutores.router)
app.include_router(animais.router)
app.include_router(veterinarios.router)
app.include_router(consultas.router)
app.include_router(vacinas.router)

# P3 - microchip e integração com o governo (Milestone 4)
from app.routers import integracoes, microchips  # noqa: E402

app.include_router(microchips.router)
app.include_router(integracoes.router)

# P4 - especies, racas, enderecos e CEP
from app.routers import cep, enderecos, especies, racas  # noqa: E402

app.include_router(especies.router)
app.include_router(racas.router)
app.include_router(enderecos.router)
app.include_router(cep.router)

# Descomente quando o login estiver pronto:
# from app.routers import auth
# app.include_router(auth.router)
