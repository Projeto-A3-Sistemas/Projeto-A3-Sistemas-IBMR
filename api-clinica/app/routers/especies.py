"""Catálogo de espécies (P4 - Milestone 2, RF12)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Especie
from app.schemas.especie import EspecieAtualizar, EspecieCriar, EspecieResposta
from app.services.erros import tratar_erro_banco

router = APIRouter(prefix="/api/especies", tags=["Espécies"])


def _buscar(db: Session, especie_id: int) -> Especie:
    especie = db.get(Especie, especie_id)
    if not especie:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Espécie não encontrada.")
    return especie


def _conferir_nome_livre(db: Session, nome: str, ignorar_id: int | None = None) -> None:
    consulta = select(Especie).where(func.lower(Especie.nome) == nome.lower())
    if ignorar_id:
        consulta = consulta.where(Especie.id != ignorar_id)
    if db.scalar(consulta):
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma espécie com este nome.")


def _salvar(db: Session, especie: Especie) -> Especie:
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(especie)
    return especie


@router.post("", response_model=EspecieResposta, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: EspecieCriar, db: Session = Depends(get_db)):
    _conferir_nome_livre(db, dados.nome)
    especie = Especie(**dados.model_dump())
    db.add(especie)
    return _salvar(db, especie)


@router.get("", response_model=list[EspecieResposta])
def listar(incluir_inativas: bool = False, db: Session = Depends(get_db)):
    """Lista as espécies em ordem alfabética. Por padrão mostra só as ativas."""
    consulta = select(Especie).order_by(Especie.nome)
    if not incluir_inativas:
        consulta = consulta.where(Especie.situacao == "ativo")
    return db.scalars(consulta).all()


@router.get("/{especie_id}", response_model=EspecieResposta)
def consultar(especie_id: int, db: Session = Depends(get_db)):
    return _buscar(db, especie_id)


@router.put("/{especie_id}", response_model=EspecieResposta)
def atualizar(especie_id: int, dados: EspecieAtualizar, db: Session = Depends(get_db)):
    especie = _buscar(db, especie_id)
    _conferir_nome_livre(db, dados.nome, ignorar_id=especie_id)
    for campo, valor in dados.model_dump().items():
        setattr(especie, campo, valor)
    return _salvar(db, especie)


@router.delete("/{especie_id}", response_model=EspecieResposta)
def inativar(especie_id: int, db: Session = Depends(get_db)):
    """Exclusão lógica (RN14): a espécie fica inativa e os animais já cadastrados são mantidos."""
    especie = _buscar(db, especie_id)
    especie.situacao = "inativo"
    return _salvar(db, especie)
