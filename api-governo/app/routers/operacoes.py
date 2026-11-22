"""Consulta de operação por protocolo (P4 - RF37)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.comum import ERROS
from app.schemas import OperacaoResposta
from app.services import operacoes

router = APIRouter(prefix="/api/governo/operacoes", tags=["Operações"])


@router.get("/{protocolo}", response_model=OperacaoResposta, responses=ERROS)
def consultar(protocolo: str, db: Session = Depends(get_db)):
    return operacoes.consultar_operacao(db, protocolo)
