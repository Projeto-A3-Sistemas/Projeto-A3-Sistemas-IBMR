from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TokenRevogado(Base):
    __tablename__ = "token_revogado"

    jti: Mapped[str] = mapped_column(String(36), primary_key=True)
    expira_em: Mapped[datetime] = mapped_column(DateTime)
