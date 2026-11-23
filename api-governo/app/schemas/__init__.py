"""Entrada e saída da API governamental (Pydantic)."""
import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AVISO = "Serviço governamental SIMULADO para fins acadêmicos — não é integração oficial."


def so_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


# ---------- Animal ----------

class AnimalDados(BaseModel):
    nome: str = Field(min_length=1, max_length=100, examples=["Rex"])
    especie: str = Field(min_length=1, max_length=50, examples=["Cão"])
    raca: str | None = Field(default=None, max_length=50, examples=["Labrador"])
    sexo: Literal["M", "F"] = Field(examples=["M"])
    data_nascimento: date | None = Field(default=None, examples=["2020-03-15"])
    tutor_nome: str = Field(min_length=3, max_length=150, examples=["João Souza"])
    tutor_cpf: str = Field(examples=["987.654.321-00"])

    @field_validator("tutor_cpf")
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        """Só confere o formato (11 dígitos). Quem valida os dígitos do CPF é a
        clínica, no cadastro do tutor (RF09, RN02)."""
        v = so_digitos(v)
        if len(v) != 11:
            raise ValueError("O CPF do tutor deve ter 11 dígitos.")
        return v

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_no_passado(cls, v: date | None) -> date | None:
        if v and v > date.today():
            raise ValueError("A data de nascimento não pode ser no futuro.")
        return v


class AnimalCriar(AnimalDados):
    microchip: str = Field(min_length=9, max_length=30, examples=["985112345678903"])

    @field_validator("microchip")
    @classmethod
    def limpar_microchip(cls, v: str) -> str:
        v = v.strip().upper()
        if not v.isalnum():
            raise ValueError("O microchip deve ter apenas letras e números.")
        return v


class AnimalAtualizar(AnimalDados):
    pass


class AnimalResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    microchip: str
    nome: str
    especie: str
    raca: str | None
    sexo: str
    data_nascimento: date | None
    tutor_nome: str
    tutor_cpf: str
    data_registro: datetime
    data_atualizacao: datetime
    aviso: str = AVISO


# ---------- Vacinação ----------

class VacinacaoCriar(BaseModel):
    microchip: str = Field(min_length=9, max_length=30, examples=["985112345678999"])
    vacina: str = Field(min_length=1, max_length=100, examples=["Rabisin"])
    fabricante: str = Field(min_length=1, max_length=100, examples=["Boehringer"])
    lote: str = Field(min_length=1, max_length=50, examples=["L2026C"])
    data_aplicacao: date = Field(examples=["2026-11-19"])
    veterinario_nome: str = Field(min_length=3, max_length=150, examples=["Ana Lima"])
    veterinario_crmv: str = Field(min_length=1, max_length=15, examples=["12345"])
    veterinario_crmv_uf: str = Field(min_length=2, max_length=2, examples=["RJ"])
    animal: AnimalDados | None = Field(
        default=None,
        description="Dados do animal. Se ele ainda não estiver registrado no governo, é cadastrado "
                    "junto com a vacinação (enunciado, seção 4, regra 2). Recomendado enviar sempre.",
    )

    @field_validator("microchip")
    @classmethod
    def limpar_microchip(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("veterinario_crmv_uf")
    @classmethod
    def uf_maiuscula(cls, v: str) -> str:
        return v.upper()

    @field_validator("data_aplicacao")
    @classmethod
    def aplicacao_no_passado(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("A data de aplicação não pode ser no futuro.")
        return v

    @property
    def crmv_completo(self) -> str:
        return f"{self.veterinario_crmv}/{self.veterinario_crmv_uf}"


# ---------- Respostas ----------

class ResultadoOperacao(BaseModel):
    protocolo: str = Field(examples=["GOV-2026-0005"])
    tipo: str = Field(examples=["VACINA_ANTIRRABICA"])
    situacao: str = Field(examples=["PROCESSADA"])
    mensagem: str
    data: datetime
    reprocessada: bool = Field(
        default=False,
        description="true quando a requisição repetiu uma já processada: devolve o mesmo protocolo",
    )
    aviso: str = AVISO


class OperacaoResposta(BaseModel):
    protocolo: str
    tipo: str
    situacao: str
    data: datetime
    mensagem: str | None
    microchip: str | None
    aviso: str = AVISO


class ErroResposta(BaseModel):
    codigo: str
    mensagem: str
    protocolo: str | None = None
    aviso: str = AVISO


# ---------- Modo falha ----------

TipoFalha = Literal["DESLIGADO", "INDISPONIVEL", "ERRO_VALIDACAO", "LENTO"]


class ModoFalha(BaseModel):
    tipo: TipoFalha = Field(examples=["INDISPONIVEL"])
    atraso_segundos: float = Field(default=10, ge=0, le=60)


class ModoFalhaResposta(ModoFalha):
    ativo: bool
