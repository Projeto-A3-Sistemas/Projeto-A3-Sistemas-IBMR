"""Conexao com o banco da clinica.

Uso em qualquer rota:

    from fastapi import Depends
    from sqlalchemy.orm import Session
    from app.db.session import get_db

    @router.get("/tutores")
    def listar(db: Session = Depends(get_db)):
        ...
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base dos models (tabelas) da clinica."""


def get_db() -> Generator[Session, None, None]:
    """Abre uma sessao com o banco por requisicao e fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
