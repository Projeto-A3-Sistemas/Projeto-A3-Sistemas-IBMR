"""Configuracoes da API do governo.

Le as variaveis do arquivo .env (na raiz do projeto) quando a API roda pelo
VS Code. Dentro do Docker, as variaveis vem do docker-compose.yml.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ_PROJETO = Path(__file__).resolve().parents[3]
load_dotenv(RAIZ_PROJETO / ".env")

DATABASE_URL = os.getenv(
    "GOVERNO_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/governo_db",
)
