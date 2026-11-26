"""Models (tabelas) do banco do governo.

Mapeiam as tabelas criadas por db/governo/01_schema.sql, iguais ao diagrama do Milestone 1.
Eles não criam nem alteram tabelas.
"""
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

# BIGSERIAL no Postgres; Integer no SQLite (usado só nos testes automatizados).
ID = BigInteger().with_variant(Integer, "sqlite")


class AnimalGoverno(Base):
    __tablename__ = "animal_governo"

    id: Mapped[int] = mapped_column(ID, primary_key=True, autoincrement=True)
    microchip: Mapped[str] = mapped_column(String(30), unique=True)
    nome: Mapped[str] = mapped_column(String(100))
    especie: Mapped[str] = mapped_column(String(50))
    raca: Mapped[str | None] = mapped_column(String(50))
    sexo: Mapped[str] = mapped_column(String(1))
    data_nascimento: Mapped[date | None] = mapped_column(Date)
    tutor_nome: Mapped[str] = mapped_column(String(150))
    tutor_cpf: Mapped[str] = mapped_column(String(11))
    data_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_atualizacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class VacinacaoAntirrabica(Base):
    __tablename__ = "vacinacao_antirrabica"

    id: Mapped[int] = mapped_column(ID, primary_key=True, autoincrement=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animal_governo.id"))
    fabricante: Mapped[str] = mapped_column(String(100))
    lote: Mapped[str] = mapped_column(String(50))
    vacina: Mapped[str] = mapped_column(String(100))
    data_aplicacao: Mapped[date] = mapped_column(Date)
    veterinario_nome: Mapped[str] = mapped_column(String(150))
    veterinario_crmv: Mapped[str] = mapped_column(String(20))   # "12345/RJ"
    chave_idempotencia: Mapped[str] = mapped_column(String(100), unique=True)


class Operacao(Base):
    __tablename__ = "operacao"

    id: Mapped[int] = mapped_column(ID, primary_key=True, autoincrement=True)
    protocolo: Mapped[str] = mapped_column(String(40), unique=True)
    tipo: Mapped[str] = mapped_column(String(30))
    situacao: Mapped[str] = mapped_column(String(20))
    data: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    mensagem: Mapped[str | None] = mapped_column(Text)
