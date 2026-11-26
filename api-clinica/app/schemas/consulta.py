from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.animal import Referencia

SituacaoConsulta = Literal["agendada", "realizada", "cancelada", "nao_compareceu"]


class ConsultaBase(BaseModel):
    animal_id: int = Field(gt=0, examples=[1])
    veterinario_id: int = Field(gt=0, examples=[1])
    data_hora: datetime = Field(examples=["2026-11-25T10:00:00"])
    motivo: str = Field(min_length=3, max_length=200, examples=["Check-up anual"])
    anamnese: str | None = None
    sintomas: str | None = None
    diagnostico: str | None = None
    tratamento: str | None = None
    prescricao: str | None = None
    peso: Decimal | None = Field(default=None, gt=0, max_digits=6, decimal_places=2, examples=[28.5])
    temperatura: Decimal | None = Field(default=None, ge=30, le=45, max_digits=4, decimal_places=1, examples=[38.5])
    observacoes: str | None = None
    situacao: SituacaoConsulta = "agendada"


class ConsultaCriar(ConsultaBase):
    pass


class ConsultaAtualizar(ConsultaBase):
    pass


class VeterinarioReferencia(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_completo: str


class ConsultaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal: Referencia
    veterinario: VeterinarioReferencia
    data_hora: datetime
    motivo: str
    anamnese: str | None
    sintomas: str | None
    diagnostico: str | None
    tratamento: str | None
    prescricao: str | None
    peso: Decimal | None
    temperatura: Decimal | None
    observacoes: str | None
    situacao: SituacaoConsulta
