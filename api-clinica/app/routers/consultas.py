"""Consultas clínicas (P3 - Milestone 3)."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Consulta
from app.schemas.consulta import ConsultaAtualizar, ConsultaCriar, ConsultaResposta, SituacaoConsulta
from app.services.erros import tratar_erro_banco
from app.services.vinculos import conferir_animal_e_veterinario

router = APIRouter(prefix="/api/consultas", tags=["Consultas"])


def _buscar(db: Session, consulta_id: int) -> Consulta:
    consulta = db.get(Consulta, consulta_id)
    if not consulta:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Consulta não encontrada.")
    return consulta


def _salvar(db: Session, consulta: Consulta) -> Consulta:
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(consulta)
    return consulta


@router.post("", response_model=ConsultaResposta, status_code=status.HTTP_201_CREATED)
def registrar(dados: ConsultaCriar, db: Session = Depends(get_db)):
    """Agenda ou registra uma consulta."""
    conferir_animal_e_veterinario(db, dados.animal_id, dados.veterinario_id)
    consulta = Consulta(**dados.model_dump())
    db.add(consulta)
    return _salvar(db, consulta)


@router.get("", response_model=list[ConsultaResposta])
def listar(
    animal_id: int | None = Query(None, description="Histórico de consultas de um animal"),
    veterinario_id: int | None = None,
    situacao: SituacaoConsulta | None = None,
    db: Session = Depends(get_db),
):
    """Lista consultas, da mais recente para a mais antiga."""
    consulta = select(Consulta).order_by(Consulta.data_hora.desc())
    if animal_id:
        consulta = consulta.where(Consulta.animal_id == animal_id)
    if veterinario_id:
        consulta = consulta.where(Consulta.veterinario_id == veterinario_id)
    if situacao:
        consulta = consulta.where(Consulta.situacao == situacao)
    return db.scalars(consulta).unique().all()


@router.get("/{consulta_id}", response_model=ConsultaResposta)
def consultar(consulta_id: int, db: Session = Depends(get_db)):
    return _buscar(db, consulta_id)


@router.put("/{consulta_id}", response_model=ConsultaResposta)
def atualizar(consulta_id: int, dados: ConsultaAtualizar, db: Session = Depends(get_db)):
    """Atualiza a consulta (ex.: registrar o atendimento e marcar como realizada)."""
    consulta = _buscar(db, consulta_id)
    conferir_animal_e_veterinario(db, dados.animal_id, dados.veterinario_id)
    for campo, valor in dados.model_dump().items():
        setattr(consulta, campo, valor)
    return _salvar(db, consulta)


@router.delete("/{consulta_id}", response_model=ConsultaResposta)
def cancelar(consulta_id: int, db: Session = Depends(get_db)):
    """Cancela a consulta (o registro é mantido no histórico)."""
    consulta = _buscar(db, consulta_id)
    consulta.situacao = "cancelada"
    return _salvar(db, consulta)
