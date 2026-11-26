"""CRUD de veterinários (P3). Login e confirmação de senha ficam em auth (P1 + P3)."""
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Veterinario
from app.schemas.veterinario import VeterinarioAtualizar, VeterinarioCriar, VeterinarioResposta
from app.services.erros import tratar_erro_banco

router = APIRouter(prefix="/api/veterinarios", tags=["Veterinários"])


def _buscar(db: Session, vet_id: int) -> Veterinario:
    vet = db.get(Veterinario, vet_id)
    if not vet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Veterinário não encontrado.")
    return vet


@router.post("", response_model=VeterinarioResposta, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: VeterinarioCriar, db: Session = Depends(get_db)):
    """Cadastra um veterinário. A senha é guardada só como hash (bcrypt)."""
    valores = dados.model_dump(exclude={"senha"})
    senha_hash = bcrypt.hashpw(dados.senha.encode(), bcrypt.gensalt()).decode()
    vet = Veterinario(**valores, senha_hash=senha_hash, senha_confirmada=False)
    db.add(vet)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(vet)
    return vet


@router.get("", response_model=list[VeterinarioResposta])
def listar(incluir_inativos: bool = False, db: Session = Depends(get_db)):
    consulta = select(Veterinario).order_by(Veterinario.nome_completo)
    if not incluir_inativos:
        consulta = consulta.where(Veterinario.situacao == "ativo")
    return db.scalars(consulta).all()


@router.get("/{vet_id}", response_model=VeterinarioResposta)
def consultar(vet_id: int, db: Session = Depends(get_db)):
    return _buscar(db, vet_id)


@router.put("/{vet_id}", response_model=VeterinarioResposta)
def atualizar(vet_id: int, dados: VeterinarioAtualizar, db: Session = Depends(get_db)):
    vet = _buscar(db, vet_id)
    for campo, valor in dados.model_dump().items():
        setattr(vet, campo, valor)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(vet)
    return vet


@router.delete("/{vet_id}", response_model=VeterinarioResposta)
def inativar(vet_id: int, db: Session = Depends(get_db)):
    """Exclusão lógica: o veterinário fica INATIVO e não consegue mais entrar."""
    vet = _buscar(db, vet_id)
    vet.situacao = "inativo"
    db.commit()
    db.refresh(vet)
    return vet
