"""Vacinas (P3 - Milestone 3)."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Vacina
from app.schemas.vacina import SituacaoVacina, VacinaAtualizar, VacinaCriar, VacinaResposta
from app.services.erros import tratar_erro_banco
from app.services.integracao import enviar_em_segundo_plano, registrar_envio_antirrabica
from app.services.vinculos import conferir_animal_e_veterinario

router = APIRouter(prefix="/api/vacinas", tags=["Vacinas"])


def _buscar(db: Session, vacina_id: int) -> Vacina:
    vacina = db.get(Vacina, vacina_id)
    if not vacina:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vacina não encontrada.")
    return vacina


def _salvar(db: Session, vacina: Vacina, tarefas: BackgroundTasks | None = None) -> Vacina:
    try:
        db.flush()
        integracao = registrar_envio_antirrabica(db, vacina)
        integracao_id = integracao.id if integracao and integracao.situacao != "confirmada" else None
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(vacina)
    if tarefas:
        enviar_em_segundo_plano(tarefas, integracao_id)
    return vacina


@router.post("", response_model=VacinaResposta, status_code=status.HTTP_201_CREATED)
def registrar(dados: VacinaCriar, tarefas: BackgroundTasks, db: Session = Depends(get_db)):
    """Registra uma vacina. Antirrábica aplicada fica pendente de envio ao governo."""
    conferir_animal_e_veterinario(db, dados.animal_id, dados.veterinario_id)
    vacina = Vacina(**dados.model_dump())
    db.add(vacina)
    return _salvar(db, vacina, tarefas)


@router.get("", response_model=list[VacinaResposta])
def listar(
    animal_id: int | None = Query(None, description="Histórico de vacinas de um animal"),
    antirrabica: bool | None = None,
    situacao: SituacaoVacina | None = None,
    db: Session = Depends(get_db),
):
    consulta = select(Vacina).order_by(Vacina.data_aplicacao.desc().nulls_first(), Vacina.id.desc())
    if animal_id:
        consulta = consulta.where(Vacina.animal_id == animal_id)
    if antirrabica is not None:
        consulta = consulta.where(Vacina.antirrabica == antirrabica)
    if situacao:
        consulta = consulta.where(Vacina.situacao == situacao)
    return db.scalars(consulta).unique().all()


@router.get("/{vacina_id}", response_model=VacinaResposta)
def consultar(vacina_id: int, db: Session = Depends(get_db)):
    return _buscar(db, vacina_id)


@router.put("/{vacina_id}", response_model=VacinaResposta)
def atualizar(vacina_id: int, dados: VacinaAtualizar, tarefas: BackgroundTasks, db: Session = Depends(get_db)):
    vacina = _buscar(db, vacina_id)
    conferir_animal_e_veterinario(db, dados.animal_id, dados.veterinario_id)
    for campo, valor in dados.model_dump().items():
        setattr(vacina, campo, valor)
    return _salvar(db, vacina, tarefas)


@router.delete("/{vacina_id}", response_model=VacinaResposta)
def cancelar(vacina_id: int, db: Session = Depends(get_db)):
    """Cancela a vacina (o registro é mantido no histórico)."""
    vacina = _buscar(db, vacina_id)
    if vacina.situacao == "aplicada":
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Vacina já aplicada não pode ser cancelada."
        )
    vacina.situacao = "cancelada"
    return _salvar(db, vacina)
