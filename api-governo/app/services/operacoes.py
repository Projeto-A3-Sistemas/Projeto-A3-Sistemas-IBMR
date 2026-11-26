"""Regras da API governamental simulada (RF33–RF35, RF37).

Banco igual ao diagrama do Milestone 1 (sem colunas extras). Por isso:
  * a idempotência usa vacinacao_antirrabica.chave_idempotencia (UNIQUE);
  * cada operação guarda no fim da `mensagem` o microchip e a chave da vacinação, no formato
    "<texto>; microchip=<código>; chave=<chave ou ->". É assim que uma repetição
    encontra o protocolo original, e a consulta por protocolo sabe a que animal se refere.

Repetições:
  * mesma chave + mesmo conteúdo     -> devolve o MESMO protocolo (200, reprocessada=true)
  * mesma chave + conteúdo diferente -> 409 CHAVE_IDEMPOTENCIA_REUTILIZADA
  * requisição rejeitada não "gasta" a chave: corrigido o dado, a clínica reenvia com a mesma.
"""
import logging
import re
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AnimalGoverno, Operacao, VacinacaoAntirrabica
from app.schemas import AnimalAtualizar, AnimalCriar, VacinacaoCriar

log = logging.getLogger("governo.operacoes")

CADASTRO = "CADASTRO_ANIMAL"
ATUALIZACAO = "ATUALIZACAO_ANIMAL"
VACINA = "VACINA_ANTIRRABICA"
PROCESSADA = "PROCESSADA"
REJEITADA = "REJEITADA"

CAMPOS_ANIMAL = ("nome", "especie", "raca", "sexo", "data_nascimento", "tutor_nome", "tutor_cpf")


class ErroGoverno(Exception):
    def __init__(self, status: int, codigo: str, mensagem: str, protocolo: str | None = None):
        self.status = status
        self.codigo = codigo
        self.mensagem = mensagem
        self.protocolo = protocolo


# ---------- operações e protocolo ----------

def _mensagem(texto: str, microchip: str, chave: str | None) -> str:
    return f"{texto}; microchip={microchip}; chave={chave or '-'}"


def _registrar(db: Session, tipo: str, situacao: str, texto: str, microchip: str,
               chave: str | None = None) -> Operacao:
    """Cria a operação e gera o protocolo sequencial: GOV-2026-0001, GOV-2026-0002..."""
    op = Operacao(protocolo=f"TMP-{uuid.uuid4().hex}", tipo=tipo, situacao=situacao,
                  mensagem=_mensagem(texto, microchip, chave))
    db.add(op)
    db.flush()
    op.protocolo = f"GOV-{datetime.now().year}-{op.id:04d}"
    return op


def _rejeitar(db: Session, status: int, codigo: str, tipo: str, texto: str, microchip: str) -> ErroGoverno:
    """Grava a operação REJEITADA (com protocolo, sem a chave) e devolve o erro para lançar."""
    db.rollback()
    op = _registrar(db, tipo, REJEITADA, f"{codigo}: {texto}", microchip)
    db.commit()
    log.info("protocolo=%s tipo=%s situacao=REJEITADA codigo=%s microchip=%s", op.protocolo, tipo, codigo, microchip)
    return ErroGoverno(status, codigo, texto, op.protocolo)


def _operacao_por_chave(db: Session, tipo: str, chave: str) -> Operacao | None:
    return db.scalar(select(Operacao).where(
        Operacao.tipo == tipo, Operacao.situacao == PROCESSADA,
        Operacao.mensagem.endswith(f"; chave={chave}", autoescape=True),
    ).order_by(Operacao.id))


def _cadastro_original(db: Session, microchip: str) -> Operacao | None:
    return db.scalar(select(Operacao).where(
        Operacao.tipo == CADASTRO, Operacao.situacao == PROCESSADA,
        Operacao.mensagem.contains(f"; microchip={microchip}; ", autoescape=True),
    ).order_by(Operacao.id))


def _animal(db: Session, microchip: str) -> AnimalGoverno | None:
    return db.scalar(select(AnimalGoverno).where(AnimalGoverno.microchip == microchip.upper()))


def _mesmos_dados(animal: AnimalGoverno, dados) -> bool:
    return all(getattr(animal, c) == getattr(dados, c) for c in CAMPOS_ANIMAL)


def _conflito(protocolo: str | None) -> ErroGoverno:
    return ErroGoverno(409, "CHAVE_IDEMPOTENCIA_REUTILIZADA",
                       "Esta Idempotency-Key já foi usada com outro conteúdo.", protocolo)


# ---------- animais (RF33) ----------

def cadastrar_animal(db: Session, dados: AnimalCriar, _retentativa: bool = False) -> tuple[Operacao, bool]:
    """Retorna (operação, repetida)."""
    existente = _animal(db, dados.microchip)
    if existente:
        if _mesmos_dados(existente, dados):
            original = _cadastro_original(db, dados.microchip)
            if original:
                log.info("protocolo=%s tipo=%s microchip=%s REPETICAO", original.protocolo, CADASTRO, dados.microchip)
                return original, True
        raise _rejeitar(db, 409, "MICROCHIP_JA_CADASTRADO", CADASTRO,
                        "Já existe animal com este microchip. Use PUT para atualizar.", dados.microchip)

    db.add(AnimalGoverno(microchip=dados.microchip, **{c: getattr(dados, c) for c in CAMPOS_ANIMAL}))
    try:
        op = _registrar(db, CADASTRO, PROCESSADA, "Animal registrado", dados.microchip)
        db.commit()
    except IntegrityError:
        # Outra requisição igual gravou primeiro: refaz pelo caminho da repetição.
        db.rollback()
        if _retentativa:
            raise ErroGoverno(409, "CONFLITO_CONCORRENTE", "Conflito de gravação; tente novamente.")
        return cadastrar_animal(db, dados, True)

    db.refresh(op)
    log.info("protocolo=%s tipo=%s microchip=%s situacao=PROCESSADA", op.protocolo, CADASTRO, dados.microchip)
    return op, False


