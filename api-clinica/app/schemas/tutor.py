from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.comum import Situacao
from app.services.validacoes import cpf_valido, so_digitos


class EnderecoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cep: str
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cidade: str
    uf: str


class TutorBase(BaseModel):
    nome_completo: str = Field(min_length=3, max_length=150, examples=["Maria Silva"])
    data_nascimento: date = Field(examples=["1990-05-20"])
    email: EmailStr = Field(examples=["maria@email.com"])
    telefone: str = Field(min_length=10, max_length=20, examples=["21999990001"])
    endereco_id: int = Field(gt=0, examples=[1])

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_no_passado(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("A data de nascimento deve ser no passado.")
        return v

    @field_validator("telefone")
    @classmethod
    def limpar_telefone(cls, v: str) -> str:
        return so_digitos(v)


class TutorCriar(TutorBase):
    cpf: str = Field(examples=["529.982.247-25"])

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        if not cpf_valido(v):
            raise ValueError("CPF inválido.")
        return so_digitos(v)


class TutorAtualizar(TutorBase):
    """O CPF não muda depois do cadastro."""


class TutorResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_completo: str
    cpf: str
    data_nascimento: date
    email: str
    telefone: str
    endereco_id: int
    endereco: EnderecoResumo
    data_cadastro: datetime
    situacao: Situacao
