from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.endereco import Endereco


class Tutor(Base):
    __tablename__ = "tutor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_completo: Mapped[str] = mapped_column(String(150))
    cpf: Mapped[str] = mapped_column(String(11), unique=True)
    data_nascimento: Mapped[date] = mapped_column(Date)
    email: Mapped[str] = mapped_column(String(120))
    telefone: Mapped[str] = mapped_column(String(20))
    endereco_id: Mapped[int] = mapped_column(ForeignKey("endereco.id"))
    data_cadastro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    situacao: Mapped[str] = mapped_column(String(10), server_default="ativo")

    endereco: Mapped[Endereco] = relationship(lazy="joined")
