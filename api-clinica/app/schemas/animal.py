from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.comum import Situacao


class AnimalBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100, examples=["Rex"])
    data_nascimento: date | None = Field(default=None, examples=["2020-03-15"])
    idade_estimada_meses: int | None = Field(default=None, ge=0, le=600)
    sexo: Literal["M", "F"] = Field(examples=["M"])
    cor: str | None = Field(default=None, max_length=50, examples=["Caramelo"])
    peso_atual: Decimal | None = Field(default=None, gt=0, max_digits=6, decimal_places=2, examples=[28.5])
    tutor_id: int = Field(gt=0, examples=[1])
    especie_id: int = Field(gt=0, examples=[1])
    raca_id: int | None = Field(default=None, gt=0, examples=[1])

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_no_passado(cls, v: date | None) -> date | None:
        if v and v > date.today():
            raise ValueError("A data de nascimento não pode ser no futuro.")
        return v

    @model_validator(mode="after")
    def nascimento_ou_idade(self):
        if self.data_nascimento is None and self.idade_estimada_meses is None:
            raise ValueError("Informe a data de nascimento ou a idade estimada em meses.")
        return self


class AnimalCriar(AnimalBase):
    pass


class AnimalAtualizar(AnimalBase):
    pass


class Referencia(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str


class TutorReferencia(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_completo: str


class AnimalResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    data_nascimento: date | None
    idade_estimada_meses: int | None
    sexo: str
    cor: str | None
    peso_atual: Decimal | None
    tutor: TutorReferencia
    especie: Referencia
    raca: Referencia | None
    data_cadastro: datetime
    situacao: Situacao
