"""Configuracoes da API da clinica.

Le as variaveis do arquivo .env (na raiz do projeto) quando a API roda pelo
VS Code. Dentro do Docker, as variaveis vem do docker-compose.yml.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ_PROJETO = Path(__file__).resolve().parents[3]
load_dotenv(RAIZ_PROJETO / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/clinica_db",
)
JWT_SECRET = os.getenv("JWT_SECRET", "troque-esta-chave")
GOVERNO_API_URL = os.getenv("GOVERNO_API_URL", "http://localhost:8001")

# Integração com a API governamental (Milestone 4)
GOVERNO_TIMEOUT_SEGUNDOS = float(os.getenv("GOVERNO_TIMEOUT_SEGUNDOS", "5"))
# De quanto em quanto tempo as comunicações pendentes são reenviadas (0 = desliga)
INTEGRACAO_INTERVALO_SEGUNDOS = int(os.getenv("INTEGRACAO_INTERVALO_SEGUNDOS", "60"))
