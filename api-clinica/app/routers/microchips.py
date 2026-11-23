"""Vínculo de microchip do animal (P3 - Milestone 3, RN05 a RN07).

- Um animal tem no máximo 1 microchip ativo.
- O mesmo código nunca pode ser usado de novo (nem no histórico).
- Substituir: o chip antigo vira 'substituido' (histórico preservado) e o novo vira 'ativo'.
- Cada vínculo gera a comunicação de cadastro do animal no governo.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Animal, Veterinario, VinculoMicrochip
from app.schemas.microchip import MicrochipResposta, MicrochipVincular
from app.services.integracao import criar_pendencia, enviar_em_segundo_plano

router = APIRouter(prefix="/api/animais/{animal_id}/microchip", tags=["Microchip"])


def _animal_ativo(db: Session, animal_id: int) -> Animal:
    animal = db.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Animal não encontrado.")
    if animal.situacao != "ativo":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Animal inativo.")
    return animal


def chip_ativo(db: Session, animal_id: int) -> VinculoMicrochip | None:
    return db.scalar(
        select(VinculoMicrochip).where(
            VinculoMicrochip.animal_id == animal_id, VinculoMicrochip.situacao == "ativo"
        )
    )


def _conferir(db: Session, dados: MicrochipVincular) -> None:
    vet = db.get(Veterinario, dados.veterinario_id)
    if not vet or vet.situacao != "ativo":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Veterinário não encontrado ou inativo.")
    usado = db.scalar(
        select(VinculoMicrochip).where(VinculoMicrochip.codigo_microchip == dados.codigo_microchip)
    )
    if usado:
        raise HTTPException(status.HTTP_409_CONFLICT, "Este microchip já foi usado (RN05).")


def _novo_vinculo(db: Session, animal: Animal, dados: MicrochipVincular, tarefas: BackgroundTasks) -> VinculoMicrochip:
    vinculo = VinculoMicrochip(animal_id=animal.id, **dados.model_dump(), situacao="ativo")
    db.add(vinculo)
    try:
        db.flush()
        integracao = criar_pendencia(
            db, animal_id=animal.id, tipo="cadastro_animal", chave=f"CAD-{vinculo.id}"
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Microchip já usado ou animal já tem chip ativo.")
    db.refresh(vinculo)
    enviar_em_segundo_plano(tarefas, integracao.id)
    return vinculo


@router.post("", response_model=MicrochipResposta, status_code=status.HTTP_201_CREATED)
def vincular(animal_id: int, dados: MicrochipVincular, tarefas: BackgroundTasks, db: Session = Depends(get_db)):
    """Vincula o primeiro microchip ao animal e envia o cadastro ao governo."""
    animal = _animal_ativo(db, animal_id)
    if chip_ativo(db, animal_id):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "O animal já tem microchip ativo. Use 'substituir' (RN06).",
        )
    _conferir(db, dados)
    return _novo_vinculo(db, animal, dados, tarefas)


@router.post("/substituir", response_model=MicrochipResposta, status_code=status.HTTP_201_CREATED)
def substituir(animal_id: int, dados: MicrochipVincular, tarefas: BackgroundTasks, db: Session = Depends(get_db)):
    """Troca o microchip: o antigo fica no histórico como 'substituido' (RN07)."""
    animal = _animal_ativo(db, animal_id)
    atual = chip_ativo(db, animal_id)
    if not atual:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "O animal não tem microchip ativo para substituir. Use o vínculo normal.",
        )
    _conferir(db, dados)
    atual.situacao = "substituido"
    db.flush()
    return _novo_vinculo(db, animal, dados, tarefas)


@router.get("", response_model=MicrochipResposta)
def consultar_ativo(animal_id: int, db: Session = Depends(get_db)):
    """Microchip ativo do animal."""
    if not db.get(Animal, animal_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Animal não encontrado.")
    vinculo = chip_ativo(db, animal_id)
    if not vinculo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "O animal não tem microchip ativo.")
    return vinculo


@router.get("/historico", response_model=list[MicrochipResposta])
def historico(animal_id: int, db: Session = Depends(get_db)):
    """Todos os microchips do animal, do mais recente ao mais antigo."""
    if not db.get(Animal, animal_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Animal não encontrado.")
    consulta = (
        select(VinculoMicrochip)
        .where(VinculoMicrochip.animal_id == animal_id)
        .order_by(VinculoMicrochip.data_vinculo.desc(), VinculoMicrochip.id.desc())
    )
    return db.scalars(consulta).unique().all()
