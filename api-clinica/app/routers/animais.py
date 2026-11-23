"""CRUD de animais (P3)."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Animal, Especie, Raca, Tutor
from app.schemas.animal import AnimalAtualizar, AnimalCriar, AnimalResposta
from app.services.erros import tratar_erro_banco
from app.services.integracao import enviar_em_segundo_plano, registrar_atualizacao_animal

router = APIRouter(prefix="/api/animais", tags=["Animais"])


def _buscar(db: Session, animal_id: int) -> Animal:
    animal = db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Animal não encontrado.")
    return animal


def _conferir_vinculos(db: Session, dados: AnimalCriar) -> None:
    """Tutor ativo, espécie existente e raça da mesma espécie (RN03 e RN04)."""
    tutor = db.get(Tutor, dados.tutor_id)
    if not tutor or tutor.situacao != "ativo":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Tutor não encontrado ou inativo.")
    if not db.get(Especie, dados.especie_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Espécie não encontrada.")
    if dados.raca_id is not None:
        raca = db.get(Raca, dados.raca_id)
        if not raca:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Raça não encontrada.")
        if raca.especie_id != dados.especie_id:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "A raça informada não pertence à espécie do animal.",
            )


@router.post("", response_model=AnimalResposta, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: AnimalCriar, db: Session = Depends(get_db)):
    _conferir_vinculos(db, dados)
    animal = Animal(**dados.model_dump())
    db.add(animal)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(animal)
    return animal


@router.get("", response_model=list[AnimalResposta])
def listar(
    tutor_id: int | None = Query(None, description="Filtrar pelos animais de um tutor"),
    nome: str | None = None,
    incluir_inativos: bool = False,
    db: Session = Depends(get_db),
):
    consulta = select(Animal).order_by(Animal.nome)
    if not incluir_inativos:
        consulta = consulta.where(Animal.situacao == "ativo")
    if tutor_id:
        consulta = consulta.where(Animal.tutor_id == tutor_id)
    if nome:
        consulta = consulta.where(Animal.nome.ilike(f"%{nome}%"))
    return db.scalars(consulta).unique().all()


@router.get("/{animal_id}", response_model=AnimalResposta)
def consultar(animal_id: int, db: Session = Depends(get_db)):
    return _buscar(db, animal_id)


@router.put("/{animal_id}", response_model=AnimalResposta)
def atualizar(animal_id: int, dados: AnimalAtualizar, tarefas: BackgroundTasks, db: Session = Depends(get_db)):
    """Atualiza o animal. Se ele tem microchip, a mudança também é enviada ao governo."""
    animal = _buscar(db, animal_id)
    _conferir_vinculos(db, dados)
    for campo, valor in dados.model_dump().items():
        setattr(animal, campo, valor)
    integracao = None
    try:
        db.flush()
        db.refresh(animal)
        integracao = registrar_atualizacao_animal(db, animal)
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise tratar_erro_banco(erro)
    db.refresh(animal)
    enviar_em_segundo_plano(tarefas, integracao.id if integracao else None)
    return animal


@router.delete("/{animal_id}", response_model=AnimalResposta)
def inativar(animal_id: int, db: Session = Depends(get_db)):
    """Exclusão lógica: o animal fica INATIVO e o histórico é preservado."""
    animal = _buscar(db, animal_id)
    animal.situacao = "inativo"
    db.commit()
    db.refresh(animal)
    return animal
