"""CRUD de tutores (P3)."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Endereco, Tutor
from app.schemas.tutor import TutorAtualizar, TutorCriar, TutorResposta
from app.services.erros import tratar_erro_banco
from app.services.validacoes import so_digitos

router = APIRouter(prefix="/api/tutores", tags=["Tutores"])


def _buscar(db: Session, tutor_id: int) -> Tutor:
    tutor = db.get(Tutor, tutor_id)
    if not tutor:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tutor não encontrado.")
    return tutor


def _conferir_endereco(db: Session, endereco_id: int) -> None:
    if not db.get(Endereco, endereco_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Endereço não encontrado.")


@router.post("", response_model=TutorResposta, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: TutorCriar, db: Session = Depends(get_db)):
    """Cadastra um tutor. O endereço precisa existir (endereco_id)."""
    _conferir_endereco(db, dados.endereco_id)
    tutor = Tutor(**dados.model_dump())
    db.add(tutor)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(tutor)
    return tutor


@router.get("", response_model=list[TutorResposta])
def listar(
    busca: str | None = Query(None, description="Parte do nome ou CPF"),
    incluir_inativos: bool = False,
    db: Session = Depends(get_db),
):
    """Lista os tutores. Por padrão mostra só os ativos."""
    consulta = select(Tutor).order_by(Tutor.nome_completo)
    if not incluir_inativos:
        consulta = consulta.where(Tutor.situacao == "ativo")
    if busca:
        filtros = [Tutor.nome_completo.ilike(f"%{busca}%")]
        if so_digitos(busca):
            filtros.append(Tutor.cpf.contains(so_digitos(busca)))
        consulta = consulta.where(or_(*filtros))
    return db.scalars(consulta).unique().all()


@router.get("/{tutor_id}", response_model=TutorResposta)
def consultar(tutor_id: int, db: Session = Depends(get_db)):
    return _buscar(db, tutor_id)


@router.put("/{tutor_id}", response_model=TutorResposta)
def atualizar(tutor_id: int, dados: TutorAtualizar, db: Session = Depends(get_db)):
    """Atualiza os dados do tutor (o CPF não pode ser alterado)."""
    tutor = _buscar(db, tutor_id)
    _conferir_endereco(db, dados.endereco_id)
    for campo, valor in dados.model_dump().items():
        setattr(tutor, campo, valor)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(tutor)
    return tutor


@router.delete("/{tutor_id}", response_model=TutorResposta)
def inativar(tutor_id: int, db: Session = Depends(get_db)):
    """Exclusão lógica: o tutor fica INATIVO e o histórico é preservado."""
    tutor = _buscar(db, tutor_id)
    tutor.situacao = "inativo"
    db.commit()
    db.refresh(tutor)
    return tutor
