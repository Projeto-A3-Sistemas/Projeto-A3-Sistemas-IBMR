from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.animal import Animal
from app.models.veterinario import Veterinario


class Vacina(Base):
    __tablename__ = "vacina"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animal.id"))
    veterinario_id: Mapped[int] = mapped_column(ForeignKey("veterinario.id"))
    nome_vacina: Mapped[str] = mapped_column(String(100))
    tipo_vacina: Mapped[str] = mapped_column(String(50))
    antirrabica: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    fabricante: Mapped[str] = mapped_column(String(100))
    numero_lote: Mapped[str] = mapped_column(String(50))
    data_aplicacao: Mapped[date | None] = mapped_column(Date)
    dose: Mapped[str] = mapped_column(String(30))
    via_aplicacao: Mapped[str | None] = mapped_column(String(30))
    data_proxima_dose: Mapped[date | None] = mapped_column(Date)
    validade_lote: Mapped[date] = mapped_column(Date)
    observacoes: Mapped[str | None] = mapped_column(Text)
    situacao: Mapped[str] = mapped_column(String(10), server_default="agendada")

    animal: Mapped[Animal] = relationship(lazy="joined")
    veterinario: Mapped[Veterinario] = relationship(lazy="joined")
