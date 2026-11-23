from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.animal import Animal
from app.models.veterinario import Veterinario


class Consulta(Base):
    __tablename__ = "consulta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animal.id"))
    veterinario_id: Mapped[int] = mapped_column(ForeignKey("veterinario.id"))
    data_hora: Mapped[datetime] = mapped_column(DateTime)
    motivo: Mapped[str] = mapped_column(String(200))
    anamnese: Mapped[str | None] = mapped_column(Text)
    sintomas: Mapped[str | None] = mapped_column(Text)
    diagnostico: Mapped[str | None] = mapped_column(Text)
    tratamento: Mapped[str | None] = mapped_column(Text)
    prescricao: Mapped[str | None] = mapped_column(Text)
    peso: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    temperatura: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    observacoes: Mapped[str | None] = mapped_column(Text)
    situacao: Mapped[str] = mapped_column(String(20), server_default="agendada")

    animal: Mapped[Animal] = relationship(lazy="joined")
    veterinario: Mapped[Veterinario] = relationship(lazy="joined")
