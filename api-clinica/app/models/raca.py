from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Raca(Base):
    __tablename__ = "raca"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    descricao: Mapped[str | None] = mapped_column(Text)
    situacao: Mapped[str] = mapped_column(String(10), server_default="ativo")
    especie_id: Mapped[int] = mapped_column(ForeignKey("especie.id"))
