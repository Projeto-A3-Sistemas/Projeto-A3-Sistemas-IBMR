from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.validacoes import so_digitos

UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB",
       "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}


class EnderecoBase(BaseModel):
    """Basta enviar cep + numero: o resto é preenchido pelo ViaCEP (RF10).
    O que for enviado preenchido tem prioridade (complementação manual)."""

    cep: str = Field(examples=["20040-020"])
    numero: str = Field(min_length=1, max_length=10, examples=["10"])
    complemento: str | None = Field(default=None, max_length=80, examples=["Sala 5"])
    logradouro: str | None = Field(default=None, max_length=150)
    bairro: str | None = Field(default=None, max_length=80)
    cidade: str | None = Field(default=None, max_length=80)
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    codigo_ibge: str | None = Field(default=None, max_length=7)

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, v: str) -> str:
        v = so_digitos(v)
        if len(v) != 8:
            raise ValueError("CEP deve ter 8 dígitos.")
        return v

    @field_validator("uf")
    @classmethod
    def validar_uf(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.upper()
        if v not in UFS:
            raise ValueError("UF inválida.")
        return v


class EnderecoCriar(EnderecoBase):
    pass


class EnderecoAtualizar(EnderecoBase):
    pass


class EnderecoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cep: str
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cidade: str
    uf: str
    codigo_ibge: str | None


class CepResposta(BaseModel):
    cep: str
    logradouro: str
    complemento: str
    bairro: str
    cidade: str
    uf: str
    codigo_ibge: str
