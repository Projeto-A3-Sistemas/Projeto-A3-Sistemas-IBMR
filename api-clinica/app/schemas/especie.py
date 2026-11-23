from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.comum import Situacao


class EspecieBase(BaseModel):
    nome: str = Field(min_length=2, max_length=50, examples=["Cão"])
    descricao: str | None = Field(default=None, examples=["Canis lupus familiaris"])

    @field_validator("nome")
    @classmethod
    def normalizar_nome(cls, v: str) -> str:
        """'  cão ' -> 'Cão' (evita duplicidade por espaço ou maiúscula)."""
        return " ".join(v.split()).capitalize()


class EspecieCriar(EspecieBase):
    pass


class EspecieAtualizar(EspecieBase):
    pass


class EspecieResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str | None
    situacao: Situacao
