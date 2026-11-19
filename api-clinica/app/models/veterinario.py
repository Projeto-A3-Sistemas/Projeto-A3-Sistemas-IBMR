from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Veterinario(Base):
    __tablename__ = "veterinario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_completo: Mapped[str] = mapped_column(String(150))
    cpf: Mapped[str] = mapped_column(String(11), unique=True)
    crmv_numero: Mapped[str] = mapped_column(String(15))
    crmv_uf: Mapped[str] = mapped_column(String(2))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    telefone: Mapped[str] = mapped_column(String(20))
    senha_hash: Mapped[str] = mapped_column(String(255))
    senha_confirmada: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    data_confirmacao: Mapped[datetime | None] = mapped_column(DateTime)
    data_cadastro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    situacao: Mapped[str] = mapped_column(String(10), server_default="ativo")
    ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime)
