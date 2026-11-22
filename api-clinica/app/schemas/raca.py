from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.comum import Situacao


class RacaBase(BaseModel):
    especie_id: int = Field(gt=0, examples=[1])
    nome: str = Field(min_length=2, max_length=50, examples=["Labrador"])
    descricao: str | None = Field(default=None, examples=["Porte grande"])

    @field_validator("nome")
    @classmethod
    def normalizar_nome(cls, v: str) -> str:
        """'  golden   retriever ' -> 'Golden Retriever'."""
        return " ".join(v.split()).title()


class RacaCriar(RacaBase):
    pass


class RacaAtualizar(RacaBase):
    pass


class RacaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    especie_id: int
    nome: str
    descricao: str | None
    situacao: Situacao
