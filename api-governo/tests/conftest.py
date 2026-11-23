"""Testes da API do governo sem Postgres: usam SQLite em memória no lugar do get_db.
Rodar na pasta api-governo:  pip install pytest  e depois  python -m pytest -v
"""
import os

os.environ["GOVERNO_DATABASE_URL"] = "sqlite://"
os.environ["GOVERNO_ADMIN_TOKEN"] = "token-teste"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401  (registra as tabelas no Base)
from app.db.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.services import modo_falha  # noqa: E402

engine_teste = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessaoTeste = sessionmaker(bind=engine_teste, autoflush=False, expire_on_commit=False)


def _get_db_teste():
    db = SessaoTeste()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine_teste)
    Base.metadata.create_all(bind=engine_teste)
    modo_falha.definir("DESLIGADO", 0)
    app.dependency_overrides[get_db] = _get_db_teste
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sessao():
    with SessaoTeste() as db:
        yield db


ANIMAL = {
    "microchip": "985112345678903",
    "nome": "Thor",
    "especie": "Cão",
    "raca": None,
    "sexo": "M",
    "data_nascimento": "2021-10-10",
    "tutor_nome": "João Souza",
    "tutor_cpf": "987.654.321-00",
}

VACINA = {
    "microchip": "985112345678903",
    "vacina": "Rabisin",
    "fabricante": "Boehringer",
    "lote": "L2026C",
    "data_aplicacao": "2026-11-19",
    "veterinario_nome": "Ana Lima",
    "veterinario_crmv": "12345",
    "veterinario_crmv_uf": "RJ",
}
