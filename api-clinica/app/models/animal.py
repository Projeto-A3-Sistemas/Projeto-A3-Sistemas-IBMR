from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.especie import Especie
from app.models.raca import Raca
from app.models.tutor import Tutor


class Animal(Base):
    __tablename__ = "animal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    data_nascimento: Mapped[date | None] = mapped_column(Date)
    idade_estimada_meses: Mapped[int | None] = mapped_column(Integer)
    sexo: Mapped[str] = mapped_column(String(1))
    cor: Mapped[str | None] = mapped_column(String(50))
    peso_atual: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutor.id"))
    especie_id: Mapped[int] = mapped_column(ForeignKey("especie.id"))
    raca_id: Mapped[int | None] = mapped_column(ForeignKey("raca.id"))
    situacao: Mapped[str] = mapped_column(String(10), server_default="ativo")
    data_cadastro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tutor: Mapped[Tutor] = relationship(lazy="joined")
    especie: Mapped[Especie] = relationship(lazy="joined")
    raca: Mapped[Raca | None] = relationship(lazy="joined")
