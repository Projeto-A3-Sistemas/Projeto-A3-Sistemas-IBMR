from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.animal import Referencia
from app.schemas.consulta import VeterinarioReferencia

SituacaoVacina = Literal["agendada", "aplicada", "cancelada"]


class VacinaBase(BaseModel):
    animal_id: int = Field(gt=0, examples=[1])
    veterinario_id: int = Field(gt=0, examples=[1])
    nome_vacina: str = Field(min_length=2, max_length=100, examples=["Rabisin"])
    tipo_vacina: str = Field(min_length=2, max_length=50, examples=["Antirrábica"])
    antirrabica: bool = Field(default=False, description="Marque true para vacina antirrábica (RN08)")
    fabricante: str = Field(min_length=2, max_length=100, examples=["Boehringer"])
    numero_lote: str = Field(min_length=1, max_length=50, examples=["L2026C"])
    data_aplicacao: date | None = Field(default=None, examples=["2026-11-19"])
    dose: str = Field(min_length=1, max_length=30, examples=["Dose única"])
    via_aplicacao: str | None = Field(default=None, max_length=30, examples=["Subcutânea"])
    data_proxima_dose: date | None = Field(default=None, examples=["2027-11-19"])
    validade_lote: date = Field(examples=["2027-06-30"])
    observacoes: str | None = None
    situacao: SituacaoVacina = "agendada"

    @model_validator(mode="after")
    def regras(self):
        if "antirr" in self.tipo_vacina.lower() and not self.antirrabica:
            raise ValueError("Vacina do tipo antirrábica precisa ter antirrabica = true.")
        if self.situacao == "aplicada":
            if self.data_aplicacao is None:
                raise ValueError("Vacina aplicada precisa da data de aplicação.")
            if self.data_aplicacao > date.today():
                raise ValueError("A data de aplicação não pode ser no futuro.")
            if self.validade_lote < self.data_aplicacao:
                raise ValueError("O lote estava vencido na data de aplicação.")
        if self.data_proxima_dose and self.data_aplicacao and self.data_proxima_dose <= self.data_aplicacao:
            raise ValueError("A próxima dose deve ser depois da data de aplicação.")
        return self


class VacinaCriar(VacinaBase):
    pass


class VacinaAtualizar(VacinaBase):
    pass


class VacinaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal: Referencia
    veterinario: VeterinarioReferencia
    nome_vacina: str
    tipo_vacina: str
    antirrabica: bool
    fabricante: str
    numero_lote: str
    data_aplicacao: date | None
    dose: str
    via_aplicacao: str | None
    data_proxima_dose: date | None
    validade_lote: date
    observacoes: str | None
    situacao: SituacaoVacina
