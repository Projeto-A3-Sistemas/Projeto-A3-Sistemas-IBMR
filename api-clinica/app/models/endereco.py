from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Endereco(Base):
    __tablename__ = "endereco"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cep: Mapped[str] = mapped_column(String(8))
    logradouro: Mapped[str] = mapped_column(String(150))
    numero: Mapped[str] = mapped_column(String(10))
    complemento: Mapped[str | None] = mapped_column(String(80))
    bairro: Mapped[str] = mapped_column(String(80))
    cidade: Mapped[str] = mapped_column(String(80))
    uf: Mapped[str] = mapped_column(String(2))
    codigo_ibge: Mapped[str | None] = mapped_column(String(7))