def consultar_animal(db: Session, microchip: str) -> AnimalGoverno:
    animal = _animal(db, microchip)
    if not animal:
        raise ErroGoverno(404, "ANIMAL_NAO_ENCONTRADO", "Nenhum animal registrado com este microchip.")
    return animal


def atualizar_animal(db: Session, microchip: str, dados: AnimalAtualizar) -> Operacao:
    microchip = microchip.strip().upper()
    animal = _animal(db, microchip)
    if not animal:
        raise _rejeitar(db, 404, "ANIMAL_NAO_ENCONTRADO", ATUALIZACAO,
                        "Nenhum animal registrado com este microchip. Cadastre antes de atualizar.", microchip)

    for campo in CAMPOS_ANIMAL:
        setattr(animal, campo, getattr(dados, campo))
    animal.data_atualizacao = datetime.now()
    op = _registrar(db, ATUALIZACAO, PROCESSADA, "Animal atualizado", microchip)
    db.commit()
    db.refresh(op)
    log.info("protocolo=%s tipo=%s microchip=%s situacao=PROCESSADA", op.protocolo, ATUALIZACAO, microchip)
    return op


# ---------- vacinação antirrábica (RF34, RF35) ----------

def _cadastrar_junto(db: Session, dados: VacinacaoCriar) -> AnimalGoverno:
    """Animal ainda não registrado: cadastra com os dados enviados junto com a vacina."""
    animal = AnimalGoverno(microchip=dados.microchip, **{c: getattr(dados.animal, c) for c in CAMPOS_ANIMAL})
    db.add(animal)
    db.flush()
    op = _registrar(db, CADASTRO, PROCESSADA, "Animal registrado junto com a vacinação", dados.microchip)
    log.info("protocolo=%s tipo=%s microchip=%s situacao=PROCESSADA (junto com vacina)",
             op.protocolo, CADASTRO, dados.microchip)
    return animal


def _mesma_vacinacao(vac: VacinacaoAntirrabica, animal_id: int, dados: VacinacaoCriar) -> bool:
    return (vac.animal_id == animal_id and vac.vacina == dados.vacina and vac.fabricante == dados.fabricante
            and vac.lote == dados.lote and vac.data_aplicacao == dados.data_aplicacao
            and vac.veterinario_nome == dados.veterinario_nome and vac.veterinario_crmv == dados.crmv_completo)


def registrar_vacinacao(db: Session, dados: VacinacaoCriar, chave: str,
                        _retentativa: bool = False) -> tuple[Operacao, bool]:
    animal = _animal(db, dados.microchip)

    ja_recebida = db.scalar(select(VacinacaoAntirrabica).where(VacinacaoAntirrabica.chave_idempotencia == chave))
    if ja_recebida:
        original = _operacao_por_chave(db, VACINA, chave)
        if not animal or not _mesma_vacinacao(ja_recebida, animal.id, dados):
            raise _conflito(original.protocolo if original else None)
        if original:
            log.info("protocolo=%s tipo=%s chave=%s REPETICAO", original.protocolo, VACINA, chave)
            return original, True

    if not animal and not dados.animal:
        raise _rejeitar(db, 422, "ANIMAL_NAO_CADASTRADO", VACINA,
                        "Animal não registrado no governo. Envie os dados do animal no campo 'animal'.",
                        dados.microchip)
    nascimento = animal.data_nascimento if animal else dados.animal.data_nascimento
    if nascimento and dados.data_aplicacao < nascimento:
        raise _rejeitar(db, 422, "DATA_APLICACAO_INVALIDA", VACINA,
                        "A data de aplicação é anterior ao nascimento do animal.", dados.microchip)

    try:
        if not animal:
            animal = _cadastrar_junto(db, dados)
        db.add(VacinacaoAntirrabica(
            animal_id=animal.id, vacina=dados.vacina, fabricante=dados.fabricante, lote=dados.lote,
            data_aplicacao=dados.data_aplicacao, veterinario_nome=dados.veterinario_nome,
            veterinario_crmv=dados.crmv_completo, chave_idempotencia=chave,
        ))
        op = _registrar(db, VACINA, PROCESSADA, "Vacinação antirrábica registrada", dados.microchip, chave)
        db.commit()
    except IntegrityError:
        db.rollback()
        if _retentativa:
            raise ErroGoverno(409, "CONFLITO_CONCORRENTE", "Conflito de gravação; tente novamente.")
        return registrar_vacinacao(db, dados, chave, True)

    db.refresh(op)
    log.info("protocolo=%s tipo=%s microchip=%s chave=%s situacao=PROCESSADA",
             op.protocolo, VACINA, dados.microchip, chave)
    return op, False


# ---------- consulta por protocolo (RF37) ----------

def consultar_operacao(db: Session, protocolo: str) -> dict:
    op = db.scalar(select(Operacao).where(Operacao.protocolo == protocolo.strip().upper()))
    if not op:
        raise ErroGoverno(404, "PROTOCOLO_NAO_ENCONTRADO", "Protocolo inexistente.")
    achado = re.search(r"; microchip=([^;]+); chave=", op.mensagem or "")
    return {"protocolo": op.protocolo, "tipo": op.tipo, "situacao": op.situacao, "data": op.data,
            "mensagem": op.mensagem, "microchip": achado.group(1) if achado else None}
