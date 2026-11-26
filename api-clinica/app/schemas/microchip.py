from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.consulta import VeterinarioReferencia


class MicrochipVincular(BaseModel):
    codigo_microchip: str = Field(examples=["985112345678903"], description="9 a 30 letras/números (padrão ISO: 15 dígitos)")
    veterinario_id: int = Field(gt=0, examples=[1])
    data_implantacao: date = Field(examples=["2026-11-23"])

    @field_validator("codigo_microchip")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        v = v.replace(" ", "").strip().upper()
        if not (9 <= len(v) <= 30) or not v.isalnum():
            raise ValueError("O microchip deve ter de 9 a 30 letras ou números.")
        return v

    @field_validator("data_implantacao")
    @classmethod
    def implantacao_no_passado(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("A data de implantação não pode ser no futuro.")
        return v


class MicrochipResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_id: int
    codigo_microchip: str
    veterinario: VeterinarioReferencia
    data_implantacao: date
    data_vinculo: datetime
    situacao: Literal["ativo", "substituido"]
