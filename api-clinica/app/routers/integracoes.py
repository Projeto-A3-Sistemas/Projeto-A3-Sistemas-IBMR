"""Status das comunicações com o governo (P3 - Milestone 4).

Usado pela tela de integrações do frontend (P5): listar, ver protocolo,
ver pendências e reenviar.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import IntegracaoGoverno
from app.schemas.integracao import (
    IntegracaoResposta, ResultadoProcessamento, ResumoIntegracoes, SituacaoIntegracao, TipoOperacao,
)
from app.services.integracao import enviar, processar_pendentes

router = APIRouter(prefix="/api/integracoes", tags=["Integração com o governo"])


def _buscar(db: Session, integracao_id: int) -> IntegracaoGoverno:
    integracao = db.get(IntegracaoGoverno, integracao_id)
    if not integracao:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comunicação não encontrada.")
    return integracao


@router.get("", response_model=list[IntegracaoResposta])
def listar(
    situacao: SituacaoIntegracao | None = Query(None, description="pendente, enviada, confirmada ou falha"),
    tipo_operacao: TipoOperacao | None = None,
    animal_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Lista as comunicações com o governo, da mais recente para a mais antiga."""
    consulta = select(IntegracaoGoverno).order_by(IntegracaoGoverno.id.desc())
    if situacao:
        consulta = consulta.where(IntegracaoGoverno.situacao == situacao)
    if tipo_operacao:
        consulta = consulta.where(IntegracaoGoverno.tipo_operacao == tipo_operacao)
    if animal_id:
        consulta = consulta.where(IntegracaoGoverno.animal_id == animal_id)
    return db.scalars(consulta).unique().all()


@router.get("/resumo", response_model=ResumoIntegracoes)
def resumo(db: Session = Depends(get_db)):
    """Quantas comunicações há em cada situação (para o painel)."""
    linhas = db.execute(
        select(IntegracaoGoverno.situacao, func.count()).group_by(IntegracaoGoverno.situacao)
    ).all()
    contagem = {situacao: total for situacao, total in linhas}
    return ResumoIntegracoes(**contagem, total=sum(contagem.values()))


@router.post("/processar-pendentes", response_model=ResultadoProcessamento)
def processar(db: Session = Depends(get_db)):
    """Reenvia agora todas as pendentes (o mesmo que o reenvio automático faz)."""
    return processar_pendentes(db)


@router.get("/{integracao_id}", response_model=IntegracaoResposta)
def consultar(integracao_id: int, db: Session = Depends(get_db)):
    return _buscar(db, integracao_id)


@router.post("/{integracao_id}/reenviar", response_model=IntegracaoResposta)
def reenviar(integracao_id: int, db: Session = Depends(get_db)):
    """Reenvia uma comunicação pendente ou com falha, usando a MESMA chave (não duplica)."""
    integracao = _buscar(db, integracao_id)
    if integracao.situacao == "confirmada":
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta comunicação já foi confirmada pelo governo.")
    enviar(db, integracao)
    db.refresh(integracao)
    return integracao
