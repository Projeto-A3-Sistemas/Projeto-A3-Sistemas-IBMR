from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.animal import Animal


class IntegracaoGoverno(Base):
    """Cada linha é uma comunicação com a API governamental (cadastro, atualização ou vacina)."""

    __tablename__ = "integracao_governo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animal.id"))
    vacina_id: Mapped[int | None] = mapped_column(ForeignKey("vacina.id"))
    tipo_operacao: Mapped[str] = mapped_column(String(30))
    protocolo_externo: Mapped[str | None] = mapped_column(String(50))
    chave_idempotencia: Mapped[str] = mapped_column(String(100), unique=True)
    situacao: Mapped[str] = mapped_column(String(12), server_default="pendente")
    data_solicitacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_resposta: Mapped[datetime | None] = mapped_column(DateTime)
    tentativas: Mapped[int] = mapped_column(Integer, server_default="0")
    mensagem_erro: Mapped[str | None] = mapped_column(Text)

    animal: Mapped[Animal] = relationship(lazy="joined")
