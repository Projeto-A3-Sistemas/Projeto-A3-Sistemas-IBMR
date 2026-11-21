"""Gancho da integração com a API governamental (Milestone 4).

Por enquanto só registra a comunicação como PENDENTE na tabela
integracao_governo. O envio de verdade (HTTP para a API do governo,
tentativas e reenvio) entra na Milestone 4.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IntegracaoGoverno, Vacina


def registrar_envio_antirrabica(db: Session, vacina: Vacina) -> None:
    """Se a vacina é antirrábica e foi aplicada, cria a pendência de envio (uma única vez)."""
    if not (vacina.antirrabica and vacina.situacao == "aplicada"):
        return
    chave = f"VAC-{vacina.id}"
    ja_existe = db.scalar(select(IntegracaoGoverno).where(IntegracaoGoverno.chave_idempotencia == chave))
    if ja_existe:
        return
    db.add(
        IntegracaoGoverno(
            animal_id=vacina.animal_id,
            vacina_id=vacina.id,
            tipo_operacao="vacina_antirrabica",
            chave_idempotencia=chave,
            situacao="pendente",
        )
    )
