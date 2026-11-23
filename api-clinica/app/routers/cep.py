"""Consulta de CEP no ViaCEP (P4 - Milestone 3, RF10, RF11, teste 6)."""
from fastapi import APIRouter

from app.schemas.endereco import CepResposta
from app.services.viacep import consultar_cep

router = APIRouter(prefix="/api/cep", tags=["CEP (ViaCEP)"])


@router.get(
    "/{cep}",
    response_model=CepResposta,
    responses={
        404: {"description": "CEP inexistente"},
        422: {"description": "CEP mal formatado"},
        503: {"description": "ViaCEP fora do ar"},
        504: {"description": "ViaCEP não respondeu em 5 segundos"},
    },
)
def consultar(cep: str):
    """Devolve o endereço do CEP para o frontend preencher o formulário."""
    return consultar_cep(cep)
