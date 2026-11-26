from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.comum import Situacao
from app.services.validacoes import cpf_valido, so_digitos

UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


class VeterinarioBase(BaseModel):
    nome_completo: str = Field(min_length=3, max_length=150, examples=["Ana Lima"])
    crmv_numero: str = Field(min_length=1, max_length=15, examples=["12345"])
    crmv_uf: str = Field(examples=["RJ"])
    email: EmailStr = Field(examples=["ana@clinica.com"])
    telefone: str = Field(min_length=10, max_length=20, examples=["21988880001"])

    @field_validator("crmv_uf")
    @classmethod
    def validar_uf(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in UFS:
            raise ValueError("UF inválida.")
        return v

    @field_validator("email")
    @classmethod
    def email_minusculo(cls, v: str) -> str:
        return v.lower()

    @field_validator("telefone")
    @classmethod
    def limpar_telefone(cls, v: str) -> str:
        return so_digitos(v)


class VeterinarioCriar(VeterinarioBase):
    cpf: str = Field(examples=["111.444.777-35"])
    senha: str = Field(min_length=8, max_length=72, examples=["Senha@123"])

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        if not cpf_valido(v):
            raise ValueError("CPF inválido.")
        return so_digitos(v)


class VeterinarioAtualizar(VeterinarioBase):
    """CPF e senha não mudam por aqui (senha é parte do login)."""


class VeterinarioResposta(BaseModel):
    """Nunca devolve a senha nem o hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_completo: str
    cpf: str
    crmv_numero: str
    crmv_uf: str
    email: str
    telefone: str
    senha_confirmada: bool
    data_cadastro: datetime
    situacao: Situacao
    ultimo_acesso: datetime | None
