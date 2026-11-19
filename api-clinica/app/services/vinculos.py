"""Conferências usadas por consultas e vacinas."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Animal, Veterinario


def conferir_animal_e_veterinario(db: Session, animal_id: int, veterinario_id: int) -> None:
    animal = db.get(Animal, animal_id)
    if not animal or animal.situacao != "ativo":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Animal não encontrado ou inativo.")
    vet = db.get(Veterinario, veterinario_id)
    if not vet or vet.situacao != "ativo":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Veterinário não encontrado ou inativo.")
