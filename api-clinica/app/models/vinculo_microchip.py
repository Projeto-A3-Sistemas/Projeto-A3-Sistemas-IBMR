from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.veterinario import Veterinario


class VinculoMicrochip(Base):
    """Histórico de microchips do animal. Só um pode estar 'ativo' por animal (RN06)."""

    __tablename__ = "vinculo_microchip"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animal.id"))
    codigo_microchip: Mapped[str] = mapped_column(String(30), unique=True)
    veterinario_id: Mapped[int] = mapped_column(ForeignKey("veterinario.id"))
    data_implantacao: Mapped[date] = mapped_column(Date)
    data_vinculo: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    situacao: Mapped[str] = mapped_column(String(12), server_default="ativo")

    veterinario: Mapped[Veterinario] = relationship(lazy="joined")
