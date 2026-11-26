"""Catálogo de raças (P4 - Milestone 2, RF13)."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Especie, Raca
from app.schemas.raca import RacaAtualizar, RacaCriar, RacaResposta
from app.services.erros import tratar_erro_banco

router = APIRouter(prefix="/api/racas", tags=["Raças"])


def _buscar(db: Session, raca_id: int) -> Raca:
    raca = db.get(Raca, raca_id)
    if not raca:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Raça não encontrada.")
    return raca


def _conferir_especie_ativa(db: Session, especie_id: int) -> None:
    especie = db.get(Especie, especie_id)
    if not especie or especie.situacao != "ativo":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Espécie não encontrada ou inativa.")


def _conferir_nome_livre(db: Session, especie_id: int, nome: str, ignorar_id: int | None = None) -> None:
    """O banco não impede a mesma raça duas vezes na mesma espécie; a API impede."""
    consulta = select(Raca).where(Raca.especie_id == especie_id, func.lower(Raca.nome) == nome.lower())
    if ignorar_id:
        consulta = consulta.where(Raca.id != ignorar_id)
    if db.scalar(consulta):
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta raça já está cadastrada para esta espécie.")


def _salvar(db: Session, raca: Raca) -> Raca:
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(raca)
    return raca


@router.post("", response_model=RacaResposta, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: RacaCriar, db: Session = Depends(get_db)):
    _conferir_especie_ativa(db, dados.especie_id)
    _conferir_nome_livre(db, dados.especie_id, dados.nome)
    raca = Raca(**dados.model_dump())
    db.add(raca)
    return _salvar(db, raca)


@router.get("", response_model=list[RacaResposta])
def listar(
    especie_id: int | None = Query(None, description="Filtrar pelas raças de uma espécie"),
    incluir_inativas: bool = False,
    db: Session = Depends(get_db),
):
    consulta = select(Raca).order_by(Raca.nome)
    if especie_id:
        consulta = consulta.where(Raca.especie_id == especie_id)
    if not incluir_inativas:
        consulta = consulta.where(Raca.situacao == "ativo")
    return db.scalars(consulta).all()


@router.get("/{raca_id}", response_model=RacaResposta)
def consultar(raca_id: int, db: Session = Depends(get_db)):
    return _buscar(db, raca_id)


@router.put("/{raca_id}", response_model=RacaResposta)
def atualizar(raca_id: int, dados: RacaAtualizar, db: Session = Depends(get_db)):
    raca = _buscar(db, raca_id)
    _conferir_especie_ativa(db, dados.especie_id)
    _conferir_nome_livre(db, dados.especie_id, dados.nome, ignorar_id=raca_id)
    for campo, valor in dados.model_dump().items():
        setattr(raca, campo, valor)
    return _salvar(db, raca)


@router.delete("/{raca_id}", response_model=RacaResposta)
def inativar(raca_id: int, db: Session = Depends(get_db)):
    """Exclusão lógica (RN14): a raça fica inativa e os animais já cadastrados são mantidos."""
    raca = _buscar(db, raca_id)
    raca.situacao = "inativo"
    return _salvar(db, raca)
