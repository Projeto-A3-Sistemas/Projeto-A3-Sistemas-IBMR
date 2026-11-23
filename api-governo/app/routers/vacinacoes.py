"""Recebimento de vacinação antirrábica (P4 - RF34, RF35)."""
from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.comum import ERROS, resultado
from app.schemas import ResultadoOperacao, VacinacaoCriar
from app.services import operacoes

router = APIRouter(prefix="/api/governo/vacinacoes-antirrabicas", tags=["Vacinação antirrábica"])


@router.post("", response_model=ResultadoOperacao, status_code=201, responses=ERROS)
def registrar(dados: VacinacaoCriar, response: Response, db: Session = Depends(get_db),
              idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=100,
                                            description="Obrigatório. Padrão do grupo: VAC-{id da vacina}")):
    """Registra a vacinação. O cabeçalho **Idempotency-Key** é obrigatório.

    * Primeira vez: **201** com protocolo novo.
    * Mesma chave e mesmo conteúdo: **200**, mesmo protocolo, nenhuma vacinação nova.
    * Mesma chave e conteúdo diferente: **409**.
    """
    op, repetida = operacoes.registrar_vacinacao(db, dados, idempotency_key)
    return resultado(op, repetida, response)
