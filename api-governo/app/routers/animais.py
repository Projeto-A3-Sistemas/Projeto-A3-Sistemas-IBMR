"""Animais registrados no governo (P4 - RF33)."""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.comum import ERROS, resultado
from app.schemas import AnimalAtualizar, AnimalCriar, AnimalResposta, ResultadoOperacao
from app.services import operacoes

router = APIRouter(prefix="/api/governo/animais", tags=["Animais"])


@router.post("", response_model=ResultadoOperacao, status_code=201, responses=ERROS)
def cadastrar(dados: AnimalCriar, response: Response, db: Session = Depends(get_db)):
    """Registra o animal pelo microchip.

    Reenviar o mesmo cadastro devolve o protocolo original (200, `reprocessada=true`).
    Mesmo microchip com dados diferentes: 409 (use PUT).
    """
    op, repetida = operacoes.cadastrar_animal(db, dados)
    return resultado(op, repetida, response)


@router.get("/{microchip}", response_model=AnimalResposta, responses=ERROS)
def consultar(microchip: str, db: Session = Depends(get_db)):
    return operacoes.consultar_animal(db, microchip)


@router.put("/{microchip}", response_model=ResultadoOperacao, responses=ERROS)
def atualizar(microchip: str, dados: AnimalAtualizar, response: Response, db: Session = Depends(get_db)):
    op = operacoes.atualizar_animal(db, microchip, dados)
    return resultado(op, False, response)
