from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.animal import Referencia

SituacaoIntegracao = Literal["pendente", "enviada", "confirmada", "falha"]
TipoOperacao = Literal["cadastro_animal", "atualizacao_animal", "vacina_antirrabica"]


class IntegracaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal: Referencia
    vacina_id: int | None
    tipo_operacao: TipoOperacao
    situacao: SituacaoIntegracao
    protocolo_externo: str | None
    chave_idempotencia: str
    tentativas: int
    mensagem_erro: str | None
    data_solicitacao: datetime
    data_resposta: datetime | None


class ResumoIntegracoes(BaseModel):
    pendente: int = 0
    enviada: int = 0
    confirmada: int = 0
    falha: int = 0
    total: int = 0


class ResultadoProcessamento(BaseModel):
    processadas: int
    confirmadas: int
    falhas: int
    continuam_pendentes: int
